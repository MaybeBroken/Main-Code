from os import system

try:
    import websockets
except:
    system(f"python3 -m pip install websockets")
import time as t

try:
    import json as js
except:
    system(f"python3 -m pip install json")
import asyncio

try:
    from panda3d.core import *
except:
    system(f"python3 -m pip install panda3d")
from panda3d.core import TextNode, loadPrcFile
from direct.showbase.ShowBase import ShowBase
from direct.stdpy.threading import Thread
from direct.gui.DirectGui import *

devMode = False

serverContents = []
portNum = 8765
if not devMode:
    ip = "wss://maybebroken.loca.lt"
else:
    ip = "ws://localhost:8765"
usrName = None
roomName = None
usrNameMenu = None
passwdMenu = None
auth = False
appGuiFrame = None
loadPrcFile("settings.prc")


async def _send_recieve(data):
    async with websockets.connect(ip) as websocket:
        encoder = js.encoder.JSONEncoder()
        if data == "!!#update":
            await websocket.send("!!#update")
            global serverContents
            serverContents = js.decoder.JSONDecoder().decode(s=await websocket.recv())
        elif data == "!!#login":
            global usrName, usrNameMenu, passwdMenu, auth
            await websocket.send(f"+@\n{usrNameMenu}\n{passwdMenu}")
            retVal = await websocket.recv()
            if retVal == "!!#wrongPassword":
                notify("incorrect password!")
            elif retVal == "!!#wrongUsrname":
                notify("incorrect username/password!")
            elif retVal == "!!#internalErr":
                notify("server error")
            elif retVal == "!!#authSuccess":
                usrName = usrNameMenu
                auth = True
            elif retVal == "!!#authDisabled":
                notify(f'AUTH disabled, using username "{usrNameMenu  + "-(!)"}"')
                usrName = usrNameMenu + "-(!)"
                auth = True

        else:
            await websocket.send(
                encoder.encode(o={"usr": usrName, "text": data, "roomName": roomName})
            )


def runClient(data):
    try:
        asyncio.run(_send_recieve(data))
    except:
        global serverContents, auth
        if not auth:
            notify("network err")
        else:
            serverContents = []
            for i in range(5):
                try:
                    asyncio.run(_send_recieve(data))
                    break
                except:
                    ...


def update():
    while True:
        try:
            runClient("!!#update")
        except:
            ...
        t.sleep(0.2)


class chatApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setupMenuGui()

    def update(self, task):
        global serverContents, roomName
        for room in serverContents:
            if room["roomName"] == roomName:
                messages = ""
                for message in room["messages"]:
                    messages += f"| {message['time']} | {message['usr']}\n|  {message['text']}\n\n"
                self.currentRoomFrame[1]["text"] = messages
                self.currentRoomFrame[1].setPos(
                    -0.5, 0.07 * len(messages.splitlines()) + self.scrollAmount
                )
        if len(serverContents) != self.len_last:
            self.refreshGui()
            self.len_last = len(serverContents)
        return task.cont

    def moveTextUp(self):
        self.scrollAmount -= 0.07

    def moveTextDown(self):
        self.scrollAmount += 0.07

    def changeRoom(self, room):
        self.currentRoomFrame[1].hide()
        self.currentRoomFrame = [item for item in self.roomsList if room in item[0]]
        self.currentRoomFrame = self.currentRoomFrame[0][1]
        global roomName
        roomName = room
        self.currentRoomFrame[1].show()

    def setupMenuGui(self):
        self.set_background_color(0.2, 0.2, 0.3, 1)
        self.guiFrame = DirectFrame(
            parent=self.aspect2d,
            frameSize=(-1.25, 1.25, -1, 1),
            frameColor=(0.1, 0.1, 0.1, 1),
        )

        def setPassW(passW):
            global passwdMenu
            passwdMenu = passW

        def setUsrName(usrN):
            global usrNameMenu
            usrNameMenu = usrN

        self.usrNameBox = DirectEntry(
            parent=self.guiFrame,
            text="",
            scale=0.1,
            command=setUsrName,
            initialText="",
            numLines=1,
            pos=(-1, 0, 0.25),
        )

        self.passwdBox = DirectEntry(
            parent=self.guiFrame,
            text="",
            scale=0.1,
            command=setPassW,
            initialText="",
            numLines=1,
            obscured=1,
            pos=(-1, 0, 0.0),
        )

        self.startButton = DirectButton(
            parent=self.guiFrame,
            text="login",
            color=(1, 1, 1, 1),
            scale=0.15,
            pos=(-0.845, 0, -0.25),
            command=runClient,
            extraArgs=["!!#login"],
        )
        self.taskMgr.add(self.checkAuthTask, "checkAuthState")

    def clearText(self):
        self.textBar.destroy()
        self.textBar = DirectEntry(
            parent=self.aspect2d,
            text="",
            scale=0.1,
            command=self.sendMessage,
            numLines=1,
            pos=(-0.5, 0, -0.9),
            cursorKeys=1,
            focus=1,
            overflow=1,
        )

    def sendMessage(self, message):
        Thread(target=runClient, args=[f"--> {message}"]).start()
        self.clearText()

    def refreshGui(self):
        self.buildMainGUI()

    def buildMainGUI(self):
        self.guiFrame.destroy()
        self.guiFrame = DirectFrame(parent=self.aspect2d)
        self.roomFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, -0.65, -1, 1),
            frameColor=(0.15, 0.15, 0.2, 1),
        )
        self.lobbyFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.64, 1, -1, 1),
            frameColor=(0.3, 0.3, 0.3, 1),
        )
        self.currentRoomFrame = None
        posIndex = 0
        defaultDistance = 0.12
        self.roomsList = []

        self.textBar = DirectEntry(
            parent=self.aspect2d,
            text="",
            scale=0.1,
            command=self.sendMessage,
            numLines=1,
            pos=(-0.5, 0, -0.9),
            cursorKeys=1,
            overflow=1,
        )
        runClient("!!#update")
        self.len_last = len(serverContents)
        for room in serverContents:
            name = room["roomName"]
            newRoomButton = DirectButton(
                parent=self.roomFrame,
                pos=(-0.85, 1, 0.9 - (defaultDistance * posIndex)),
                scale=0.06,
                text=name,
                command=self.changeRoom,
                extraArgs=[name],
            )

            messages = ""
            for message in room["messages"]:
                messages += f"| {message['usr']}\n|  --> {message['text']}\n\n"
            messageText = OnscreenText(
                parent=self.lobbyFrame,
                text=messages,
                pos=(-0.5, 0.07 * len(messages.splitlines())),
                scale=0.07,
                align=TextNode.ALeft,
                wordwrap=20,
            )
            messageText.hide()
            self.roomsList.append([name, [newRoomButton, messageText]])
            posIndex += 1
        self.currentRoomFrame = self.roomsList[0][1]
        self.currentRoomFrame[1].show()
        global roomName
        roomName = self.roomsList[0][0]
        self.accept("wheel_up", self.moveTextUp)
        self.accept("wheel_down", self.moveTextDown)
        self.scrollAmount = 0

    def startService(self):
        Thread(target=update).start()
        self.buildMainGUI()
        self.taskMgr.add(self.update, "update")

    def checkAuthTask(self, task):
        if auth:
            self.startService()
        else:
            return task.cont


def fadeOutGuiElement(
    element,
    timeToFade=100,
    daemon=True,
    execBeforeOrAfter: None = None,
    target: None = None,
    args=(),
):
    def _internalThread():
        if execBeforeOrAfter == "Before":
            target(*args)

        for i in range(timeToFade):
            val = 1 - (1 / timeToFade) * (i + 1)
            try:
                element.setAlphaScale(val)
            except:
                None
            t.sleep(0.01)
        element.hide()
        if execBeforeOrAfter == "After":
            target(*args)

    return Thread(target=_internalThread, daemon=daemon).start()


def fadeInGuiElement(
    element,
    timeToFade=100,
    daemon=True,
    execBeforeOrAfter: None = None,
    target: None = None,
    args=(),
):
    def _internalThread():
        if execBeforeOrAfter == "Before":
            target(*args)

        element.show()
        for i in range(timeToFade):
            val = abs(0 - (1 / timeToFade) * (i + 1))
            element.setAlphaScale(val)
            t.sleep(0.01)
        if execBeforeOrAfter == "After":
            target(*args)

    return Thread(target=_internalThread, daemon=daemon).start()


def notify(message: str, pos=(0.8, 0, -0.5), scale=0.75):
    global appGuiFrame

    def fade(none):
        timeToFade = 20
        newMessage.setTransparency(True)

        def _internalThread():
            for i in range(timeToFade):
                val = 1 - (1 / timeToFade) * (i + 1)
                newMessage.setAlphaScale(val)
                t.sleep(0.01)
            newMessage.destroy()
             #newMessage.cleanup()

        Thread(target=_internalThread).start()

    newMessage = OkDialog(
        parent=appGuiFrame,
        text=message,
        pos=pos,
        scale=scale,
        frameColor=(0.5, 0.5, 0.5, 0.25),
        text_fg=(1, 1, 1, 1),
        command=fade,
        pad=[0.02, 0.02, 0.02, 0.02],
    )
    return newMessage


chatapp = chatApp()
chatapp.run()
