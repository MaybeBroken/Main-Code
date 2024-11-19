from time import sleep
import server
import client
import threading


class vars:
    serverKeys = [
        ["ReactorTotalPower", 0],
        ["LeftGeneratorPowerIn", 0],
        ["RightGeneratorPowerIn", 0],
        ["LeftTransformer_1_Power", 0],
        ["RightTransformer_2_Power", 0],
        ["RightTransformer_1_Power", 0],
        ["LeftTransformer_2_Power", 0],
        ["ConnectedCard", "Shields", False, 0],
        ["ConnectedCard", "Generator", "LeftTransformer_1", False],
    ]
    jsKeys = serverKeys
    boardKeys = serverKeys


pythonServer = threading.Thread(
    target=server.startServer, daemon=True, args=[8765, vars, "py"]
).start()

jsServer = threading.Thread(
    target=server.startServer, daemon=True, args=[8766, vars, "js"]
).start()

while 1 == 1:
    client.runClient()
    sleep(0.2)
