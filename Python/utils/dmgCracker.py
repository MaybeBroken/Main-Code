import os
from PyQt5.QtWidgets import QApplication, QFileDialog
import sys

os.chdir(os.path.dirname(__file__))

app = QApplication(sys.argv)
file_path, _ = QFileDialog.getOpenFileName(
    None,
    "Select a DMG file",
    "",
    "DMG files (*.dmg);;All files (*)",
)
if not file_path:
    print("No file selected.")
    sys.exit(1)

out_path = os.path.splitext(file_path)[0]
os.system(f"./7zz x -o{out_path} {file_path}")
