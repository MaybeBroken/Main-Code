from time import sleep

TaskMgr = None
registeredNodes = []
globalClock = None


def _fadeOutNode(task):
    for id in registeredNodes:
        dt = globalClock.getDt()
        if id[1] > 0:
            id[1] -= 1 / (dt * 10)
            if id[2] != None:
                id[0].getParent().setAlphaScale(id[1])
                id[0].setAlphaScale(id[1])
            else:
                id[0].setAlphaScale(id[1])
        else:
            if id[2] != None:
                try:
                    id[0].hide()
                    id[2]["exec"](*id[2]["args"])
                except:
                    print(id)
            else:
                id[0].hide()
            registeredNodes.remove(id)
    return task.cont

taskload = True
class fade:
    def fadeOutNode(node, time, exec: dict = None):
        global taskload
        registeredNodes.append([node, time, exec])
        if taskload:
            TaskMgr.add(_fadeOutNode, priority=-1)
            taskload = False

    def fadeOutGuiElement_ThreadedOnly(
        element, timeToFade, execBeforeOrAfter, target, args=()
    ):
        if execBeforeOrAfter == "before":
            target(*args)

        for i in range(timeToFade):
            val = 1 - (1 / timeToFade) * (i + 1)
            try:
                element.setAlphaScale(val)
            except:
                None
        print("17")
        element.hide()
        print("19")
        if execBeforeOrAfter == "after":
            target(*args)

    def fadeInGuiElement_ThreadedOnly(
        element, timeToFade, execBeforeOrAfter, target, args=()
    ):
        if execBeforeOrAfter == "Before":
            target(*args)

        element.show()
        for i in range(timeToFade):
            val = abs(0 - (1 / timeToFade) * (i + 1))
            element.setAlphaScale(val)
        if execBeforeOrAfter == "After":
            target(*args)
