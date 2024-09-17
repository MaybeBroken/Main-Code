from time import sleep


class fade:
    def fadeOutGuiElement_ThreadedOnly(
        element, timeToFade, execBeforeOrAfter, target, args=()
    ):
        if execBeforeOrAfter == "Before":
            target(*args)

        for i in range(timeToFade):
            val = 1 - (1 / timeToFade) * (i + 1)
            try:
                element.setAlphaScale(val)
            except:
                None
            sleep(0.01)
        element.hide()
        if execBeforeOrAfter == "After":
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
            sleep(0.01)
        if execBeforeOrAfter == "After":
            target(*args)
