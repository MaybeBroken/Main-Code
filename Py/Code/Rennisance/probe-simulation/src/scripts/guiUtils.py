from time import sleep

TaskMgr = None
registeredNodes = []
globalClock = None


taskload = True
class fade:
    def fadeOutGuiElement_ThreadedOnly(
        element, timeToFade, execBeforeOrAfter:None = None, target:None = None, args=()
    ):
        if execBeforeOrAfter == "before":
            target(*args)

        for i in range(timeToFade):
            val = 1 - (1 / timeToFade) * (i + 1)
            element.setAlphaScale(val)
            sleep(0.01)
        element.hide()
        if execBeforeOrAfter == "after":
            target(*args)

    def fadeInGuiElement_ThreadedOnly(
        element, timeToFade, execBeforeOrAfter:None = None, target:None = None, args=()
    ):
        if execBeforeOrAfter == "Before":
            target(*args)

        element.show()
        for i in range(timeToFade):
            val = abs(0 - (1 / timeToFade) * (i + 1))
            element.setAlphaScale(val)
            sleep(0.01)
        if execBeforeOrAfter == "After":
            target(*args)
