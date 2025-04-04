from tkinter import Tk, Entry, Frame, Text
from tkinter import *


def entryBoxEnter(text):
    entryBox.delete(0, -1)


root = Tk()
contentFrame = Frame(root)
contentFrame.pack()
outputViewer = Text(contentFrame, state="disabled")
outputViewer.pack()
entryBox = Entry(contentFrame)
entryBox.pack()
root.mainloop()
