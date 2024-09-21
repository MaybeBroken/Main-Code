from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter
from src.scripts.weapons import lasers
from time import monotonic


def behaviors(ai):
    AIbehaviors = ai.getAiBehaviors()

    class internals:
        FLEE = AIbehaviors.flee
        PURSUE = AIbehaviors.pursue
        PAUSE = AIbehaviors.pauseAi
        SETMASS = AIbehaviors.setMass
        GETMASS = AIbehaviors.getMass

    return internals


lastFire = monotonic()


def droneFire(target, origin):
    if abs(monotonic() - lastFire) > 3:
        lasers.fire(origin=origin, target=target, destroy=False)
        lastFire = monotonic()


def removeChar(ai, ship):
    behaviors(ai["ai"]).FLEE(ship, 100000, 100000, 0)


def update(AIworld, aiChars, ship):
    try:
        for aiChar in aiChars:
            ai = aiChars[aiChar]["ai"]
            node = aiChars[aiChar]["mesh"]
            if aiChars[aiChar]["active"]:
                if ai.getDistance(ship) > 50:
                    behaviors(ai).PURSUE(ship)
                    behaviors(ai).SETMASS(50)
                else:
                    behaviors(ai).SETMASS(10000)
                    droneFire(ship, node)
            else:
                behaviors(ai).FLEE(ship, 100000, 100000, 1)
    except:
        None
    AIworld.update()
