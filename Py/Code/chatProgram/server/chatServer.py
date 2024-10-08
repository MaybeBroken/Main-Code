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

portNum = 8765

exampleMsg = {"time": 0, "usr": "MaybeBroken", "text": "test"}

devMode = False
anyAuth = True
register_reset = False
chatRooms = [
    {"roomName": "hangout", "messages": []},
    {"roomName": "spam", "messages": []},
]

accounts = {
    "MaybeBroken": "123456",
    "EthanG": "123456",
    "noAuth-(!!)": "",
}

loadPrcFile("settings.prc")


def parseMessage(msg: str):
    parseMsg: dict = js.decoder.JSONDecoder().decode(s=msg)
    for chatRoom in chatRooms:
        if chatRoom["roomName"] == parseMsg["roomName"]:
            chatRoom["messages"].append(
                {
                    "time": f"{t.localtime()[1]}/{t.localtime()[2]}/{t.localtime()[0]} at {t.localtime()[3]}:{t.localtime()[4]}:{t.localtime()[5]}",
                    "usr": parseMsg["usr"],
                    "text": parseMsg["text"],
                }
            )


def newRoom(msg):
    global register_reset
    chatRooms.append({"roomName": msg, "messages": []})
    register_reset = True


def delRoom(roomName):
    global register_reset
    for room in chatRooms:
        if room["roomName"] == roomName:
            chatRooms.remove(room)
    register_reset = True


def controlLoop():
    authMGR = False
    while True:
        _in = input()
        if _in == "help":
            print(
                f"\n{'='*20}\nSERVER COMMANDS:\nnewRoom: creates a new room\ndelRoom: deletes a room\nauthMgr: runs the authMgr\n{'='*20}"
            )
        elif _in == "newRoom":
            newRoom(input("new room name: "))
        elif _in == "delRoom":
            print([room["roomName"] for room in chatRooms])
            delRoom(input("room to delete: "))
        elif _in == "authMgr":
            authMGR = True
            print(f"ANYAUTH (!): {anyAuth}")
            while authMGR:
                _in = input("| ")
                if _in == "help":
                    print(
                        "| viewAccounts: show a list of all registered users\n| exit: exits the authMgr"
                    )
                if _in == "exit":
                    print("| closing...\n^")
                    authMGR = False
                if _in == "viewAccounts":
                    print(f"{'='*20}\n|")
                    for account in accounts:
                        print(f"| |-->{account}, {accounts[account]}")


async def _echo(websocket):
    try:
        msg = await websocket.recv()
        encoder = js.encoder.JSONEncoder()
        if msg == "!!#update":
            await websocket.send(encoder.encode(o=chatRooms))
        elif msg[0] == "+" and msg[1] == "@":
            if anyAuth:
                msg = msg.splitlines()
                await websocket.send("!!#authDisabled")
            else:
                try:
                    msg = msg.splitlines()
                    try:
                        i = accounts[msg[1]]
                        if accounts[msg[1]] == msg[2]:
                            await websocket.send("!!#authSuccess")
                        else:
                            await websocket.send("!!#wrongPassword")
                    except:
                        await websocket.send("!!#wrongUsrname")
                except:
                    print(f"STUPID SERVER BROKE:\nmsg-->{msg}\naccounts-->{accounts}")
                    await websocket.send("!!#internalErr")
        else:
            parseMessage(msg)
            await websocket.send(encoder.encode(o=chatRooms))
    except:
        ...


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()


def startLocaltunnel():
    system(command=f"lt -p {portNum} -s maybebroken")
    ...


def saveServer():
    while True:
        with open("./backup.dat", "wt") as backup:
            backup.write(js.encoder.JSONEncoder().encode(o=chatRooms))
        t.sleep(3)


if not devMode:
    Thread(target=startLocaltunnel).start()
with open("./backup.dat", "rt") as backup:
    chatRooms = js.decoder.JSONDecoder().decode(s=backup.read())
Thread(target=saveServer).start()
Thread(target=controlLoop).start()
Thread(target=asyncio.run, args=[_buildServe()]).start()


class chatApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setupMenuGui()

    def update(self, task):
        global chatRooms, roomName
        for room in chatRooms:
            if room["roomName"] == roomName:
                messages = ""
                for message in room["messages"]:
                    messages += f"| {message['time']} | {message['usr']}\n|  {message['text']}\n\n"
                self.currentRoomFrame[1]["text"] = messages
                self.currentRoomFrame[1].setPos(
                    -0.5, 0.07 * len(messages.splitlines()) + self.scrollAmount
                )
        self.updateRooms()
        return task.cont

    def moveTextUp(self):
        self.scrollAmount -= 0.07

    def moveTextDown(self):
        self.scrollAmount += 0.07

    def updateRooms(self):
        global register_reset
        if register_reset:
            self.guiFrame.destroy()
            self.buildMainGUI()
            register_reset = False

    def changeRoom(self, room):
        self.currentRoomFrame[1].hide()
        self.currentRoomFrame = [item for item in self.roomsList if room in item[0]]
        self.currentRoomFrame = self.currentRoomFrame[0][1]
        global roomName
        roomName = room
        self.currentRoomFrame[1].show()

    def setupMenuGui(self):
        self.set_background_color(0.2, 0.2, 0.3, 1)
        self.startService()

    def newRoomGUI(self):
        self.newRoomTextBar = DirectEntry(
            parent=self.guiFrame,
            text="",
            scale=0.06,
            command=newRoom,
            numLines=1,
            pos=(-0.6, 0, -0.8),
            cursorKeys=1,
            overflow=0,
        )

    def buildMainGUI(self):
        self.guiFrame = DirectFrame(parent=self.aspect2d)
        self.roomFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, -0.65, -1, 1),
            frameColor=(0.15, 0.15, 0.2, 1),
        )
        self.lobbyFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.64, 1, -1, 1),
            pos=(0, -1, 0),
            frameColor=(0.3, 0.3, 0.3, 1),
        )
        self.newRoom = DirectButton(
            parent=self.roomFrame,
            pos=(-0.82, 1, -0.8),
            scale=0.06,
            text="New Room",
            command=self.newRoomGUI,
        )
        self.currentRoomFrame = None
        posIndex = 0
        defaultDistance = 0.12
        self.roomsList = []

        for room in chatRooms:
            name = room["roomName"]
            newRoomButton = DirectButton(
                parent=self.roomFrame,
                pos=(-0.85, 1, 0.9 - (defaultDistance * posIndex)),
                scale=0.06,
                text=name,
                command=self.changeRoom,
                extraArgs=[name],
            )
            delRoomButton = DirectButton(
                parent=self.roomFrame,
                pos=(-1.05, 1, 0.9 - (defaultDistance * posIndex)),
                scale=0.06,
                text="del",
                command=delRoom,
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
            self.roomsList.append([name, [newRoomButton, messageText, delRoomButton]])
            posIndex += 1
        self.currentRoomFrame = self.roomsList[0][1]
        self.currentRoomFrame[1].show()
        global roomName
        roomName = self.roomsList[0][0]
        self.scrollAmount = 0
        self.accept("wheel_up", self.moveTextUp)
        self.accept("wheel_down", self.moveTextDown)

    def startService(self):
        self.buildMainGUI()
        self.taskMgr.add(self.update, "update")


chatapp = chatApp()
chatapp.run()
