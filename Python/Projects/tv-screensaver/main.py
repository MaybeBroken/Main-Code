IMG_PATH = "./img.png"

import sys
import math
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCursor, QFont, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtOpenGL import (
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLTexture,
    QOpenGLBuffer,
    QOpenGLVertexArrayObject,
)


# -------------------------
# Settings and Dialog
# -------------------------

THEMES = [
    "None",
    "Scanlines",
    "Vignette",
    "Neon Glow",
    "Chromatic",
    "Posterize",
    "CRT Curve",
]


@dataclass
class StartSettings:
    speed_px_s: float = 180.0
    logo_scale: float = 0.20  # fraction of min(width, height)
    fps: int = 60
    theme_index: int = 1
    show_overlay: bool = True
    stage_corner_on_start: bool = False
    stage_time_s: float = 8.0
    project_time_s: float = 10.0


class StartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TV Screensaver — Startup")
        self.setModal(True)

        tabs = QTabWidget(self)

        # Timing Tab
        timing = QWidget(self)
        form = QFormLayout(timing)

        self.speed = QDoubleSpinBox(self)
        self.speed.setRange(10.0, 2000.0)
        self.speed.setValue(180.0)
        self.speed.setSuffix(" px/s")
        self.speed.setDecimals(1)

        self.logo_size = QDoubleSpinBox(self)
        self.logo_size.setRange(0.05, 0.90)
        self.logo_size.setSingleStep(0.05)
        self.logo_size.setValue(0.20)
        self.logo_size.setSuffix(" of min dim")

        self.fps = QSpinBox(self)
        self.fps.setRange(24, 240)
        self.fps.setValue(60)

        self.theme = QComboBox(self)
        self.theme.addItems(THEMES)
        self.theme.setCurrentIndex(1)

        self.stage_time = QDoubleSpinBox(self)
        self.stage_time.setRange(0.5, 600.0)
        self.stage_time.setSingleStep(0.5)
        self.stage_time.setValue(8.0)
        self.stage_time.setSuffix(" s to staged hit")

        self.proj_time = QDoubleSpinBox(self)
        self.proj_time.setRange(1.0, 600.0)
        self.proj_time.setSingleStep(1.0)
        self.proj_time.setValue(10.0)
        self.proj_time.setSuffix(" s path projection")

        form.addRow("Speed:", self.speed)
        form.addRow("Logo size:", self.logo_size)
        form.addRow("FPS:", self.fps)
        form.addRow("Theme:", self.theme)
        form.addRow("Stage time:", self.stage_time)
        form.addRow("Project path:", self.proj_time)

        tabs.addTab(timing, "Timing")

        # Controls Tab
        controls = QWidget(self)
        vbox = QVBoxLayout(controls)
        lbl = QLabel(
            "Keybinds:\n"
            "  Space: Pause/Resume\n"
            "  +/-: Speed down/up\n"
            "  T: Next theme\n"
            "  C: Toggle corner overlay\n"
            "  H: Stage next corner hit\n"
            "  R: Reset position\n"
            "  F: Toggle fullscreen\n"
            "  ?: Toggle help overlay\n"
            "  Esc: Quit",
            self,
        )
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        vbox.addWidget(lbl)
        vbox.addStretch(1)
        tabs.addTab(controls, "Controls")

        # Corner Hit Tab
        corner = QWidget(self)
        cform = QFormLayout(corner)
        self.show_overlay_cb = QCheckBox("Show projected corner hit overlay", self)
        self.show_overlay_cb.setChecked(True)
        self.stage_on_start_cb = QCheckBox("Stage a corner hit on start", self)
        self.stage_on_start_cb.setChecked(False)
        cform.addRow(self.show_overlay_cb)
        cform.addRow(self.stage_on_start_cb)
        tabs.addTab(corner, "Corner Hit")

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(buttons)

    def result_settings(self) -> StartSettings:
        return StartSettings(
            speed_px_s=float(self.speed.value()),
            logo_scale=float(self.logo_size.value()),
            fps=int(self.fps.value()),
            theme_index=int(self.theme.currentIndex()),
            show_overlay=bool(self.show_overlay_cb.isChecked()),
            stage_corner_on_start=bool(self.stage_on_start_cb.isChecked()),
            stage_time_s=float(self.stage_time.value()),
            project_time_s=float(self.proj_time.value()),
        )


# -------------------------
# OpenGL Bouncing Widget
# -------------------------


class GLBouncer(QOpenGLWidget):
    frameRendered = QtCore.Signal()

    def __init__(self, img: QImage, settings: StartSettings, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self._settings = settings
        self._paused = False
        self._show_help = False
        self._show_overlay = settings.show_overlay
        self._theme = settings.theme_index
        self._fps = settings.fps
        self._bg_color = QtGui.QColor(10, 10, 12)

        # movement state
        self._pos = QtCore.QPointF(100.0, 100.0)
        self._vel = QtCore.QPointF(1.0, 0.8)  # will be normalized and scaled to speed
        self._speed = settings.speed_px_s
        # logo geometry (preserve aspect)
        self._logo_w_px = 100
        self._logo_h_px = 100

        # image/texture
        self._img = img.convertToFormat(QImage.Format_RGBA8888)
        self._tex = None  # QOpenGLTexture

        # GL program
        self._program = None
        self._vao = None
        self._vbo = None

        # timing
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(int(1000 / max(1, self._fps)))
        self._elapsed = QtCore.QElapsedTimer()
        self._elapsed.start()
        self._last_ms = self._elapsed.elapsed()

        # staging/projection times
        self._stage_time = settings.stage_time_s
        self._proj_time = settings.project_time_s

    # ------------- GL lifecycle -------------
    def initializeGL(self):
        # Texture
        self._tex = QOpenGLTexture(QOpenGLTexture.Target2D)
        self._tex.setFormat(QOpenGLTexture.RGBA8_UNorm)
        self._tex.create()
        self._tex.bind()
        self._tex.setWrapMode(QOpenGLTexture.ClampToEdge)
        self._tex.setMinificationFilter(QOpenGLTexture.Linear)
        self._tex.setMagnificationFilter(QOpenGLTexture.Linear)
        self._tex.setData(self._img)
        self._tex.release()

        # Program
        self._program = self._build_program()
        if not self._program:
            raise RuntimeError("Failed to compile shaders")

        # fullscreen triangle (NDC)
        verts = (
            -1.0,
            -1.0,
            0.0,
            3.0,
            -1.0,
            0.0,
            -1.0,
            3.0,
            0.0,
        )
        import struct

        ba = bytearray()
        for f in verts:
            ba += struct.pack("f", f)
        data = bytes(ba)

        self._vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self._vbo.create()
        self._vbo.bind()
        self._vbo.allocate(data, len(data))
        self._vbo.release()

    def _build_program(self) -> QOpenGLShaderProgram | None:
        # Prepare shader pairs for 330 core, 300 es, and 100 es
        shaders = []

        vert_330 = """
        #version 330 core
        in vec3 aPos;
        out vec2 vUV;
        void main(){
            vUV = 0.5 * (aPos.xy + vec2(1.0));
            gl_Position = vec4(aPos, 1.0);
        }
        """
        frag_330 = """
        #version 330 core
        in vec2 vUV;
        out vec4 FragColor;
        uniform sampler2D u_tex;
        uniform vec2 u_resolution; // pixels
        uniform vec4 u_logoRect;   // x,y,w,h in pixels
        uniform float u_time;      // seconds
        uniform int u_mode;        // theme
        uniform vec2 u_texSize;    // logo texture size in px
        float luma(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
        vec2 barrel(vec2 uv, float amt){ vec2 cc = uv * 2.0 - 1.0; float r2 = dot(cc, cc); cc *= 1.0 + amt * r2; return (cc * 0.5) + 0.5; }
        vec3 posterize(vec3 c, float steps){ return floor(c * steps) / steps; }
        void main(){
            vec2 fragPx = vUV * u_resolution;
            vec2 lmin = u_logoRect.xy; vec2 lmax = u_logoRect.xy + u_logoRect.zw;
            vec4 base = vec4(0.04, 0.04, 0.05, 1.0); vec4 col = base;
            if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){
                vec2 tuv = clamp((fragPx - lmin) / u_logoRect.zw, 0.001, 0.999);
                tuv.y = 1.0 - tuv.y;
                vec3 c = texture(u_tex, tuv).rgb; col = vec4(c, 1.0);
            }
            if(u_mode == 1){ float scan = 0.07 * sin(3.14159 * fragPx.y); col.rgb *= 1.0 - scan; }
            else if(u_mode == 2){ vec2 uv = vUV - 0.5; float r = dot(uv, uv); col.rgb *= smoothstep(0.75, 0.2, r); }
            else if(u_mode == 3){ if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = (fragPx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; vec2 o = 1.0/ u_texSize; float gx = -luma(texture(u_tex, tuv+vec2(-o.x,-o.y)).rgb) - 2.0*luma(texture(u_tex, tuv+vec2(-o.x,0.0)).rgb) - luma(texture(u_tex, tuv+vec2(-o.x,o.y)).rgb) + luma(texture(u_tex, tuv+vec2(o.x,-o.y)).rgb) + 2.0*luma(texture(u_tex, tuv+vec2(o.x,0.0)).rgb) + luma(texture(u_tex, tuv+vec2(o.x,o.y)).rgb); float gy = -luma(texture(u_tex, tuv+vec2(-o.x,-o.y)).rgb) - 2.0*luma(texture(u_tex, tuv+vec2(0.0,-o.y)).rgb) - luma(texture(u_tex, tuv+vec2(o.x,-o.y)).rgb) + luma(texture(u_tex, tuv+vec2(-o.x,o.y)).rgb) + 2.0*luma(texture(u_tex, tuv+vec2(0.0,o.y)).rgb) + luma(texture(u_tex, tuv+vec2(o.x,o.y)).rgb); float edge = clamp(sqrt(gx*gx+gy*gy),0.0,1.0); col.rgb += 0.8*vec3(edge,0.3*edge,edge);} }
            else if(u_mode == 4){ vec2 shift = 0.002 * (vUV - 0.5); vec3 c2 = col.rgb; if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = (fragPx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; vec3 crgb; crgb.r = texture(u_tex, clamp(tuv + shift, 0.001, 0.999)).r; crgb.g = texture(u_tex, tuv).g; crgb.b = texture(u_tex, clamp(tuv - shift, 0.001, 0.999)).b; c2 = crgb; } col.rgb = c2; }
            else if(u_mode == 5){ col.rgb = posterize(col.rgb, 5.0); }
            else if(u_mode == 6){ vec2 uv = barrel(vUV, 0.12); vec2 fpx = uv * u_resolution; vec4 c3 = base; if(all(greaterThanEqual(fpx, lmin)) && all(lessThan(fpx, lmax))){ vec2 tuv = (fpx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; c3 = vec4(texture(u_tex, clamp(tuv, 0.001, 0.999)).rgb, 1.0);} float scan = 0.08 * sin(3.14159 * fpx.y); c3.rgb *= 1.0 - scan; col = c3; }
            FragColor = col;
        }
        """

        vert_300es = """
        #version 300 es
        precision highp float; precision highp int;
        in vec3 aPos; out vec2 vUV;
        void main(){ vUV = 0.5 * (aPos.xy + vec2(1.0)); gl_Position = vec4(aPos, 1.0); }
        """
        frag_300es = """
        #version 300 es
        precision highp float; precision highp int;
        in vec2 vUV; out vec4 FragColor;
        uniform sampler2D u_tex; uniform vec2 u_resolution; uniform vec4 u_logoRect; uniform float u_time; uniform int u_mode; uniform vec2 u_texSize;
        float luma(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
        vec2 barrel(vec2 uv, float amt){ vec2 cc = uv * 2.0 - 1.0; float r2 = dot(cc, cc); cc *= 1.0 + amt * r2; return (cc * 0.5) + 0.5; }
        vec3 posterize(vec3 c, float steps){ return floor(c * steps) / steps; }
        void main(){
            vec2 fragPx = vUV * u_resolution;
            vec2 lmin = u_logoRect.xy; vec2 lmax = u_logoRect.xy + u_logoRect.zw;
            vec4 base = vec4(0.04, 0.04, 0.05, 1.0); vec4 col = base;
            if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = clamp((fragPx - lmin) / u_logoRect.zw, 0.001, 0.999); tuv.y = 1.0 - tuv.y; vec3 c = texture(u_tex, tuv).rgb; col = vec4(c, 1.0); }
            if(u_mode == 1){ float scan = 0.07 * sin(3.14159 * fragPx.y); col.rgb *= 1.0 - scan; }
            else if(u_mode == 2){ vec2 uv = vUV - 0.5; float r = dot(uv, uv); col.rgb *= smoothstep(0.75, 0.2, r); }
            else if(u_mode == 3){ if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = (fragPx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; vec2 o = 1.0/ u_texSize; float gx = -luma(texture(u_tex, tuv+vec2(-o.x,-o.y)).rgb) - 2.0*luma(texture(u_tex, tuv+vec2(-o.x,0.0)).rgb) - luma(texture(u_tex, tuv+vec2(-o.x,o.y)).rgb) + luma(texture(u_tex, tuv+vec2(o.x,-o.y)).rgb) + 2.0*luma(texture(u_tex, tuv+vec2(o.x,0.0)).rgb) + luma(texture(u_tex, tuv+vec2(o.x,o.y)).rgb); float gy = -luma(texture(u_tex, tuv+vec2(-o.x,-o.y)).rgb) - 2.0*luma(texture(u_tex, tuv+vec2(0.0,-o.y)).rgb) - luma(texture(u_tex, tuv+vec2(o.x,-o.y)).rgb) + luma(texture(u_tex, tuv+vec2(-o.x,o.y)).rgb) + 2.0*luma(texture(u_tex, tuv+vec2(0.0,o.y)).rgb) + luma(texture(u_tex, tuv+vec2(o.x,o.y)).rgb); float edge = clamp(sqrt(gx*gx+gy*gy),0.0,1.0); col.rgb += 0.8*vec3(edge,0.3*edge,edge);} }
            else if(u_mode == 4){ vec2 shift = 0.002 * (vUV - 0.5); vec3 c2 = col.rgb; if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = (fragPx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; vec3 crgb; crgb.r = texture(u_tex, clamp(tuv + shift, 0.001, 0.999)).r; crgb.g = texture(u_tex, tuv).g; crgb.b = texture(u_tex, clamp(tuv - shift, 0.001, 0.999)).b; c2 = crgb; } col.rgb = c2; }
            else if(u_mode == 5){ col.rgb = posterize(col.rgb, 5.0); }
            else if(u_mode == 6){ vec2 uv = barrel(vUV, 0.12); vec2 fpx = uv * u_resolution; vec4 c3 = base; if(all(greaterThanEqual(fpx, lmin)) && all(lessThan(fpx, lmax))){ vec2 tuv = (fpx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; c3 = vec4(texture(u_tex, clamp(tuv, 0.001, 0.999)).rgb, 1.0);} float scan = 0.08 * sin(3.14159 * fpx.y); c3.rgb *= 1.0 - scan; col = c3; }
            FragColor = col;
        }
        """

        vert_es2 = """
        #version 100
        precision highp float; precision highp int;
        attribute vec3 aPos; varying vec2 vUV;
        void main(){ vUV = 0.5 * (aPos.xy + vec2(1.0)); gl_Position = vec4(aPos, 1.0); }
        """
        frag_es2 = """
        #version 100
        precision highp float; precision highp int;
        varying vec2 vUV; uniform sampler2D u_tex; uniform vec2 u_resolution; uniform vec4 u_logoRect; uniform float u_time; uniform int u_mode; uniform vec2 u_texSize;
        float luma(vec3 c){ return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
        vec2 barrel(vec2 uv, float amt){ vec2 cc = uv * 2.0 - 1.0; float r2 = dot(cc, cc); cc *= 1.0 + amt * r2; return (cc * 0.5) + 0.5; }
        vec3 posterize(vec3 c, float steps){ return floor(c * steps) / steps; }
        void main(){
            vec2 fragPx = vUV * u_resolution;
            vec2 lmin = u_logoRect.xy; vec2 lmax = u_logoRect.xy + u_logoRect.zw;
            vec4 base = vec4(0.04, 0.04, 0.05, 1.0); vec4 col = base;
            if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = clamp((fragPx - lmin) / u_logoRect.zw, 0.001, 0.999); tuv.y = 1.0 - tuv.y; vec3 c = texture2D(u_tex, tuv).rgb; col = vec4(c, 1.0); }
            if(u_mode == 1){ float scan = 0.07 * sin(3.14159 * fragPx.y); col.rgb *= 1.0 - scan; }
            else if(u_mode == 2){ vec2 uv = vUV - 0.5; float r = dot(uv, uv); col.rgb *= smoothstep(0.75, 0.2, r); }
            else if(u_mode == 3){ if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = (fragPx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; vec2 o = 1.0/ u_texSize; float gx = -luma(texture2D(u_tex, tuv+vec2(-o.x,-o.y)).rgb) - 2.0*luma(texture2D(u_tex, tuv+vec2(-o.x,0.0)).rgb) - luma(texture2D(u_tex, tuv+vec2(-o.x,o.y)).rgb) + luma(texture2D(u_tex, tuv+vec2(o.x,-o.y)).rgb) + 2.0*luma(texture2D(u_tex, tuv+vec2(o.x,0.0)).rgb) + luma(texture2D(u_tex, tuv+vec2(o.x,o.y)).rgb); float gy = -luma(texture2D(u_tex, tuv+vec2(-o.x,-o.y)).rgb) - 2.0*luma(texture2D(u_tex, tuv+vec2(0.0,-o.y)).rgb) - luma(texture2D(u_tex, tuv+vec2(o.x,-o.y)).rgb) + luma(texture2D(u_tex, tuv+vec2(-o.x,o.y)).rgb) + 2.0*luma(texture2D(u_tex, tuv+vec2(0.0,o.y)).rgb) + luma(texture2D(u_tex, tuv+vec2(o.x,o.y)).rgb); float edge = clamp(sqrt(gx*gx+gy*gy),0.0,1.0); col.rgb += 0.8*vec3(edge,0.3*edge,edge);} }
            else if(u_mode == 4){ vec2 shift = 0.002 * (vUV - 0.5); vec3 c2 = col.rgb; if(all(greaterThanEqual(fragPx, lmin)) && all(lessThan(fragPx, lmax))){ vec2 tuv = (fragPx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; vec3 crgb; crgb.r = texture2D(u_tex, clamp(tuv + shift, 0.001, 0.999)).r; crgb.g = texture2D(u_tex, tuv).g; crgb.b = texture2D(u_tex, clamp(tuv - shift, 0.001, 0.999)).b; c2 = crgb; } col.rgb = c2; }
            else if(u_mode == 5){ col.rgb = posterize(col.rgb, 5.0); }
            else if(u_mode == 6){ vec2 uv = barrel(vUV, 0.12); vec2 fpx = uv * u_resolution; vec4 c3 = base; if(all(greaterThanEqual(fpx, lmin)) && all(lessThan(fpx, lmax))){ vec2 tuv = (fpx - lmin) / u_logoRect.zw; tuv.y = 1.0 - tuv.y; c3 = vec4(texture2D(u_tex, clamp(tuv, 0.001, 0.999)).rgb, 1.0);} float scan = 0.08 * sin(3.14159 * fpx.y); c3.rgb *= 1.0 - scan; col = c3; }
            gl_FragColor = col;
        }
        """

        shaders.append((vert_330, frag_330))
        shaders.append((vert_300es, frag_300es))
        shaders.append((vert_es2, frag_es2))

        for vsrc, fsrc in shaders:
            prog = QOpenGLShaderProgram(self.context())
            vs = QOpenGLShader(QOpenGLShader.Vertex, self.context())
            fs = QOpenGLShader(QOpenGLShader.Fragment, self.context())
            if not vs.compileSourceCode(vsrc):
                continue
            if not fs.compileSourceCode(fsrc):
                continue
            prog.addShader(vs)
            prog.addShader(fs)
            prog.bindAttributeLocation("aPos", 0)
            if not prog.link():
                continue
            return prog
        return None

    def resizeGL(self, w: int, h: int):
        # Recompute logo size based on settings; preserve texture aspect ratio
        m = min(max(1, w), max(1, h))
        short_side = max(8, int(self._settings.logo_scale * m))
        aspect = max(1e-6, float(self._img.width()) / float(self._img.height()))
        if aspect >= 1.0:
            self._logo_h_px = short_side
            self._logo_w_px = int(short_side * aspect)
        else:
            self._logo_w_px = short_side
            self._logo_h_px = int(short_side / aspect)
        self._logo_w_px = min(self._logo_w_px, max(1, w))
        self._logo_h_px = min(self._logo_h_px, max(1, h))
        # Normalize velocity and scale to speed
        mag = math.hypot(self._vel.x(), self._vel.y()) or 1.0
        self._vel = QtCore.QPointF(self._vel.x() / mag, self._vel.y() / mag)
        self._vel = QtCore.QPointF(
            self._vel.x() * self._speed, self._vel.y() * self._speed
        )

        # Keep inside bounds
        bx, by = self._bounds()
        self._pos.setX(min(max(0.0, self._pos.x()), bx))
        self._pos.setY(min(max(0.0, self._pos.y()), by))

        # Optionally stage corner on start
        if self._settings.stage_corner_on_start:
            self._stage_corner_next()

    def paintGL(self):
        w = max(1, self.width())
        h = max(1, self.height())

        # Use shader to draw fullscreen + logo
        self._program.bind()
        # Set uniforms
        self._program.setUniformValue(
            "u_resolution", QtGui.QVector2D(float(w), float(h))
        )
        self._program.setUniformValue(
            "u_logoRect",
            QtGui.QVector4D(
                float(self._pos.x()),
                float(self._pos.y()),
                float(self._logo_w_px),
                float(self._logo_h_px),
            ),
        )
        # PySide6 requires using uniform locations for float/int when setting by value
        loc_time = self._program.uniformLocation("u_time")
        self._program.setUniformValue(loc_time, float(self._elapsed.elapsed() / 1000.0))
        loc_mode = self._program.uniformLocation("u_mode")
        self._program.setUniformValue(loc_mode, int(self._theme))
        self._program.setUniformValue(
            "u_texSize",
            QtGui.QVector2D(float(self._img.width()), float(self._img.height())),
        )

        # Texture unit 0 (default)
        self._tex.bind()
        loc_tex = self._program.uniformLocation("u_tex")
        self._program.setUniformValue(loc_tex, 0)

        # Draw full-screen triangle using VBO (bind attributes per frame)
        self._vbo.bind()
        self._program.enableAttributeArray(0)
        # attribute 0, GL_FLOAT(0x1406), offset 0, tuple size 3, stride 0
        self._program.setAttributeBuffer(0, 0x1406, 0, 3, 0)
        funcs = self.context().functions()
        funcs.glDrawArrays(0x0004, 0, 3)  # GL_TRIANGLES
        self._program.disableAttributeArray(0)
        self._vbo.release()
        self._tex.release()
        self._program.release()

        # Overlays using QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self._show_overlay:
            self._draw_overlay(painter)
        if self._show_help:
            self._draw_help(painter)
        painter.end()

        self.frameRendered.emit()

    # ------------- Movement and helpers -------------
    def _bounds(self):
        return max(0, self.width() - self._logo_w_px), max(
            0, self.height() - self._logo_h_px
        )

    def _tick(self):
        if self._paused:
            self.update()
            return
        now = self._elapsed.elapsed()
        dt = max(0.0, (now - self._last_ms) / 1000.0)
        self._last_ms = now
        self._advance(dt)
        self.update()

    def _advance(self, dt: float):
        if dt <= 0.0:
            return
        x, y = self._pos.x(), self._pos.y()
        vx, vy = self._vel.x(), self._vel.y()
        maxx, maxy = self._bounds()

        x += vx * dt
        y += vy * dt

        bounced = False
        if x < 0.0:
            x = -x
            vx = abs(vx)
            bounced = True
        elif x > maxx:
            x = 2 * maxx - x
            vx = -abs(vx)
            bounced = True
        if y < 0.0:
            y = -y
            vy = abs(vy)
            bounced = True
        elif y > maxy:
            y = 2 * maxy - y
            vy = -abs(vy)
            bounced = True

        self._pos = QtCore.QPointF(x, y)
        self._vel = QtCore.QPointF(vx, vy)

        # Keep magnitude equal to speed (avoid drift)
        mag = math.hypot(vx, vy) or 1.0
        scale = self._speed / mag
        self._vel = QtCore.QPointF(vx * scale, vy * scale)

    # ------------- Overlays -------------
    def _draw_overlay(self, p: QPainter):
        w, h = self.width(), self.height()
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 90), 1))
        # Draw border
        p.drawRect(0, 0, w - 1, h - 1)

        # Draw projected path
        pts = self._project_path(self._proj_time, max_segments=240)
        if len(pts) > 1:
            pen = QtGui.QPen(QtGui.QColor(0, 200, 255, 120), 1.5)
            p.setPen(pen)
            for i in range(1, len(pts)):
                p.drawLine(
                    int(pts[i - 1].x()),
                    int(pts[i - 1].y()),
                    int(pts[i].x()),
                    int(pts[i].y()),
                )
        # Project next corner hit
        t_corner, which = self._time_to_next_corner()
        if t_corner is not None:
            txt = f"Next corner in {t_corner:.2f}s → {which} (H to stage)"
        else:
            txt = "No corner alignment soon (H to stage)"
        p.setFont(QFont("Consolas", 10))
        p.setPen(QtGui.QColor(240, 240, 240, 200))
        p.drawText(10, 20, txt)

        # Draw logo rect
        p.setPen(QtGui.QPen(QtGui.QColor(0, 255, 180, 180), 1))
        p.drawRect(
            int(self._pos.x()),
            int(self._pos.y()),
            int(self._logo_w_px),
            int(self._logo_h_px),
        )

        # Mark corners
        corners = {
            "TL": QtCore.QPointF(0, 0),
            "TR": QtCore.QPointF(w - 1, 0),
            "BL": QtCore.QPointF(0, h - 1),
            "BR": QtCore.QPointF(w - 1, h - 1),
        }
        # Draw all corners
        for name, pt in corners.items():
            p.setBrush(QtGui.QColor(255, 255, 255, 60))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QtCore.QPointF(pt.x(), pt.y()), 4, 4)
            p.setPen(QtGui.QColor(255, 255, 255, 160))
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawText(
                int(pt.x()) + (5 if "L" in name else -35),
                int(pt.y()) + (15 if "T" in name else -5),
                name,
            )

        # Highlight the next-hit corner if known
        if which in corners:
            pt = corners[which]
            p.setPen(Qt.NoPen)
            p.setBrush(QtGui.QColor(0, 255, 180, 180))
            p.drawEllipse(QtCore.QPointF(pt.x(), pt.y()), 8, 8)

    def _draw_help(self, p: QPainter):
        lines = [
            "Space: Pause/Resume",
            "+/-: Speed up/down",
            "T: Next theme",
            "C: Toggle corner overlay",
            "H: Stage next corner hit",
            "R: Reset position",
            "F: Toggle fullscreen",
            "?: Toggle help",
            "Esc: Quit",
        ]
        bg = QtGui.QColor(0, 0, 0, 180)
        fg = QtGui.QColor(240, 240, 240)
        margin = 12
        w = 300
        h = 20 * (len(lines) + 1)
        rect = QtCore.QRect(10, 40, w, h)
        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawRoundedRect(rect, 8, 8)
        p.setPen(fg)
        p.setFont(QFont("Consolas", 10))
        y = rect.top() + 24
        p.drawText(rect.left() + margin, y - 10, "Help")
        for ln in lines:
            p.drawText(rect.left() + margin, y, ln)
            y += 18

    def _project_path(self, duration_s: float, max_segments: int = 180):
        # Simulate future path of the top-left point for a fixed time
        if duration_s <= 0:
            return []
        pts = []
        x, y = float(self._pos.x()), float(self._pos.y())
        vx, vy = float(self._vel.x()), float(self._vel.y())
        maxx, maxy = self._bounds()
        # Use uniform time steps, capped to max_segments
        steps = max(2, min(max_segments, int(self._fps * duration_s)))
        dt = duration_s / steps
        pts.append(QtCore.QPointF(x, y))
        for _ in range(steps):
            x += vx * dt
            y += vy * dt
            if x < 0.0:
                x = -x
                vx = abs(vx)
            elif x > maxx:
                x = 2 * maxx - x
                vx = -abs(vx)
            if y < 0.0:
                y = -y
                vy = abs(vy)
            elif y > maxy:
                y = 2 * maxy - y
                vy = -abs(vy)
            pts.append(QtCore.QPointF(x, y))
        return pts

    # ------------- Corner utilities -------------
    def _time_to_walls(self):
        x, y = self._pos.x(), self._pos.y()
        vx, vy = self._vel.x(), self._vel.y()
        maxx, maxy = self._bounds()
        # Distance to next wall along each axis
        dx = (maxx - x) if vx > 0 else x
        dy = (maxy - y) if vy > 0 else y
        tx = dx / abs(vx) if vx != 0 else math.inf
        ty = dy / abs(vy) if vy != 0 else math.inf
        return tx, ty, ("R" if vx > 0 else "L"), ("B" if vy > 0 else "T")

    def _time_to_next_corner(self, max_mult: int = 200, eps: float = 1e-3):
        tx, ty, sx, sy = self._time_to_walls()
        if math.isinf(tx) or math.isinf(ty):
            return None, None
        # Periods for reflections
        maxx, maxy = self._bounds()
        Tx = (2.0 * max(1e-6, maxx)) / (abs(self._vel.x()) or 1e-6)
        Ty = (2.0 * max(1e-6, maxy)) / (abs(self._vel.y()) or 1e-6)
        # Scan multiples of Tx from tx, find close to ty mod Ty
        best = None
        for k in range(0, max_mult):
            t = tx + k * Tx
            m = (t - ty) % Ty
            d = min(m, Ty - m)
            if d < eps:
                best = t
                break
        if best is None:
            return None, None
        corner = ("T" if sy == "T" else "B") + ("R" if sx == "R" else "L")
        # Present as TL/TR/BL/BR order
        if corner == "TR":
            which = "TR"
        elif corner == "TL":
            which = "TL"
        elif corner == "BR":
            which = "BR"
        else:
            which = "BL"
        return best, which

    def _stage_corner_next(self):
        # Choose velocity so that at time self._stage_time the top-left hits a corner exactly.
        T = max(0.1, float(self._stage_time))
        x0, y0 = float(self._pos.x()), float(self._pos.y())
        W, H = self._bounds()
        if W <= 0 or H <= 0:
            return
        # Target lattice points are (n*W, m*H). Pick n,m near the circle radius R = speed*T.
        R = max(1e-6, self._speed * T)
        # Search a window around current tile indices
        nx0 = int(round((x0) / max(1e-6, W)))
        ny0 = int(round((y0) / max(1e-6, H)))
        best = None
        for dn in range(-8, 9):
            for dm in range(-8, 9):
                n = nx0 + dn
                m = ny0 + dm
                tx = n * W
                ty = m * H
                dx = tx - x0
                dy = ty - y0
                d = math.hypot(dx, dy)
                if best is None or abs(d - R) < best[0]:
                    best = (abs(d - R), dx, dy, d)
        if best is None or best[3] < 1e-6:
            return
        _, dx, dy, dist = best
        # Set velocity to reach that point in exactly T seconds; adjust speed magnitude accordingly
        vx = dx / T
        vy = dy / T
        self._vel = QtCore.QPointF(vx, vy)
        self._speed = float(dist / T)

    # ------------- Key handling -------------
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        key = e.key()
        if key in (Qt.Key_Space,):
            self._paused = not self._paused
            return
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            self._speed *= 1.1
            return
        if key in (Qt.Key_Minus, Qt.Key_Underscore):
            self._speed /= 1.1
            return
        if key in (Qt.Key_T,):
            self._theme = (self._theme + 1) % len(THEMES)
            return
        if key in (Qt.Key_C,):
            self._show_overlay = not self._show_overlay
            return
        if key in (Qt.Key_H,):
            self._stage_corner_next()
            return
        if key in (Qt.Key_R,):
            # Reset to center with random-ish dir
            self._pos = QtCore.QPointF(
                (self.width() - self._logo_w_px) / 2,
                (self.height() - self._logo_h_px) / 2,
            )
            ang = (self._elapsed.elapsed() % 1000) / 1000.0 * 2 * math.pi
            self._vel = QtCore.QPointF(
                self._speed * math.cos(ang), self._speed * math.sin(ang)
            )
            return
        if key in (Qt.Key_Question, Qt.Key_Slash):
            self._show_help = not self._show_help
            return
        if key in (Qt.Key_F,):
            # Toggle fullscreen of the top-level window
            win = self.window()
            if isinstance(win, QtWidgets.QWidget):
                if win.isFullScreen():
                    win.showNormal()
                else:
                    win.showFullScreen()
            return
        if key in (Qt.Key_Escape,):
            QApplication.quit()
            return
        super().keyPressEvent(e)


# -------------------------
# Main Window
# -------------------------


class Screensaver(QWidget):
    def __init__(self, settings: StartSettings):
        super().__init__()
        self.setWindowTitle("TV Screensaver")
        self.setCursor(Qt.BlankCursor)
        self.setMouseTracking(False)

        # Load image
        pm = QPixmap(IMG_PATH)
        if pm.isNull():
            # Fallback: generate placeholder
            pm = QPixmap(256, 256)
            pm.fill(Qt.black)
            painter = QPainter(pm)
            painter.setPen(QtGui.QColor("white"))
            painter.setFont(QFont("Consolas", 24))
            painter.drawText(pm.rect(), Qt.AlignCenter, "img.png")
            painter.end()
        img = pm.toImage()

        self.gl = GLBouncer(img, settings, self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.gl)

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        # Delegate to GL widget
        self.gl.keyPressEvent(e)


def run():
    app = QApplication(sys.argv)

    # Startup dialog
    dlg = StartDialog()
    if dlg.exec() != QDialog.Accepted:
        return 0
    settings = dlg.result_settings()

    win = Screensaver(settings)
    win.showFullScreen()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
