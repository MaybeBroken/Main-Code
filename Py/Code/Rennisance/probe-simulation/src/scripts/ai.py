from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter
from panda3d.core import NodePath
from direct.stdpy.threading import Thread
from src.scripts.weapons import lasers
from time import monotonic, sleep


def behaviors(ai):
    AIbehaviors = ai.getAiBehaviors()

    class internals:
        FLEE = AIbehaviors.flee
        PURSUE = AIbehaviors.pursue
        WANDER = AIbehaviors.wander
        PAUSE = AIbehaviors.pauseAi
        REMOVE = AIbehaviors.removeAi

    return internals



def droneFire(target, origin):
    lastFire = monotonic()
    while True:
        if abs(monotonic() - lastFire) > 3:
            lasers.fire(origin=origin, target=target, destroy=False)
            lastFire = monotonic()
        if target.getDistance(origin) > 40:
            return False
        sleep(0.01)


def removeChar(ai, ship):
    behaviors(ai["ai"]).FLEE(ship, 100000, 100000, 0)


def update(AIworld, aiChars, ship):
    for aiChar in aiChars:
        ai = aiChars[aiChar]["ai"]
        node = aiChars[aiChar]["mesh"]
        if aiChars[aiChar]["active"]:
            if ship.getDistance(node) > 50:
                behaviors(ai).PURSUE(ship)
            else:
                behaviors(ai).REMOVE('pursue')
                node.lookAt((ship.get_x(), ship.get_y(), ship.get_z()))
                node.setP(node.getP() +180)
                node.setR(node.getR() +180)
                if not aiChars[aiChar]["firing"]:
                    if ship.getDistance(node) < 40:
                        Thread(target=droneFire, args=(ship, node)).start()
                        aiChars[aiChar]["firing"] = True
            if ship.getDistance(node) > 40:
                aiChars[aiChar]["firing"] = False
        else:
            behaviors(ai).FLEE(ship, 10000, 10000, 1)
    AIworld.update()
