import os

IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img.png")

import sys
import math
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QAction,
    QCursor,
    QFont,
    QImage,
    QPainter,
    QPixmap,
)
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


class ScreensaverWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setMouseTracking(True)
        self.image = QImage(IMG_PATH)
        if self.image.isNull():
            # Fallback placeholder if image file is not found
            placeholder = QImage(400, 400, QImage.Format_ARGB32)
            placeholder.fill(Qt.black)
            ph_painter = QtGui.QPainter(placeholder)
            grad = QtGui.QLinearGradient(0, 0, 400, 400)
            grad.setColorAt(0.0, QtGui.QColor(30, 30, 30))
            grad.setColorAt(1.0, QtGui.QColor(80, 80, 80))
            ph_painter.fillRect(0, 0, 400, 400, grad)
            ph_painter.setPen(QtGui.QPen(QtGui.QColor(200, 80, 80)))
            ph_painter.setFont(QtGui.QFont("Segoe UI", 22, QtGui.QFont.Bold))
            ph_painter.drawText(
                QtCore.QRectF(0, 0, 400, 400), Qt.AlignCenter, "img.png\nmissing"
            )
            ph_painter.end()
            self.image = placeholder
        self.image = self.image.scaled(
            400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image = self.image.convertToFormat(QImage.Format_ARGB32)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS
        # Position and bounds
        self.x = 0.0
        self.y = 0.0
        self.min_x = 0.0
        self.min_y = 0.0
        self.max_x = 0.0
        self.max_y = 0.0
        # Motion
        self.speed_fac = 1.8
        self.scale = 1.0
        inv = 1.0 / math.sqrt(2.0)
        self.dir_x = inv
        self.dir_y = inv
        # Overlays/state
        self.paused = False
        self.show_visualizer = False
        self.overlay_quantize = False  # disable by default to avoid jitter
        self.overlay_points_cache = None

    def update_animation(self):
        # Update bounds based on widget size
        self.max_x = max(0.0, self.width() - (self.image.width() * self.scale))
        self.max_y = max(0.0, self.height() - (self.image.height() * self.scale))

        if self.paused:
            self.overlay_points_cache = None
            self.update()
            return

        # Move
        self.x += self.dir_x * self.speed_fac
        self.y += self.dir_y * self.speed_fac

        # Bounce
        bounced = False
        if self.x <= self.min_x:
            self.x = self.min_x
            self.dir_x = -self.dir_x
            bounced = True
        elif self.x >= self.max_x:
            self.x = self.max_x
            self.dir_x = -self.dir_x
            bounced = True
        if self.y <= self.min_y:
            self.y = self.min_y
            self.dir_y = -self.dir_y
            bounced = True
        elif self.y >= self.max_y:
            self.y = self.max_y
            self.dir_y = -self.dir_y
            bounced = True

        if bounced:
            self._normalize_dir()

        self.overlay_points_cache = None
        self.update()

    def _normalize_dir(self):
        mag = math.hypot(self.dir_x, self.dir_y)
        if mag > 1e-9:
            self.dir_x /= mag
            self.dir_y /= mag
        else:
            inv = 1.0 / math.sqrt(2.0)
            self.dir_x = inv
            self.dir_y = inv

    def toggle_pause(self):
        self.paused = not self.paused
        self.overlay_points_cache = None
        self.update()

    def toggle_visualizer(self):
        self.show_visualizer = not self.show_visualizer
        self.overlay_points_cache = None
        self.update()

    def rotate_dir(self, degrees: float):
        theta = math.radians(degrees)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        dx = self.dir_x * cos_t - self.dir_y * sin_t
        dy = self.dir_x * sin_t + self.dir_y * cos_t
        self.dir_x, self.dir_y = dx, dy
        self._normalize_dir()
        self.overlay_points_cache = None
        self.update()

    def set_dir_towards(self, px: float, py: float):
        cx = self.x + (self.image.width() * self.scale) * 0.5
        cy = self.y + (self.image.height() * self.scale) * 0.5
        dx = px - cx
        dy = py - cy
        if abs(dx) < 1e-6 and abs(dy) < 1e-6:
            return
        self.dir_x, self.dir_y = dx, dy
        self._normalize_dir()
        self.overlay_points_cache = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), Qt.black)

        if not self.image.isNull():
            image = self.image.scaled(
                int(400 * self.scale),
                int(400 * self.scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawImage(QtCore.QPointF(self.x, self.y), image)

        if self.show_visualizer:
            points = self._get_overlay_points()
            if len(points) > 1:
                pen = QtGui.QPen(QtGui.QColor(0, 255, 180, 200))
                pen.setWidth(2)
                painter.setPen(pen)
                for i in range(len(points) - 1):
                    p1 = points[i]
                    p2 = points[i + 1]
                    painter.drawLine(
                        QtCore.QPointF(p1[0], p1[1]), QtCore.QPointF(p2[0], p2[1])
                    )
                col_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 180))
                painter.setPen(col_pen)
                for p in points[1:-1]:
                    painter.drawEllipse(QtCore.QPointF(p[0], p[1]), 3, 3)

        painter.end()
        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.paused:
            self.set_dir_towards(event.position().x(), event.position().y())
        super().mouseMoveEvent(event)

    def _center_and_bounds(self):
        w = self.image.width() * self.scale
        h = self.image.height() * self.scale
        cx = float(self.x) + w * 0.5
        cy = float(self.y) + h * 0.5
        left = self.min_x + w * 0.5
        right = self.max_x + w * 0.5
        top = self.min_y + h * 0.5
        bottom = self.max_y + h * 0.5
        return cx, cy, left, right, top, bottom, w, h

    def _simulate_path(
        self,
        max_bounces=200,
        stop_on_corner=True,
        near_threshold=5.0,
        corner_threshold=1.0,
    ):
        cx, cy, left, right, top, bottom, _, _ = self._center_and_bounds()
        dx = self.dir_x
        dy = self.dir_y
        if self.overlay_quantize:
            B = 24
            sx = 1 if dx >= 0 else -1
            sy = 1 if dy >= 0 else -1
            qx = max(1, int(round(abs(dx) * B)))
            qy = max(1, int(round(abs(dy) * B)))
            dx = sx * qx
            dy = sy * qy
            mag = math.hypot(dx, dy)
            dx /= mag
            dy /= mag

        pts = [(cx, cy)]
        near_events = []
        corner_event = None
        bounces = 0
        eps = 1e-9
        while bounces < max_bounces:
            t_v = None
            t_h = None
            if dx > eps:
                t_v = (right - cx) / dx
            elif dx < -eps:
                t_v = (left - cx) / dx
            if dy > eps:
                t_h = (bottom - cy) / dy
            elif dy < -eps:
                t_h = (top - cy) / dy

            candidates = []
            if t_v is not None and t_v > eps:
                candidates.append((t_v, "v"))
            if t_h is not None and t_h > eps:
                candidates.append((t_h, "h"))
            if not candidates:
                break

            # Near-corner estimation
            if t_v is not None and t_h is not None and t_v > eps and t_h > eps:
                dt = abs(t_v - t_h)
                if dt < near_threshold:
                    t_corner = 0.5 * (t_v + t_h)
                    px = cx + dx * t_corner
                    py = cy + dy * t_corner
                    frames = t_corner / max(self.speed_fac, eps)
                    evt = {"pos": (px, py), "frames": frames, "delta": dt}
                    near_events.append(evt)
                    if dt < corner_threshold and stop_on_corner:
                        corner_event = evt
                        pts.append((px, py))
                        break

            t_min, kind = min(candidates, key=lambda x: x[0])
            cx += dx * t_min
            cy += dy * t_min
            pts.append((cx, cy))
            if kind == "v":
                dx = -dx
            else:
                dy = -dy
            bounces += 1

        return pts, near_events, corner_event

    def _get_overlay_points(self):
        if self.overlay_points_cache is not None:
            return self.overlay_points_cache
        pts, _, _ = self._simulate_path(max_bounces=150, stop_on_corner=False)
        self.overlay_points_cache = pts
        return pts


class UISettingsWindow(QDialog):
    def __init__(self, root: "ScreensaverApp"):
        super().__init__()
        self.setWindowTitle("Screensaver Settings")
        self.screensaver_widget = root.screensaver_widget
        self.root = root
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(int(self.screensaver_widget.speed_fac * 10))
        self.speed_slider.valueChanged.connect(self.update_speed)

        self.scale_label = QLabel("Scale:")
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setValue(int(self.screensaver_widget.scale * 100))
        self.scale_slider.valueChanged.connect(self.update_scale)

        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.speed_slider)
        self.layout.addWidget(self.scale_label)
        self.layout.addWidget(self.scale_slider)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.close)
        self.layout.addWidget(self.button_box)

    def keyPressEvent(self, arg__1):
        if arg__1.key() == Qt.Key_C:
            self.root.ui_toggle()

    def update_speed(self, value):
        self.screensaver_widget.speed_fac = value / 10.0
        self.screensaver_widget.overlay_points_cache = None
        self.screensaver_widget.update()

    def update_scale(self, value):
        self.screensaver_widget.scale = value / 100.0
        self.screensaver_widget.overlay_points_cache = None
        self.screensaver_widget.update()

    def __init__(self, root: "ScreensaverApp"):
        super().__init__()
        self.setWindowTitle("Screensaver Settings")
        self.screensaver_widget = root.screensaver_widget
        self.root = root
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(int(self.screensaver_widget.speed_fac * 10))
        self.speed_slider.valueChanged.connect(self.update_speed)

        self.scale_label = QLabel("Scale:")
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setValue(int(self.screensaver_widget.scale * 100))
        self.scale_slider.valueChanged.connect(self.update_scale)

        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.speed_slider)
        self.layout.addWidget(self.scale_label)
        self.layout.addWidget(self.scale_slider)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.close)
        self.layout.addWidget(self.button_box)

    def keyPressEvent(self, arg__1):
        if arg__1.key() == Qt.Key_C:
            self.root.ui_toggle()

    def update_speed(self, value):
        self.screensaver_widget.speed_fac = value / 10.0
        self.screensaver_widget.overlay_points_cache = None
        self.screensaver_widget.update()

    def update_scale(self, value):
        self.screensaver_widget.scale = value / 100.0
        self.screensaver_widget.overlay_points_cache = None
        self.screensaver_widget.update()


class ScreensaverApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV Screensaver")
        self.setGeometry(100, 100, 800, 600)
        self.screensaver_widget = ScreensaverWidget(self)
        self.setCentralWidget(self.screensaver_widget)
        self.ui_window = None
        self.ui_visible = False
        self.setCursor(Qt.BlankCursor)
        self.screensaver_widget.setCursor(Qt.BlankCursor)
        self.showFullScreen()
        # If a second monitor exists, spawn StatsWindow there
        try:
            screens = QtWidgets.QApplication.screens()
            if screens and len(screens) > 1:
                self.stats_window = StatsWindow(self.screensaver_widget, screens[1])
                self.stats_window.show()
        except Exception:
            self.stats_window = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
        elif event.key() == Qt.Key_C:
            self.ui_toggle()
        elif event.key() == Qt.Key_Space:
            self.screensaver_widget.toggle_pause()
        elif event.key() == Qt.Key_V:
            self.screensaver_widget.toggle_visualizer()
        elif event.key() == Qt.Key_Left:
            # Re-angle while paused (or anytime)
            self.screensaver_widget.rotate_dir(-5.0)
        elif event.key() == Qt.Key_Right:
            self.screensaver_widget.rotate_dir(5.0)

    def closeEvent(self, event):
        self.screensaver_widget.timer.stop()
        event.accept()

    def ui_toggle(self):
        self.ui_visible = not self.ui_visible
        if self.ui_visible:
            if self.ui_window is None:
                self.ui_window = UISettingsWindow(self)
            self.ui_window.show()
            # Show the mouse cursor
            self.unsetCursor()
            self.screensaver_widget.unsetCursor()
        else:
            if self.ui_window is not None:
                self.ui_window.hide()
            # Hide the mouse cursor over the screensaver
            self.setCursor(Qt.BlankCursor)
            self.screensaver_widget.setCursor(Qt.BlankCursor)


class StatsCanvas(QWidget):
    def __init__(self, src_widget: ScreensaverWidget):
        super().__init__()
        self.src = src_widget
        self.setMinimumSize(200, 150)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), Qt.black)

        # Get path until the next corner event
        pts, _, corner = self.src._simulate_path(max_bounces=300, stop_on_corner=True)
        if len(pts) > 1:
            # Scale to fit this canvas while preserving aspect
            src_w = max(1, self.src.width())
            src_h = max(1, self.src.height())
            scale = min(self.width() / src_w, self.height() / src_h)
            tx = (self.width() - src_w * scale) * 0.5
            ty = (self.height() - src_h * scale) * 0.5

            pen = QtGui.QPen(QtGui.QColor(220, 60, 60, 210))
            pen.setWidth(2)
            painter.setPen(pen)
            for i in range(len(pts) - 1):
                x1 = tx + pts[i][0] * scale
                y1 = ty + pts[i][1] * scale
                x2 = tx + pts[i + 1][0] * scale
                y2 = ty + pts[i + 1][1] * scale
                painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2))

            # Draw corner point if available
            if corner is not None:
                px, py = corner["pos"]
                painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 200, 200)))
                painter.drawEllipse(
                    QtCore.QPointF(tx + px * scale, ty + py * scale), 4, 4
                )

        painter.end()
        event.accept()


class StatsWindow(QtWidgets.QMainWindow):
    def __init__(self, src_widget: ScreensaverWidget, target_screen: QtGui.QScreen):
        super().__init__()
        self.setWindowTitle("Corner Hit Forecast")
        self.src = src_widget
        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)
        v.setContentsMargins(8, 8, 8, 8)
        self.info_label = QtWidgets.QLabel()
        self.info_label.setStyleSheet("color: white; font-size: 14px;")
        self.canvas = StatsCanvas(src_widget)
        v.addWidget(self.info_label)
        v.addWidget(self.canvas, 1)
        self.setCentralWidget(central)

        # Move to target screen
        geo = target_screen.geometry()
        self.setGeometry(geo)
        self.showFullScreen()

        # Update periodically
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(125)  # ~8 Hz

    def refresh(self):
        # Compute next near-perfect corner hit and upcoming near events
        pts, near_events, corner = self.src._simulate_path(
            max_bounces=800,
            stop_on_corner=True,
            near_threshold=5.0,
            corner_threshold=1.0,
        )
        if corner is not None:
            frames = corner["frames"]
            # Approximate seconds using 60 FPS
            seconds = frames / 60.0
            text = f"Next near-perfect corner: ~{seconds:.2f}s (delta={corner['delta']:.2f})\n"
            # Show upcoming near hits until that corner
            items = []
            count = 0
            for e in near_events:
                if e is corner:
                    break
                if e["delta"] >= 1.0:  # exclude the final corner event here
                    items.append(f"t~{(e['frames']/60.0):.2f}s, delta={e['delta']:.2f}")
                    count += 1
                if count >= 5:
                    break
            if not items:
                text += "No earlier near-corner events."
            else:
                text += "Upcoming near-corner events:\n  - " + "\n  - ".join(items)
        else:
            text = "No near-perfect corner detected in forecast window."
        self.info_label.setText(text)
        self.canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreensaverApp()
    window.show()
    sys.exit(app.exec())
