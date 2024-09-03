import direct.stdpy.threading as thread


class physicsMgr:
    def enable(
        self,
        minimum_motion_check: float = 0.001,
        drag: float = 0.001,
        gravity: tuple = (0, 0, -0.098),
    ):
        self.minimum_motion_check: float = minimum_motion_check
        self.drag = drag
        self.gravity = gravity
        self.registeredObjects = []
        self.colliders = []
        self.collisionActions = []
        self.collisions = []
        self.updating = True

    def registerObject(self, object, velocity: list, name: str):
        self.registeredObjects.append([object, name, velocity])

    def registerColliderPlane(
        self,
        object,
        pos: int,
        name: str,
        orientation: str = "+x",
        collisionAction: str = "rebound",
    ):
        self.colliders.append([object, name, pos, orientation, collisionAction])
    
    def registerCollisionAction(self, action, extraArgs:list):
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

    def clearVectorForce(self, object: None, name: str):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                node[2] = [0, 0, 0]

    def getObjectVelocity(self, object, name) -> list[3]:
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                return node[2]

    def returnCollisions(self) -> list:
        return self.collisions

    def clearCollisions(self):
        self.collisions = []

    def runCollisionActions(self):
        for actionList in self.collisionActions:
            actionList[0](val for val in actionList[1])

    def updateWorldPositions(self):
        for node in self.registeredObjects:

            # drag

            for i in range(len(node[2])):
                if abs(node[2][i]) > self.minimum_motion_check:
                    if node[2][i] > 0:
                        node[2][i] -= self.drag
                    if node[2][i] < 0:
                        node[2][i] += self.drag
                else:
                    node[2][i] = 0

            # gravity

            for i in range(len(node[2])):
                node[2][i] += self.gravity[i]

            #

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
                            if collider[4] == 'rebound':
                                node[2][0] = -(node[2][0])
                            if collider[4] == 'damp':
                                node[2][0] = -(0.5*node[2][0])
                            if collider[4] == 'stop':
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
                            if collider[4] == 'rebound':
                                node[2][0] = -(node[2][0])
                            if collider[4] == 'damp':
                                node[2][0] = -(0.5*node[2][0])
                            if collider[4] == 'stop':
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
                            if collider[4] == 'rebound':
                                node[2][1] = -(node[2][1])
                            if collider[4] == 'damp':
                                node[2][1] = -(0.5*node[2][1])
                            if collider[4] == 'stop':
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
                            if collider[4] == 'rebound':
                                node[2][1] = -(node[2][1])
                            if collider[4] == 'damp':
                                node[2][1] = -(0.5*node[2][1])
                            if collider[4] == 'stop':
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
                            if collider[4] == 'rebound':
                                node[2][2] = -(node[2][2])
                            if collider[4] == 'damp':
                                node[2][2] = -(0.5*node[2][2])
                            if collider[4] == 'stop':
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
                            if collider[4] == 'rebound':
                                node[2][2] = -(node[2][2])
                            if collider[4] == 'damp':
                                node[2][2] = -(0.5*node[2][2])
                            if collider[4] == 'stop':
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
