from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.stdpy.threading import Thread
from direct.gui.DirectGui import *
import os
from screeninfo import get_monitors
import mouse
from panda3d.core import (
    loadPrcFileData,
    Vec4,
    TransparencyAttrib,
    PointLight,
    AmbientLight,
    LineSegs,
    Texture,
    Shader,
    Vec3,
)
from direct.interval.IntervalGlobal import *
import complexpbr
import random
from typing import Callable
from direct.filter.CommonFilters import CommonFilters
from src.scripts.utils import *

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def get_current_monitor():
    x, y = mouse.get_position()
    for idx, m in enumerate(get_monitors()):
        if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
            return idx
    return 0


monitor = get_monitors()[get_current_monitor()]
monitor_width = monitor.width
monitor_height = monitor.height
aspect_ratio = monitor_width / monitor_height

loadPrcFileData("", "win-size " + str(monitor_width) + " " + str(monitor_height))
loadPrcFileData("", "window-title Slipstream Client")
loadPrcFileData("", "undecorated true")


class shaderMgr:
    def __init__(self, manager):
        self.threshold = Vec4(0.8, 0.9, 0.85, 0.2)
        self.manager = manager
        self.tex1 = Texture()
        self.depthTex = Texture()
        self.tex2 = Texture()
        self.tex3 = Texture()
        self.tex4 = Texture()
        self.tex1.setCompression(Texture.CMOff)
        self.depthTex.setCompression(Texture.CMOff)
        self.tex2.setCompression(Texture.CMOff)
        self.tex3.setCompression(Texture.CMOff)
        self.tex4.setCompression(Texture.CMOff)
        self.finalquad = self.manager.renderSceneInto(
            colortex=self.tex1, depthtex=self.depthTex
        )
        self.interquad3 = self.manager.renderQuadInto(colortex=self.tex4)
        self.interquad3.setShader(
            Shader.load(
                Shader.SL_GLSL,
                "shaders/VERT2D.vert",
                "shaders/lensFlare.glsl",
            )
        )
        self.interquad3.setShaderInput("pos", Vec3(0, 0, 0))
        self.interquad3.setShaderInput("strength", 1.0)
        self.interquad3.setShaderInput("Frame", 0)

        self.finalquad.setShader(Shader.load("shaders/lens_flare.sha"))
        self.finalquad.setShaderInput("tex1", self.tex1)
        self.finalquad.setShaderInput("tex2", self.tex2)
        self.finalquad.setShaderInput("tex3", self.tex3)
        self.finalquad.setShaderInput("tex4", self.tex4)
        self.finalquad.setShaderInput("depth", self.depthTex)
        self.lf_samples = 8
        self.lf_halo_width = 0.1
        self.lf_flare_dispersal = 0.35
        self.lf_chroma_distort = 0.001
        self.lf_settings = Vec3(
            self.lf_samples, self.lf_halo_width, self.lf_flare_dispersal
        )
        self.finalquad.setShaderInput("lf_settings", self.lf_settings)
        self.finalquad.setShaderInput("lf_chroma_distort", self.lf_chroma_distort)
        self.finalquad.setTransparency(TransparencyAttrib.MAlpha)


class Window(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(0, 0, 0, 1)
        self.mfont = self.loader.loadFont(
            "src/fonts/AquireLight-YzE0o.otf", pixelsPerUnit=200
        )
        self.accept("q", self.userExit)
        self.filters = CommonFilters(self.win, self.cam)
        self.filters.setBloom(intensity=0.2, size="large")
        self.filters.setMSAA(32)
        fmanager = self.filters.manager
        self.shaderMgr = shaderMgr(fmanager)

        self.background_intro = DirectFrame(
            parent=self.render2d,
            frameColor=(0, 0, 0, 1),
            frameSize=(-1, 1, -1, 1),
            pos=(0, 0, 0),
        )
        self.background_intro.setTransparency(TransparencyAttrib.MAlpha)
        self.root_intro = OnscreenText(
            text="Programmed by\nMaybeBroken",
            style=1,
            fg=(1, 1, 1, 1),
            bg=(0, 0, 0, 1),
            pos=(0, 0),
            scale=0.3,
            font=self.mfont,
        )
        self.root_intro.setTransparency(TransparencyAttrib.MAlpha)

        self.sun = create_circle(radius=15, resolution=6)
        self.sun.reparentTo(self.render)
        self.sun.setPos(0, 2000, 50)
        self.sun.setHpr(0, 90, 0)

        self.intro_grid = self.generateGrid(grid_size=200, spacing=1.5)

        self.camera.setPos(0, -8, 1)
        self.camLens.setFov(94)

        LerpColorScaleInterval(
            nodePath=self.root_intro,
            duration=1.5,
            colorScale=Vec4(1, 1, 1, 1),
            startColorScale=Vec4(1, 1, 1, 0),
        ).start()
        self.doMethodLater(
            2.0,
            lambda task: LerpColorScaleInterval(
                nodePath=self.root_intro,
                duration=1.5,
                colorScale=Vec4(1, 1, 1, 0),
                startColorScale=Vec4(1, 1, 1, 1),
            ).start(),
            "fade_out_intro",
        )
        self.doMethodLater(
            4.0,
            lambda task: self.build_intro_UI(),
            "build_intro_UI",
        )
        self.taskMgr.add(self.update_tasks, "update_tasks")
        self.taskMgr.add(self.move_background_task, "move_background_task")

    def update_tasks(self, task):
        MouseOverManager.update()
        pos = Math.project_point_to_2d(
            camera=self.camera,
            lens=self.camLens,
            node=self.sun,
        )
        if pos:
            self.shaderMgr.interquad3.setShaderInput(
                "pos", (pos[0] / aspect_ratio, pos[2])
            )
        return task.cont

    def move_background_task(self, task):
        """Task to move the background grid."""
        if self.intro_grid.getY() <= 1.5:
            self.intro_grid.setY(self.intro_grid.getY() + 0.005)
        else:
            self.intro_grid.setY(-1.5)
        return task.cont

    def build_intro_UI(self):
        self.start_button = DirectButton(
            text="Start",
            scale=0.2,
            text_fg=(1, 1, 1, 1),
            color=(0, 0, 0, 0),
            geom=None,
            relief=DGG.FLAT,
            pos=(0, 0, 0.5),
            command=self.start_game,
            text_font=self.mfont,
        )
        self.start_button.setTransparency(TransparencyAttrib.MAlpha)

        def start_button_hover(is_hovered):
            if is_hovered:
                LerpColorScaleInterval(
                    nodePath=self.start_button,
                    duration=0.05,
                    colorScale=Vec4(0.1, 1, 0.2, 1),
                    startColorScale=Vec4(1, 1, 1, 1),
                ).start()
            else:
                LerpColorScaleInterval(
                    nodePath=self.start_button,
                    duration=0.075,
                    colorScale=Vec4(1, 1, 1, 1),
                    startColorScale=Vec4(0.1, 1, 0.2, 1),
                ).start()

        MouseOverManager.registerElement(
            self.start_button,
            (1, 1),
            start_button_hover,
        )
        LerpColorScaleInterval(
            nodePath=self.start_button,
            duration=1.5,
            colorScale=Vec4(1, 1, 1, 1),
            startColorScale=Vec4(1, 1, 1, 0),
        ).start()
        LerpColorScaleInterval(
            nodePath=self.background_intro,
            duration=1.5,
            colorScale=Vec4(1, 1, 1, 0),
            startColorScale=Vec4(1, 1, 1, 1),
        ).start()
        self.doMethodLater(
            1.5,
            lambda task: self.background_intro.destroy(),
            "destroy_background_intro",
        )

    def start_game(self):
        self.start_button["state"] = (
            DGG.DISABLED
        )  # disable button to prevent double-clicks
        self.start_button.setState()
        LerpColorScaleInterval(
            nodePath=self.start_button,
            duration=1,
            colorScale=Vec4(1, 1, 1, 0),
            startColorScale=Vec4(1, 1, 1, 1),
        ).start()
        self.doMethodLater(
            1,
            lambda task: self.start_button.destroy(),
            "destroy_start_button",
        )
        LerpPosInterval(
            nodePath=self.sun,
            duration=1,
            pos=(0, 2000, -10),
            startPos=(0, 2000, 50),
            blendType="easeInOut",
        ).start()
        LerpColorScaleInterval(
            nodePath=self.intro_grid,
            duration=2.25,
            colorScale=Vec4(1, 1, 1, 0),
            startColorScale=Vec4(1, 1, 1, 1),
            blendType="easeInOut",
        ).start()
        LerpFunctionInterval(
            function=lambda t: self.shaderMgr.interquad3.setShaderInput("strength", t),
            duration=2,
            fromData=1,
            toData=0,
        ).start()
        self.doMethodLater(
            0.75,
            lambda task: [
                LerpScaleInterval(
                    nodePath=self.sun,
                    duration=1.5,
                    scale=(20, 20, 20),
                    startScale=(1, 1, 1),
                    blendType="easeInOut",
                ).start(),
                LerpHprInterval(
                    nodePath=self.sun,
                    duration=1.5,
                    hpr=(0, 90, 0),
                    startHpr=(0, 90, 0),
                    blendType="easeInOut",
                ).start(),
                LerpPosInterval(
                    nodePath=self.camera,
                    duration=1.5,
                    pos=(0, -8, 0),
                    startPos=(0, -8, 1),
                    blendType="easeInOut",
                ).start(),
                LerpHprInterval(
                    nodePath=self.camera,
                    duration=1.75,
                    hpr=(0, 0, 180),
                    startHpr=(0, 0, 0),
                    blendType="easeInOut",
                ).start(),
                task.done,
            ][-1],
            "expand_sphere",
        )

    def generateGrid(self, grid_size=100, spacing=10):
        """Generate a 2D grid around the player that fades into transparency."""
        self.gridNode = self.render.attachNewNode("gridNode")
        for x in range(-grid_size, grid_size + 1):
            line = LineSegs()
            line.setThickness(1.0)
            line.setColor(1, 1, 1, 1)  # White color
            # Horizontal line
            line.moveTo(x * spacing, -grid_size * spacing, 0)
            line.drawTo(x * spacing, grid_size * spacing, 0)
            node = line.create()
            self.gridNode.attachNewNode(node)

        for y in range(-grid_size, grid_size + 1):
            line = LineSegs()
            line.setThickness(1.0)
            line.setColor(1, 1, 1, 1)  # White color
            # Vertical line
            line.moveTo(-grid_size * spacing, y * spacing, 0)
            line.drawTo(grid_size * spacing, y * spacing, 0)
            node = line.create()
            self.gridNode.attachNewNode(node)
        self.gridNode.setTransparency(TransparencyAttrib.MAlpha)
        return self.gridNode


class MouseOverManager:
    def __init__(self):
        self.elements = []
        self.activeElements = []

    def registerElement(
        self, element, hitbox_scale: tuple[2], callback: Callable, *args, **kwargs
    ):
        """
        Registers an element with a callback to be triggered when the mouse is over the element.
        :param element: The NodePath or DirectGUI element to monitor.
        :param callback: The function to call when the mouse is over the element.
        """
        self.elements.append((element, hitbox_scale, callback, args, kwargs))

    def update(self):
        """
        Checks if the mouse is over any registered elements and triggers the corresponding callbacks.
        """
        if base.mouseWatcherNode.hasMouse():  # type: ignore
            mouse_pos = base.mouseWatcherNode.getMouse()  # type: ignore
            for element, hitbox_scale, callback, args, kwargs in self.elements:
                try:
                    if not element or element.isEmpty() or element.isHidden():
                        self.elements.remove(
                            (element, hitbox_scale, callback, args, kwargs)
                        )
                        continue
                except:
                    self.elements.remove(
                        (element, hitbox_scale, callback, args, kwargs)
                    )
                    continue
                bounds = element.getBounds()
                xmin, xmax, ymin, ymax = bounds
                transform = element.getTransform(base.render2d)  # type: ignore
                pos: tuple[3] = transform.getPos()
                scale: tuple[3] = element.getScale()
                xmin *= scale[0] * hitbox_scale[0]
                xmax *= scale[0] * hitbox_scale[0]
                ymin *= scale[2] * hitbox_scale[1]
                ymax *= scale[2] * hitbox_scale[1]

                xmin += pos[0]
                xmax += pos[0]
                ymin += pos[2]
                ymax += pos[2]

                bounds = (xmin, xmax, ymin, ymax)
                if xmin <= mouse_pos.x <= xmax and ymin <= mouse_pos.y <= ymax:
                    if element not in self.activeElements:
                        self.activeElements.append(element)
                        callback(True, *args, **kwargs)
                else:
                    if element in self.activeElements:
                        self.activeElements.remove(element)
                        callback(False, *args, **kwargs)


MouseOverManager = MouseOverManager()

if __name__ == "__main__":
    app = Window()
    app.run()
