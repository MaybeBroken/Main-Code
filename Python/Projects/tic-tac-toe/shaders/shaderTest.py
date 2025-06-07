VERT = """#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float Frame;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;
out float frame;

void main() {
    float x = p3d_Vertex.x;
    float y = p3d_Vertex.y;
    float z = p3d_Vertex.z;
    float w = p3d_Vertex.w;
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(x, y, z, w);
    texcoord = p3d_MultiTexCoord0;
    frame = Frame;
}

"""

FRAG = """#version 330

uniform sampler2D p3d_Texture0;
uniform float threshold;
uniform float boost;

in vec2 texcoord;
in float frame;

out vec4 p3d_FragColor;


void main() {
    vec4 texColor = texture(p3d_Texture0, texcoord);
    
    // Boost dark areas more aggressively while keeping bright areas the same
    float brightness = dot(texColor.rgb, vec3(0.299, 0.587, 0.114)); // Grayscale brightness
    float boostFactor = smoothstep(0.0, threshold, brightness); // Apply a steeper curve to dark areas

    vec3 adjustedColor = mix(texColor.rgb * boost, texColor.rgb, boostFactor); // Boost only dark parts more
    adjustedColor = clamp(adjustedColor, 0.0, 1.0); // Ensure colors remain in valid range
    p3d_FragColor = vec4(adjustedColor, texColor.a);
}
"""

SHADERNAME = "brighten"


from panda3d.core import *
from panda3d.core import (
    loadPrcFileData,
    Shader,
    TransparencyAttrib,
    TextNode,
)
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, radians as degToRad
from screeninfo import get_monitors
from direct.gui.DirectGui import *
import os

os.chdir(os.path.dirname(__file__))

monitor = get_monitors()

loadPrcFileData(
    "",
    f"gl-coordinate-system default\nwin-size {monitor[0].width} {monitor[0].height}\nfullscreen 0\nundecorated 1\ngl-version 3 3\ngl-debug true\n",
)


class Wvars:
    speed = 50
    swingSpeed = 60
    camX = 0
    camY = 0
    camZ = 0
    camH = 0
    camP = 0
    camR = 0


class MyApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.render.setShaderAuto()
        self.disableMouse()

        self.model = self.loader.loadModel("../models/control1.bam")
        self.model.reparentTo(self.render)
        self.model.setScale(5)

        # Load and apply the shader
        with open(f"{SHADERNAME}.vert", "w") as vert_file:
            vert_file.write(VERT)
        with open(f"{SHADERNAME}.frag", "w") as frag_file:
            frag_file.write(FRAG)

        self.shader = Shader.load(
            Shader.SL_GLSL,
            f"{SHADERNAME}.vert",
            f"{SHADERNAME}.frag",
        )
        self.model.setShader(self.shader)
        self.model.setTransparency(TransparencyAttrib.MAlpha)
        self.model.setShaderInput("threshold", 0.05)
        self.model.setShaderInput("boost", 5.0)

        self.posText = OnscreenText(
            text=f"{Wvars.camX}, {Wvars.camY}, {Wvars.camZ}",
            pos=(-1.3, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
        )

        self.accept("wheel_up", self.wireframeOn)
        self.accept("wheel_down", self.wireframeOff)

        self.setupControls()
        self.taskMgr.add(self.update, "update")

    def update(self, task):

        playerMoveSpeed = 1
        frame = task.frame
        self.model.setShaderInput("Frame", frame)

        result = task.cont
        playerMoveSpeed = Wvars.speed / 10

        x_movement = 0
        y_movement = 0
        z_movement = 0

        dt = globalClock.getDt()  # type: ignore

        if self.keyMap["forward"]:
            x_movement -= dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
            y_movement += dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
        if self.keyMap["backward"]:
            x_movement += dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
            y_movement -= dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
        if self.keyMap["left"]:
            x_movement -= dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
            y_movement -= dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
        if self.keyMap["right"]:
            x_movement += dt * playerMoveSpeed * cos(degToRad(self.camera.getH()))
            y_movement += dt * playerMoveSpeed * sin(degToRad(self.camera.getH()))
        if self.keyMap["up"]:
            z_movement += dt * playerMoveSpeed
        if self.keyMap["down"]:
            z_movement -= dt * playerMoveSpeed

        self.camera.setPos(
            self.camera.getX() + x_movement,
            self.camera.getY() + y_movement,
            self.camera.getZ() + z_movement,
        )
        Wvars.camX = self.camera.getX()
        Wvars.camY = self.camera.getY()
        Wvars.camZ = self.camera.getZ()

        md = self.win.getPointer(0)
        mouseX = md.getX()
        mouseY = md.getY()

        if int(monitor[0].width / 2) - mouseX >= int(monitor[0].width / 4):
            self.win.movePointer(0, x=int(monitor[0].width / 2), y=int(mouseY))
            self.lastMouseX = int(monitor[0].width / 2)
        elif int(monitor[0].width / 2) - mouseX <= -int(monitor[0].width / 4):
            self.win.movePointer(0, x=int(monitor[0].width / 2), y=int(mouseY))
            self.lastMouseX = int(monitor[0].width / 2)
        elif int(monitor[0].height / 2) - mouseY >= int(monitor[0].height / 4):
            self.win.movePointer(0, x=int(mouseX), y=int(monitor[0].height / 2))
            self.lastMouseY = int(monitor[0].height / 2)
        elif int(monitor[0].height / 2) - mouseY <= -int(monitor[0].height / 4):
            self.win.movePointer(0, x=int(mouseX), y=int(monitor[0].height / 2))
            self.lastMouseY = int(monitor[0].height / 2)
        else:
            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY

            self.cameraSwingFactor = Wvars.swingSpeed / 10

            currentH = self.camera.getH()
            currentP = self.camera.getP()
            currentR = self.camera.getR()

            Wvars.camH = currentH
            Wvars.camP = currentP
            Wvars.camR = currentR

            self.camera.setHpr(
                currentH - mouseChangeX * dt * self.cameraSwingFactor,
                min(
                    90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)
                ),
                0,
            )

            self.lastMouseX = mouseX
            self.lastMouseY = mouseY
        self.posText.setText(
            f"X: {round(Wvars.camX, 2)}, Y: {round(Wvars.camY, 2)}, Z: {round(Wvars.camZ, 2)}"
        )
        return result

    def setupControls(self):
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        self.accept("w", self.updateKeyMap, ["forward", True])
        self.accept("w-up", self.updateKeyMap, ["forward", False])
        self.accept("s", self.updateKeyMap, ["backward", True])
        self.accept("s-up", self.updateKeyMap, ["backward", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("space", self.updateKeyMap, ["up", True])
        self.accept("space-up", self.updateKeyMap, ["up", False])
        self.accept("shift", self.updateKeyMap, ["down", True])
        self.accept("shift-up", self.updateKeyMap, ["down", False])
        self.accept("k", self.toggleShaders)

        self.accept("escape", exit)
        self.accept("q", exit)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def toggleShaders(self):
        if self.model.getShader() is None:
            self.model.setShader(self.shader)
        else:
            self.model.clearShader()
            self.model.setShaderAuto()


app = MyApp()
app.run()
