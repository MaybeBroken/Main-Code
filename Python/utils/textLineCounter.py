import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("../../..")

totalLines = 0
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".py"):
            try:
                with open(os.path.join(root, file), "r") as f:
                    curLines = len(f.readlines())
                    totalLines += curLines
                    print(f"{file}: {curLines} lines")
            except:
                print(f"Error reading {os.path.join(root, file)}")

print(f"Total lines: {totalLines}")
