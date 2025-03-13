import os
from tkinter import filedialog, Tk
from tkinter import *

os.chdir(os.path.dirname(__file__))


class Main:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("800x600")
        self.root.title("DMG Cracker")
        self.root.configure(bg="black")
        self.buildGui()

    def openDmg(self, file_path=None, out_path=None):
        if not file_path:
            print("No file selected.")
        if not out_path:
            out_path = os.path.dirname(file_path)
            print("Output directory not selected, defaulting to:", out_path)
        os.system(f".{os.path.sep}7zz x -o{out_path} {file_path}")

    def buildGui(self):
        self.label = Label(
            self.root, text="Add DMG files to crack:", bg="black", fg="white"
        )
        self.label.pack(pady=20)

        self.top_frame = Frame(self.root, bg="black")
        self.top_frame.pack(pady=10)
        self.select_button = Button(
            self.top_frame,
            text="Add DMG File",
            command=self.select_file,
            bg="black",
            fg="black",
        )
        self.select_button.pack(side=LEFT, pady=10)

        self.delete_button = Button(
            self.top_frame,
            text="Delete Selected File",
            command=lambda: self.files_list.delete(ANCHOR),
            bg="black",
            fg="black",
        )
        self.delete_button.pack(side=RIGHT, padx=10)

        self.files_list = Listbox(self.root, width=50, height=10)
        self.files_list.pack(pady=10)

        self.output_button = Button(
            self.root,
            text="Select Output Directory",
            command=self.select_output,
            bg="black",
            fg="black",
        )
        self.output_button.pack(pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select DMG file",
            filetypes=[("DMG files", "*.dmg")],
        )
        if file_path:
            self.files_list.insert(END, file_path)
            self.openDmg(file_path)
        else:
            print("No file selected.")

    def select_output(self):
        out_path = filedialog.askdirectory(
            title="Select Output Directory",
        )
        if out_path:
            self.openDmg(out_path=out_path)
        else:
            print("No output directory selected.")


Main().root.mainloop()
