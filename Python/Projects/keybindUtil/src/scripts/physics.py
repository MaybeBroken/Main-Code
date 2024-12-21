from direct.stdpy.threading import Thread
from time import sleep


class physicsMgr:
    def __init__(
        self,
        minimum_motion_check: float = 0.001,
        drag: float = 0.001,
        gravity: tuple = (0, 0, -0.098),
    ):
        self.minimum_motion_check: float = minimum_motion_check
        self.drag = drag
        self.gravity = gravity
        self.registeredObjects = {}
        self.colliders = []
        self.collisionActions = []
        self.collisions = []
        self.updating = True

    def registerObject(self, object, name: str, velocity=[0, 0, 0], rotation=[0, 0, 0]):
        node = [object, name, velocity, rotation]
        self.registeredObjects[name] = node
        self.registeredObjects[f"{name}-t"] = Thread(target=self.update, args=[name])

    def registerColliderPlane(
        self,
        object,
        pos: int,
        name: str,
        orientation: str = "+x",
        collisionAction: str = "rebound",
    ):
        self.colliders.append([object, name, pos, orientation, collisionAction])

    def registerCollisionAction(self, action, extraArgs: list):
        self.collisionActions.append([action, extraArgs])

    def removeObject(self, name: str):
        del self.registeredObjects[name]
        del self.registeredObjects[f"{name}-t"]

    def removeColliderPlane(self, object: None, name: str):
        for node in self.colliders:
            if node[0] == object or node[1] == name:
                self.colliders.remove(node)

    def addVectorForce(self, name: str, vector: list):
        node = self.registeredObjects[name]
        if len(vector) == len(node[2]):
            node[2][0] += vector[0]
            node[2][1] += vector[1]
            node[2][2] += vector[2]
        else:
            exit(
                "Warning: incorrect vector addition for "
                + str(node[2])
                + " and "
                + str(vector)
            )

    def clearVectorForce(self, name: str):
        self.registeredObjects[name] = [0, 0, 0]

    def getObjectVelocity(self, name: str) -> list[3]:
        return self.registeredObjects[name]

    def returnCollisions(self) -> list:
        return self.collisions

    def clearCollisions(self):
        self.collisions = []

    def runCollisionActions(self):
        for actionList in self.collisionActions:
            actionList[0](val for val in actionList[1])

    def update(self, nodeName):
        try:
            while True:
                sleep(0.01)
                node = self.registeredObjects[nodeName]
                # drag

                for i in range(len(node[2])):
                    if abs(node[2][i]) > self.minimum_motion_check:
                        if node[2][i] > 0:
                            node[2][i] -= self.drag
                        if node[2][i] < 0:
                            node[2][i] += self.drag
                    else:
                        node[2][i] = 0
                for i in range(len(node[3])):
                    if abs(node[3][i]) > self.minimum_motion_check:
                        if node[3][i] > 0:
                            node[3][i] -= self.drag
                        if node[3][i] < 0:
                            node[3][i] += self.drag
                    else:
                        node[3][i] = 0

                # gravity

                for i in range(len(node[2])):
                    node[2][i] += self.gravity[i]

                # rotation

                node[0].setHpr(
                    node[0].getHpr()[0] + node[3][0],
                    node[0].getHpr()[1] + node[3][1],
                    node[0].getHpr()[2] + node[3][2],
                )

                # final check, collisions + updated pos

                if len(self.colliders) == 0:
                    node[0].setPos(
                        node[0].getPos()[0] + node[2][0],
                        node[0].getPos()[1] + node[2][1],
                        node[0].getPos()[2] + node[2][2],
                    )
                else:

                    # collision math

                    for collider in self.colliders:
                        if collider[3] == "+x":
                            if node[0].getPos()[0] + node[2][0] <= collider[2]:
                                if collider[4] == "rebound":
                                    node[2][0] = -(node[2][0])
                                if collider[4] == "damp":
                                    node[2][0] = -(0.5 * node[2][0])
                                if collider[4] == "stop":
                                    node[2][0] = 0
                                self.collisions.append(
                                    [
                                        node,
                                        (
                                            node[0].getPos()[0] + node[2][0],
                                            node[0].getPos()[1] + node[2][1],
                                            node[0].getPos()[2] + node[2][2],
                                        ),
                                    ]
                                )
                                self.runCollisionActions(self=self)
                        if collider[3] == "-x":
                            if node[0].getPos()[0] + node[2][0] >= collider[2]:
                                if collider[4] == "rebound":
                                    node[2][0] = -(node[2][0])
                                if collider[4] == "damp":
                                    node[2][0] = -(0.5 * node[2][0])
                                if collider[4] == "stop":
                                    node[2][0] = 0
                                self.collisions.append(
                                    [
                                        node,
                                        (
                                            node[0].getPos()[0] + node[2][0],
                                            node[0].getPos()[1] + node[2][1],
                                            node[0].getPos()[2] + node[2][2],
                                        ),
                                    ]
                                )
                                self.runCollisionActions(self=self)
                        if collider[3] == "+y":
                            if node[0].getPos()[1] + node[2][1] <= collider[2]:
                                if collider[4] == "rebound":
                                    node[2][1] = -(node[2][1])
                                if collider[4] == "damp":
                                    node[2][1] = -(0.5 * node[2][1])
                                if collider[4] == "stop":
                                    node[2][1] = 0
                                self.collisions.append(
                                    [
                                        node,
                                        (
                                            node[0].getPos()[0] + node[2][0],
                                            node[0].getPos()[1] + node[2][1],
                                            node[0].getPos()[2] + node[2][2],
                                        ),
                                    ]
                                )
                                self.runCollisionActions(self=self)
                        if collider[3] == "-y":
                            if node[0].getPos()[1] + node[2][1] >= collider[2]:
                                if collider[4] == "rebound":
                                    node[2][1] = -(node[2][1])
                                if collider[4] == "damp":
                                    node[2][1] = -(0.5 * node[2][1])
                                if collider[4] == "stop":
                                    node[2][1] = 0
                                self.collisions.append(
                                    [
                                        node,
                                        (
                                            node[0].getPos()[0] + node[2][0],
                                            node[0].getPos()[1] + node[2][1],
                                            node[0].getPos()[2] + node[2][2],
                                        ),
                                    ]
                                )
                                self.runCollisionActions(self=self)
                        if collider[3] == "+z":
                            if node[0].getPos()[2] + node[2][2] <= collider[2]:
                                if collider[4] == "rebound":
                                    node[2][2] = -(node[2][2])
                                if collider[4] == "damp":
                                    node[2][2] = -(0.5 * node[2][2])
                                if collider[4] == "stop":
                                    node[2][2] = 0
                                self.collisions.append(
                                    [
                                        node,
                                        (
                                            node[0].getPos()[0] + node[2][0],
                                            node[0].getPos()[1] + node[2][1],
                                            node[0].getPos()[2] + node[2][2],
                                        ),
                                    ]
                                )
                                self.runCollisionActions(self=self)
                        if collider[3] == "-z":
                            if node[0].getPos()[2] + node[2][2] >= collider[2]:
                                if collider[4] == "rebound":
                                    node[2][2] = -(node[2][2])
                                if collider[4] == "damp":
                                    node[2][2] = -(0.5 * node[2][2])
                                if collider[4] == "stop":
                                    node[2][2] = 0
                                self.collisions.append(
                                    [
                                        node,
                                        (
                                            node[0].getPos()[0] + node[2][0],
                                            node[0].getPos()[1] + node[2][1],
                                            node[0].getPos()[2] + node[2][2],
                                        ),
                                    ]
                                )
                                self.runCollisionActions(self=self)

                    # update FINAL position

                    node[0].setPos(
                        node[0].getPos()[0] + node[2][0],
                        node[0].getPos()[1] + node[2][1],
                        node[0].getPos()[2] + node[2][2],
                    )

        except:
            ...
