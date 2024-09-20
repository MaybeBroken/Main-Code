from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter
from src.scripts.weapons import lasers


def behaviors(ai):
    AIbehaviors = ai.getAiBehaviors()

    class internals:
        FLEE = AIbehaviors.flee
        PURSUE = AIbehaviors.pursue

    return internals


def fireLoop(target, origin):
    lasers.fire(origin=origin, target=target, destroy=False)


def update(AIworld, aiChars, ship):
    try:
        for aiChar in aiChars:
            ai = aiChars[aiChar]["ai"]
            node = aiChars[aiChar]["mesh"]
            if node.getDistance(ship) > 40:
                behaviors(ai).PURSUE(ship)
            else:
                behaviors(ai).FLEE(ship)
    except:
        None
    AIworld.update()
