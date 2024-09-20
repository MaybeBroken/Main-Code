from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter


def behaviors(ai):
    AIbehaviors = ai.getAiBehaviors()

    class internals:
        FLEE = AIbehaviors.flee
        PURSUE = AIbehaviors.pursue

    return internals


def update(aiChars, ship):
    try:
        for aiChar in aiChars:
            ai = aiChars[aiChar]["ai"]
            node = aiChars[aiChar]["mesh"]
            behaviors(ai).PURSUE(ship)
    except:
        None
