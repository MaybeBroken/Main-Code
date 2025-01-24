from time import sleep
import direct.stdpy.threading as thread


class physicsMgr:
    def enable(
        self,
        drag: float = 0.001,
        gravity: tuple = (0, 0, -0.098),
        rotational_drag: float = 0.001,  # Add rotational drag
    ):
        self.drag = drag
        self.gravity = gravity
        self.rotational_drag = rotational_drag  # Initialize rotational drag
        self.registeredObjects = []
        self.colliders = []
        self.collisionActions = []
        self.collisions = []
        self.updating = True

    def registerObject(
        self,
        object,
        name: str,
        velocity: list = [0, 0, 0],
        velocityLimit=None,
        rotational_velocity: list = [0, 0, 0],
        rotationLimit=None,
    ):
        self.registeredObjects.append(
            [
                object,
                name,
                velocity,
                rotational_velocity,
                velocityLimit,
                rotationLimit,
            ]
        )  # Add rotational velocity

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

    def removeObject(self, object: None, name: str):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                self.registeredObjects.remove(node)

    def removeColliderPlane(self, object: None, name: str):
        for node in self.colliders:
            if node[0] == object or node[1] == name:
                self.colliders.remove(node)

    def addVectorForce(self, object: None, name: str, vector: list):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                if node[4] != None:
                    if len(vector) == len(node[2]):
                        if abs(node[2][0]) < abs(node[4][0]):
                            node[2][0] += vector[0]
                        if abs(node[2][1]) < abs(node[4][1]):
                            node[2][1] += vector[1]
                        if abs(node[2][2]) < abs(node[4][2]):
                            node[2][2] += vector[2]
                    else:
                        exit(
                            "Warning: incorrect vector addition for "
                            + str(node[2])
                            + " and "
                            + str(vector)
                        )
                else:
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

    def addRotationalForce(self, object: None, name: str, rotational_vector: list):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                if node[5] != None:
                    if len(rotational_vector) == len(node[3]):
                        if abs(node[3][0]) < abs(node[5][0]):
                            node[3][0] += rotational_vector[0]
                        if abs(node[3][1]) < abs(node[5][1]):
                            node[3][1] += rotational_vector[1]
                        if abs(node[3][2]) < abs(node[5][2]):
                            node[3][2] += rotational_vector[2]
                    else:
                        exit(
                            "Warning: incorrect rotational vector addition for "
                            + str(node[3])
                            + " and "
                            + str(rotational_vector)
                        )
                else:
                    if len(rotational_vector) == len(node[3]):
                        node[3][0] += rotational_vector[0]
                        node[3][1] += rotational_vector[1]
                        node[3][2] += rotational_vector[2]
                    else:
                        exit(
                            "Warning: incorrect rotational vector addition for "
                            + str(node[3])
                            + " and "
                            + str(rotational_vector)
                        )

    def clearVectorForce(self, object: None, name: str):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                node[2] = [0, 0, 0]

    def clearRotationalForce(self, object: None, name: str):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                node[3] = [0, 0, 0]

    def getObjectVelocity(self, object, name) -> list[3]:
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                return node[2]

    def getObjectRotationalVelocity(self, object, name) -> list[3]:
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                return node[3]

    def returnCollisions(self) -> list:
        return self.collisions

    def clearCollisions(self):
        self.collisions = []

    def runCollisionActions(self):
        for actionList in self.collisionActions:
            actionList[0](val for val in actionList[1])

    def start(self, FPS=60):
        def _th():
            while True:
                sleep(1 / FPS)
                self.updateWorldPositions()

        thread.Thread(target=_th).start()

    def updateWorldPositions(self):
        for node in self.registeredObjects:

            # drag

            for i in range(len(node[2])):
                if abs(node[2][i]) > self.drag:
                    if node[2][i] > 0:
                        node[2][i] -= self.drag
                    if node[2][i] < 0:
                        node[2][i] += self.drag
                else:
                    node[2][i] = 0

            # gravity

            for i in range(len(node[2])):
                node[2][i] += self.gravity[i]

            # rotational drag
            for i in range(len(node[3])):
                if abs(node[3][i]) > self.rotational_drag:
                    if node[3][i] > 0:
                        node[3][i] -= self.rotational_drag
                    if node[3][i] < 0:
                        node[3][i] += self.rotational_drag
                else:
                    node[3][i] = 0

            # final check, collisions + updated pos

            if len(self.colliders) == 0:
                node[0].setPos(
                    node[0].getPos()[0] + node[2][0],
                    node[0].getPos()[1] + node[2][1],
                    node[0].getPos()[2] + node[2][2],
                )
                node[0].setHpr(
                    node[0].getH() + node[3][0],
                    node[0].getP() + node[3][1],
                    node[0].getR() + node[3][2],
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
                node[0].setHpr(
                    node[0].getH() + node[3][0],
                    node[0].getP() + node[3][1],
                    node[0].getR() + node[3][2],
                )
