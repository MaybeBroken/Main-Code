"""This is a utility script to combine multiple shader files into a single file.
It is designed to work with the Panda3D engine and is intended for use in a project that involves shader programming in GLSL.
"""

import os
from tkinter import *
from tkinter import messagebox, Tk, filedialog, Radiobutton
from time import sleep
from threading import Thread
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from panda3d.core import (
    loadPrcFileData,
    Shader,
    TransparencyAttrib,
    CardMaker,
    Geom,
    GeomNode,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomTriangles,
)
from math import sin, cos, radians as degToRad
import numpy as np
import random
import sys


@staticmethod
def Sphere(radius, lat, lon):
    """
    Create a UV sphere mesh with the given radius and position.
    """

    # Create vertex data format
    format = GeomVertexFormat.get_v3n3c4t2()
    vdata = GeomVertexData("vertices", format, Geom.UH_static)

    # Create vertex writer
    vertex_writer = GeomVertexWriter(vdata, "vertex")
    normal_writer = GeomVertexWriter(vdata, "normal")
    color_writer = GeomVertexWriter(vdata, "color")
    texcoord_writer = GeomVertexWriter(vdata, "texcoord")

    # Generate vertices
    for i in range(lat + 1):
        lat_angle = np.pi * i / lat
        for j in range(lon + 1):
            lon_angle = 2 * np.pi * j / lon
            x = radius * np.sin(lat_angle) * np.cos(lon_angle)
            y = radius * np.sin(lat_angle) * np.sin(lon_angle)
            z = radius * np.cos(lat_angle)
            vertex_writer.add_data3f(x, y, z)
            normal_writer.add_data3f(x / radius, y / radius, z / radius)
            color_writer.add_data4f(1.0, 1.0, 1.0, 1.0)
            texcoord_writer.add_data2f(j / lon, i / lat)

    # Create triangles
    tris = []
    for i in range(lat):
        for j in range(lon):
            tris.append(
                (
                    i * (lon + 1) + j,
                    (i + 1) * (lon + 1) + j,
                    (i + 1) * (lon + 1) + (j + 1),
                )
            )
            tris.append(
                (
                    i * (lon + 1) + j,
                    (i + 1) * (lon + 1) + (j + 1),
                    i * (lon + 1) + (j + 1),
                )
            )

    # Create geom and add triangles
    geom = Geom(vdata)
    triangles = GeomTriangles(Geom.UH_static)
    for tri in tris:
        triangles.add_vertices(*tri)
    geom.add_primitive(triangles)
    node = GeomNode("sphere")
    node.add_geom(geom)
    return node


os.chdir(os.path.dirname(__file__))


def extract_shader_inputs(shader_code):
    inputs = []
    lines = shader_code.split("\n")
    for line in lines:
        if line.startswith("uniform float"):
            input_line = line.split("uniform float")[1]
            input_name = input_line.split(";")[0].strip()
            inputs.append(input_name)
    return inputs


class ShaderViewer(ShowBase):
    def __init__(self, shader_file: str):
        loadPrcFileData(
            "",
            "gl-coordinate-system default\nwin-size 800 600\ngl-debug true\n",
        )
        if sys.platform == "darwin":
            loadPrcFileData("", "gl-version 3 3\n")
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.4, 0.4, 0.4, 1)
        self.setFrameRateMeter(True)
        self.accept("q", self.destroy)
        self.render.setShaderAuto()
        self.shader_file = shader_file
        self.buildGui()

    def buildGui(self):
        self.toggleModeList = DirectOptionMenu(
            parent=self.aspect2d,
            text="Toggle Mode",
            scale=0.1,
            pos=(-0.7, 0, 0.85),
            items=["3d Object", "World", "Render Buffer"],
            initialitem=0,
            command=self.toggleMode,
        )

    def toggleMode(self, mode):
        if mode == "3d Object":
            self.world.clearShader()
            self.renderCardNp.clearShader()
            self.renderCardNp.setColor(0, 0, 0, 0)
            self.model.setShader(self.shader)
        elif mode == "World":
            self.world.setShader(self.shader)
            self.renderCardNp.clearShader()
            self.renderCardNp.setColor(0, 0, 0, 0)
            self.model.clearShader()
        elif mode == "Render Buffer":
            self.world.clearShader()
            self.renderCardNp.setShader(self.shader)
            self.renderCardNp.setColor(1, 1, 1, 1)
            self.model.clearShader()

    def load_shader(self):
        self.shader = Shader.load(
            Shader.SL_GLSL,
            vertex=(
                self.shader_file if self.shader_file.endswith(".vert") else "VERT.vert"
            ),
            fragment=(
                self.shader_file if self.shader_file.endswith(".frag") else "FRAG.frag"
            ),
        )
        self.model = self.loader.loadModel("../models/control1.bam")
        self.model.reparentTo(self.render)
        self.model.setShader(self.shader)
        self.model.setTransparency(TransparencyAttrib.MAlpha)
        self.camera.setPos(10, 10, 10)
        self.camera.lookAt(self.model)
        self.shaderInputControls = []
        self.renderCard = CardMaker("renderCard")
        self.renderCard.setFrameFullscreenQuad()
        self.renderCardNp = self.render2d.attachNewNode(self.renderCard.generate())
        self.renderCardNp.setColor(0, 0, 0, 0)
        self.renderCardNp.setTransparency(TransparencyAttrib.MAlpha)
        self.world = self.render.attachNewNode(Sphere(10, 10, 10))
        self.world.setScale(-100)
        for input_name in extract_shader_inputs(open(self.shader_file).read()):
            self.addInputToggle(input_name)
        self.taskMgr.add(self.update, "update")

    def update(self, task):
        self.model.setShaderInput("Frame", task.frame)
        self.renderCardNp.setShaderInput("Frame", task.frame)
        self.world.setShaderInput("Frame", task.frame)
        for inputButton, input_name in self.shaderInputControls:
            self.model.setShaderInput(input_name, inputButton["value"])
            self.renderCardNp.setShaderInput(input_name, inputButton["value"])
            self.world.setShaderInput(input_name, inputButton["value"])
        return task.cont

    def addInputToggle(self, input_name):
        inputButton = DirectSlider(
            parent=self.aspect2d,
            text=input_name,
            range=(0, 1),
            pos=(-0.7, 0, 0.1 * len(self.shaderInputControls) - 0.8),
            value=0.5,
            scale=0.6,
            text_scale=0.15,
        )
        self.shaderInputControls.append([inputButton, input_name])
        shader = Shader.load(
            Shader.SL_GLSL,
            vertex=(
                self.shader_file if self.shader_file.endswith(".vert") else "VERT.vert"
            ),
            fragment=(
                self.shader_file if self.shader_file.endswith(".frag") else "FRAG.frag"
            ),
        )
        self.model.setShader(shader)

    def render_loop(self):
        self.load_shader()
        while True:
            self.run()
        Thread(
            target=self.run,
            daemon=True,
        ).start()


class VIEWER:
    def __init__(self):
        self.window = Tk()
        self.window.title("Output Viewer")
        self.window.geometry("900x500")
        self.window.configure(bg="#000000")
        self.emulatedTerminal = Text(
            self.window,
            bg="#000000",
            fg="white",
            font=("Arial", 12),
            width=100,
            height=30,
            state=DISABLED,
        )
        self.emulatedTerminal.pack(pady=10)

    def print(self, text):
        self.emulatedTerminal.config(state=NORMAL)
        self.emulatedTerminal.insert(END, text + "\n")
        self.emulatedTerminal.config(state=DISABLED)
        self.emulatedTerminal.see(END)
        self.window.update()


class DUMMYVIEWER:
    def print(self, text):
        print(text)


class MERGER:
    def __init__(
        self,
        shader_files: list,
        shaderType: str,
        mixOperation: str,
        viewer: VIEWER,
    ):
        self.viewer = viewer
        self.SHADERFILELIST = shader_files
        self.SHADEROPENLIST = []
        self.SHADERDATALIST: list[dict] = [
            {
                "VERSION": "",
                "INCLUDES": [],
                "VARYINGS": [],
                "INPUTS": [],
                "OUTPUTS": [],
                "FUNCTIONS": [],
                "MAINFUNCDATA": "",
            }
            for _ in range(len(shader_files))
        ]
        self.MERGINGSHADERLIST = {
            "VERSION": [],
            "INCLUDES": [],
            "VARYINGS": [],
            "INPUTS": [],
            "OUTPUTS": [],
            "FUNCTIONS": [],
            "MAINFUNCDATA": [],
        }
        self.MAPPINGS = {
            "VARIABLES": [
                "uniform",
                "attribute",
                "varying",
                "struct",
                "const",
            ],
            "DECLARATIONS": [
                "int",
                "float",
                "vec2",
                "vec3",
                "vec4",
                "mat2",
                "mat3",
                "mat4",
            ],
        }
        self.SHADERTYPE = shaderType
        self.MIXOPERATION = mixOperation
        self.viewer.print(
            f"Shader Data Mem: {len(str(self.SHADERTYPE))}b | Shader File Index Mem: {len(str(self.SHADERFILELIST))}b"
        )

    def readSection(self, section_start, section_end, shader_code, keepEnds=False):
        self.viewer.print(f"Parsing shader section: {section_start} to {section_end}")
        section = []
        in_section = False
        for line in shader_code.split("\n"):
            if section_start in line:
                in_section = True
            if in_section:
                section.append(line)
            if section_end in line and in_section:
                section.append(line)
                break
        return "\n".join(section[1:-2]) if not keepEnds else "\n".join(section[:-1])

    def merge(self):
        self.viewer.print("Merging shader files...")
        for shader in self.SHADERFILELIST:
            with open(shader, "r") as file:
                shader_code = file.read()
                self.SHADEROPENLIST.append(shader_code)

        self.viewer.print(
            f"Shader files opened successfully. Mem updated to {len(str(self.SHADEROPENLIST))}b"
        )
        self.viewer.print("Parsing shader files...")

        for index, shader in enumerate(self.SHADEROPENLIST):
            self.viewer.print(
                f"Parsing shader file {index + 1}/{len(self.SHADERFILELIST)} - {len(str(self.SHADERFILELIST[index]))}b"
            )
            lines = shader.split("\n")
            self.SHADERDATALIST[index]["VERSION"] = lines[0]
            self.viewer.print(
                f"Found Shader version: {self.SHADERDATALIST[index]['VERSION']}"
            )
            self.SHADERDATALIST[index]["VARYINGS"] = [
                line
                for line in lines
                for check in self.MAPPINGS["VARIABLES"]
                if check in line
                and not "{" in line
                and not line.startswith("   ")
                and not line.startswith("\t")
                and not line.startswith("in ")
                and not line.startswith("out ")
            ]
            self.viewer.print(
                f"Found Shader Varyings: {self.SHADERDATALIST[index]['VARYINGS']}"
            )
            self.SHADERDATALIST[index]["INPUTS"] = [
                line for line in lines if line.startswith("in ")
            ]
            self.viewer.print(
                f"Found Shader Inputs: {self.SHADERDATALIST[index]['INPUTS']}"
            )
            self.SHADERDATALIST[index]["OUTPUTS"] = [
                line for line in lines if line.startswith("out ")
            ]
            self.viewer.print(
                f"Found Shader Outputs: {self.SHADERDATALIST[index]['OUTPUTS']}"
            )
            self.SHADERDATALIST[index]["MAINFUNCDATA"] = self.readSection(
                "void main", "}", shader
            )
            self.viewer.print(
                f"Found Shader Main Function Data: {self.SHADERDATALIST[index]['MAINFUNCDATA']}"
            )
            splitShader = shader.split("\n")
            for line in splitShader:
                if "{" in line and not "void main" in line:
                    self.SHADERDATALIST[index]["FUNCTIONS"].append(
                        self.readSection(line, "}", shader, keepEnds=True)
                    )
            self.viewer.print(
                f"Found Shader Functions: {self.SHADERDATALIST[index]['FUNCTIONS']}"
            )
            if index > 0:
                self.viewer.print(
                    f"Adding mix operation to shader file {index + 1}/{len(self.SHADERFILELIST)}"
                )
                self.SHADERDATALIST[index]["MAINFUNCDATA"] = (
                    self.SHADERDATALIST[index]["MAINFUNCDATA"]
                    .replace("p3d_FragColor ", "p3d_FragColor " + self.MIXOPERATION)
                    .replace("gl_Position ", "gl_Position " + self.MIXOPERATION)
                    .replace("p3d_FragColor=", "p3d_FragColor " + self.MIXOPERATION)
                    .replace("gl_Position=", "gl_Position " + self.MIXOPERATION)
                )
                self.SHADERDATALIST[index]["MAINFUNCDATA"] = (
                    self.SHADERDATALIST[index]["MAINFUNCDATA"] + "\n\n"
                )
                self.viewer.print(
                    f"Packed mix operation to shader file {index + 1}/{len(self.SHADERFILELIST)}"
                )

        for index, shader in enumerate(self.SHADERDATALIST):
            self.MERGINGSHADERLIST["VERSION"].append(shader["VERSION"])
            self.MERGINGSHADERLIST["VARYINGS"].extend(shader["VARYINGS"])
            self.MERGINGSHADERLIST["INPUTS"].extend(shader["INPUTS"])
            self.MERGINGSHADERLIST["OUTPUTS"].extend(shader["OUTPUTS"])
            self.MERGINGSHADERLIST["MAINFUNCDATA"].append(
                "   // Start of shader fragment"
            )
            self.MERGINGSHADERLIST["MAINFUNCDATA"].append(shader["MAINFUNCDATA"])
            self.MERGINGSHADERLIST["MAINFUNCDATA"].append(
                "   // End of shader fragment\n\n"
            )
            self.MERGINGSHADERLIST["FUNCTIONS"].extend(shader["FUNCTIONS"])

        self.viewer.print(
            f"Shader data extracted successfully. Mem updated to {len(str(self.MERGINGSHADERLIST))}b"
        )

        self.viewer.print("Removing duplicates from shader data...")

        self.MERGINGSHADERLIST["VERSION"] = self.removeDuplicates(
            self.MERGINGSHADERLIST["VERSION"]
        )
        self.MERGINGSHADERLIST["VARYINGS"] = self.removeDuplicates(
            self.MERGINGSHADERLIST["VARYINGS"]
        )
        self.MERGINGSHADERLIST["INPUTS"] = self.removeDuplicates(
            self.MERGINGSHADERLIST["INPUTS"]
        )
        self.MERGINGSHADERLIST["OUTPUTS"] = self.removeDuplicates(
            self.MERGINGSHADERLIST["OUTPUTS"]
        )
        self.viewer.print(
            f"Duplicates removed successfully. Mem updated to {len(str(self.MERGINGSHADERLIST))}b"
        )
        outFileName = (
            " - ".join(
                ".".join(shader.split("/")[-1].split(".")[:-1])
                for shader in self.SHADERFILELIST
            )
            + self.SHADERTYPE
        )
        self.viewer.print(
            f"Output file name: {outFileName} | Shader Type: {self.SHADERTYPE}"
        )
        finishedData = (
            "\n".join(self.MERGINGSHADERLIST["VERSION"])
            + "\n"
            + "\n".join(self.MERGINGSHADERLIST["INCLUDES"])
            + "\n"
            + "\n".join(self.MERGINGSHADERLIST["VARYINGS"])
            + "\n"
            + "\n".join(self.MERGINGSHADERLIST["INPUTS"])
            + "\n"
            + "\n".join(self.MERGINGSHADERLIST["OUTPUTS"])
            + "\n"
            + "\n".join(self.MERGINGSHADERLIST["FUNCTIONS"])
            + "\n"
            + "\nvoid main() {\n"
            + self.renameDuplicateVariables(
                "\n".join(self.MERGINGSHADERLIST["MAINFUNCDATA"])
            )
            + "\n}"
        )
        finishedData = self.removeEmptyLines(finishedData)
        self.viewer.print(f"Finished shader data:\n{finishedData}\n\n")
        self.viewer.print("Shader data merged successfully.")
        with open(outFileName, "w") as file:
            file.write(finishedData)
        return outFileName

    def removeDuplicates(self, lst):
        seen = set()
        lst = [x for x in lst if not (x in seen or seen.add(x))]
        return lst

    def removeEmptyLines(self, _str: str):
        return _str

    def renameDuplicateVariables(self, funcData: str):
        _funcData = []
        randVars = []
        self.viewer.print("Renaming duplicate variables...")
        for block in funcData.split("   // Start of shader fragment"):
            self.viewer.print(
                f"Searching for variables in block: {block.split('// Start of shader fragment')[0]}"
            )
            for line in block.split("\n"):
                self.viewer.print(f"Checking line: {line}")
                for check in self.MAPPINGS["DECLARATIONS"]:
                    if " " + check + " " in line:
                        self.viewer.print(
                            f"Found variable: {line.split(check)[1].split('=')[0].strip()}"
                        )
                        variableName = line.split(check)[1].split("=")[0].strip()
                        randVal = random.randint(0, 10000)
                        if randVal in randVars:
                            while randVal in randVars:
                                randVal = random.randint(0, 10000)
                        randVars.append(randVal)
                        newVariableName = variableName + "_" + str(randVal)
                        block = block.replace(variableName, newVariableName)
            _funcData.append(block)
        return "\n".join(_funcData)


class Main:
    def __init__(self):
        self.window = Tk()
        self.window.title("Shader File Merger")
        self.window.geometry("800x600")
        self.window.configure(bg="#000000")
        self.fileType = ""
        self.SHADERFILELIST = []

    def get_file_path(self):
        shader_type = self.shader_type_var.get()
        if shader_type == "Vertex Shader":
            filetypes = [("Vertex Shader Files", "*.vert")]
            self.fileType = ".vert"
        elif shader_type == "Fragment Shader":
            filetypes = [("Fragment Shader Files", "*.frag")]
            self.fileType = ".frag"
        else:
            messagebox.showerror("Error", "Please select a shader type.")
            return None

        file_path = filedialog.askopenfilename(
            title="Select Shader File",
            filetypes=filetypes,
        )
        if not file_path:
            return None
        self.viewer.print(f"Added shader file: {file_path}")
        return file_path

    def merge_shader_files(self):
        if self.mix_operation_var.get() == "Select Mix Operation":
            messagebox.showerror("Error", "Please select a mix operation.")
            return
        merger = MERGER(
            self.SHADERFILELIST,
            self.fileType,
            self.mix_operation_var.get(),
            self.viewer,
        )
        self.viewer.print(f"Merging shader files: {', '.join(self.SHADERFILELIST)}")
        outFile = merger.merge()
        messagebox.showinfo(
            "Success",
            f"Shader files merged successfully into {outFile}.",
        )
        if self.is_vscode_in_path():
            self.viewer.print("VSCode found in PATH.")
            if not hasattr(self, "open_with_code_button"):
                self.open_with_code_button = Button(
                    self.viewer_frame,
                    text="Open Last Output with Code",
                    command=lambda: os.system(f'code "{os.path.abspath(outFile)}"'),
                    bg="#2196F3",
                    fg="white",
                    font=("Arial", 14),
                    padx=10,
                    pady=5,
                )
                self.open_with_code_button.pack(side=LEFT, pady=10)
                self.launch_viewer_button = Button(
                    self.viewer_frame,
                    text="Launch Viewer",
                    command=lambda: ShaderViewer(outFile).render_loop(),
                    bg="#4CAF50",
                    fg="white",
                    font=("Arial", 14),
                    padx=10,
                    pady=5,
                )
                self.launch_viewer_button.pack(side=RIGHT, pady=10)
        else:
            self.viewer.print("VSCode not found in PATH.")
            if not hasattr(self, "open_with_notepad_button"):
                self.open_with_notepad_button = Button(
                    self.viewer_frame,
                    text="Open Last Output with Notepad",
                    command=lambda: os.system(f'notepad "{os.path.abspath(outFile)}"'),
                    bg="#2196F3",
                    fg="white",
                    font=("Arial", 14),
                    padx=10,
                    pady=5,
                )
                self.open_with_notepad_button.pack(side=LEFT, pady=10)
                self.launch_viewer_button = Button(
                    self.viewer_frame,
                    text="Launch Viewer",
                    command=lambda: ShaderViewer(outFile).render_loop(),
                    bg="#4CAF50",
                    fg="white",
                    font=("Arial", 14),
                    padx=10,
                    pady=5,
                )
                self.launch_viewer_button.pack(side=RIGHT, pady=10)

    def is_vscode_in_path(self):
        return any(
            os.access(os.path.join(path, "code"), os.X_OK)
            for path in os.environ["PATH"].split(os.pathsep)
        )

    def add_shader_file(self):
        file_path = self.get_file_path()
        if file_path:
            self.SHADERFILELIST.append(file_path)
            fileText = file_path.split("/")[-1].split(".")[:-1]
            fileType = file_path.split("/")[-1].split(".")[-1]
            with open(file_path, "r") as file:
                shader_code = file.read()
            self.shader_listbox.insert(
                END,
                f"{fileText} --> {fileType}  |  {len(shader_code.splitlines())} lines",
            )
        if len(self.SHADERFILELIST) > 1:
            if not hasattr(self, "merge_button"):
                self.merge_button = Button(
                    self.window,
                    text="Merge Shader Files",
                    command=self.merge_shader_files,
                    bg="#4CAF50",
                    fg="black",
                    font=("Arial", 14),
                    padx=10,
                    pady=5,
                )
                self.merge_button.pack(pady=20)
        self.viewer.print(
            f"Added shader file: {file_path.split('/')[-1].split('.')[0]} - {fileType}"
        )

    def remove_shader_file(self):
        selected_index = self.shader_listbox.curselection()
        if selected_index:
            self.shader_listbox.delete(selected_index)
            self.viewer.print(
                f"Removed shader file: {self.SHADERFILELIST[selected_index[0]]}"
            )
            del self.SHADERFILELIST[selected_index[0]]
        if len(self.SHADERFILELIST) <= 1:
            if hasattr(self, "merge_button"):
                self.merge_button.destroy()
                del self.merge_button

    def clear_shader_list(self, *args):
        self.shader_listbox.delete(0, END)
        self.SHADERFILELIST.clear()
        self.viewer.print("Shader list cleared.")

    def main(self):
        # Create a frame to hold the buttons
        button_frame = Frame(self.window, bg="#000000")
        button_frame.pack(pady=20)

        # Create a button to add a shader file
        self.add_shader = Button(
            button_frame,
            text="Add Shader File",
            command=self.add_shader_file,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 14),
            padx=10,
            pady=5,
        )
        self.add_shader.pack(side=LEFT, padx=10)

        # Create a button to remove the selected shader file
        self.remove_shader = Button(
            button_frame,
            text="Remove Selected Shader",
            command=self.remove_shader_file,
            bg="#F44336",
            fg="black",
            font=("Arial", 14),
            padx=10,
            pady=5,
        )
        self.remove_shader.pack(side=LEFT, padx=10)

        options_frame = Frame(self.window, bg="#000000")
        options_frame.pack(pady=20)
        # Create a dropdown menu to select the shader file type
        self.shader_type_var = StringVar(self.window)
        self.shader_type_var.set("Select Shader Type")
        self.shader_type_var.trace_add("write", self.clear_shader_list)
        self.shader_type_menu = OptionMenu(
            options_frame,
            self.shader_type_var,
            "Vertex Shader",
            "Fragment Shader",
        )
        self.shader_type_menu.pack(side=LEFT, pady=10)
        # Create a dropdown menu to select the mix operation
        self.mix_operation_var = StringVar(self.window)
        self.mix_operation_var.set("Select Mix Operation")
        self.mix_operation_menu = OptionMenu(
            options_frame,
            self.mix_operation_var,
            "*",
            "+",
            "-",
            "/",
        )
        self.mix_operation_menu.pack(side=RIGHT, pady=10)

        self.view_output_var = BooleanVar(value=True)
        self.view_output_toggle = Button(
            options_frame,
            text="View Output On",
            command=self.toggle_view_output,
            bg="#2196F3",
            fg="black",
            font=("Arial", 14),
            padx=10,
            pady=5,
        )
        self.view_output_toggle.pack(padx=10, side=LEFT)

        self.shader_listbox = Listbox(
            self.window,
            bg="#333333",
            fg="black",
            font=("Arial", 12),
            width=50,
            height=10,
        )
        self.shader_listbox.pack(pady=10)
        self.toggle_view_output()

        # Create a frame to hold the output viewer
        self.viewer_frame = Frame(self.window, bg="#000000")
        self.viewer_frame.pack(pady=10)
        # Start the main event loop
        self.window.mainloop()

    def toggle_view_output(self):
        self.viewer = VIEWER() if self.view_output_var.get() else DUMMYVIEWER()
        self.view_output_var.set(not self.view_output_var.get())


if __name__ == "__main__":
    main = Main()
    main.main()
