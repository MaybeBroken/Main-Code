from direct.stdpy.threading import Thread
from time import sleep
import math


def distance(pointA, pointB):
    if pointA > 0 and pointB < 0 or pointA < 0 and pointB < 0:
        return pointA - pointB
    elif pointA > 0 and pointB > 0 or pointA < 0 and pointB > 0:
        return pointA + pointB


class physicsMgr:
    def __init__(
        self,
        minimum_motion_check: float = 0.001,
        drag: float = 0.001,
        gravity: tuple = (0, 0, -0.034),
    ):
        self.minimum_motion_check: float = minimum_motion_check
        self.drag = drag
        self.gravity = gravity
        self.registeredObjects = {}
        self.colliders = []
        self.collisionActions = []
        self.collisions = []
        self.updating = True

    def registerObject_Core(
        self,
        object,
        name: str,
        velocity=[0, 0, 0],
        rotation=[0, 0, 0],
    ):
        node = {
            "node": object,
            "name": name,
            "velocity": velocity,
            "rotation": rotation,
            "type": "core",
        }
        self.registeredObjects[name] = node
        self.registeredObjects[f"{name}-t"] = Thread(target=self.update, args=[name])
        self.registeredObjects[f"{name}-t"].start()

    def registerObject_Sphere(
        self,
        object,
        name: str,
        velocity=[0, 0, 0],
        rotation=[0, 0, 0],
        radius=1,
    ):
        node = {
            "node": object,
            "name": name,
            "velocity": velocity,
            "rotation": rotation,
            "type": "sphere",
            "radius": -radius,
        }
        self.registeredObjects[name] = node
        self.registeredObjects[f"{name}-t"] = Thread(target=self.update, args=[name])
        self.registeredObjects[f"{name}-t"].start()

    def registerColliderPlane(
        self,
        object,
        pos: int,
        name: str,
        cType: str = ("rebound", "damp", "stop"),
        orientation: str = ("x", "y", "z"),
    ):
        plane = {
            "node": object,
            "name": name,
            "pos": pos,
            "cType": cType,
            "orientation": 0 if orientation == "x" else 1 if orientation == "y" else 2,
        }
        self.colliders.append(plane)

    def removeObject(self, name: str):
        del self.registeredObjects[name]
        del self.registeredObjects[f"{name}-t"]

    def removeColliderPlane(self, object: None, name: str):
        for node in self.colliders:
            if node["node"] == object or node[1] == name:
                self.colliders.remove(node)

    def addVectorForce(self, name: str, vector: list = [0, 0, 0], rotation=[0, 0, 0]):
        node = self.registeredObjects[name]
        for index in range(len(vector)):
            node["velocity"][index] += vector[index]
        for index in range(len(rotation)):
            node["rotation"][index] += rotation[index]

    def update(self, nodeName):
        while True:
            if self.updating:
                sleep(1 / 60)
                node = self.registeredObjects[nodeName]

                if node["type"] == "core":
                    # drag

                    for i in range(len(node["velocity"])):
                        if abs(node["velocity"][i]) > self.minimum_motion_check:
                            if node["velocity"][i] >= 0:
                                node["velocity"][i] -= self.drag
                            if node["velocity"][i] < 0:
                                node["velocity"][i] += self.drag
                        else:
                            node["velocity"][i] = 0
                    for i in range(len(node["rotation"])):
                        if abs(node["rotation"][i]) > self.minimum_motion_check:
                            if node["rotation"][i] >= 0:
                                node["rotation"][i] -= self.drag
                            if node["rotation"][i] < 0:
                                node["rotation"][i] += self.drag
                        else:
                            node["rotation"][i] = 0
                    # gravity

                    for i in range(len(node["velocity"])):
                        node["velocity"][i] += self.gravity[i]

                    # rotation

                    node["node"].setHpr(
                        node["node"].getHpr()[0] + node["rotation"][0],
                        node["node"].getHpr()[1] + node["rotation"][1],
                        node["node"].getHpr()[2] + node["rotation"][2],
                    )

                    # final check, collisions + updated pos

                    if len(self.colliders) == 0:
                        node["node"].setPos(
                            node["node"].getPos()[0] + node["velocity"][0],
                            node["node"].getPos()[1] + node["velocity"][1],
                            node["node"].getPos()[2] + node["velocity"][2],
                        )
                    else:
                        for collider in self.colliders:
                            if (
                                distance(
                                    node["node"].getPos()[collider["orientation"]]
                                    + node["velocity"][collider["orientation"]],
                                    collider["pos"],
                                )
                                < self.minimum_motion_check
                            ):
                                xyz = collider["orientation"]
                                if collider["cType"] == "stop":
                                    node["velocity"][xyz] = 0
                                elif collider["cType"] == "damp":
                                    if (
                                        node["velocity"][xyz]
                                        > self.minimum_motion_check
                                    ):
                                        node["velocity"][xyz] = (
                                            node["velocity"][xyz] / 2
                                        )
                                    else:
                                        node["velocity"][xyz] = 0
                                elif collider["cType"] == "rebound":
                                    node["velocity"][xyz] = (
                                        -node["velocity"][xyz] + self.gravity[xyz]
                                    )

                        node["node"].setPos(
                            node["node"].getPos()[0] + node["velocity"][0],
                            node["node"].getPos()[1] + node["velocity"][1],
                            node["node"].getPos()[2] + node["velocity"][2],
                        )

                elif node["type"] == "sphere":
                    # drag

                    for i in range(len(node["velocity"])):
                        if abs(node["velocity"][i]) > self.minimum_motion_check:
                            if node["velocity"][i] >= 0:
                                node["velocity"][i] -= self.drag
                            if node["velocity"][i] < 0:
                                node["velocity"][i] += self.drag
                        else:
                            node["velocity"][i] = 0
                    for i in range(len(node["rotation"])):
                        if abs(node["rotation"][i]) > self.minimum_motion_check:
                            if node["rotation"][i] >= 0:
                                node["rotation"][i] -= self.drag
                            if node["rotation"][i] < 0:
                                node["rotation"][i] += self.drag
                        else:
                            node["rotation"][i] = 0
                    # gravity

                    for i in range(len(node["velocity"])):
                        node["velocity"][i] += self.gravity[i]

                    # rotation

                    node["node"].setHpr(
                        node["node"].getHpr()[0] + node["rotation"][0],
                        node["node"].getHpr()[1] + node["rotation"][1],
                        node["node"].getHpr()[2] + node["rotation"][2],
                    )

                    # final check, collisions + updated pos

                    if len(self.colliders) == 0:
                        node["node"].setPos(
                            node["node"].getPos()[0] + node["velocity"][0],
                            node["node"].getPos()[1] + node["velocity"][1],
                            node["node"].getPos()[2] + node["velocity"][2],
                        )
                    else:
                        for collider in self.colliders:
                            if (
                                distance(
                                    node["node"].getPos()[collider["orientation"]]
                                    + node["velocity"][collider["orientation"]]
                                    + node["radius"],
                                    collider["pos"],
                                )
                                < self.minimum_motion_check
                            ):
                                xyz = collider["orientation"]
                                if collider["cType"] == "stop":
                                    node["velocity"][xyz] = 0
                                elif collider["cType"] == "damp":
                                    if (
                                        node["velocity"][xyz]
                                        > self.minimum_motion_check
                                    ):
                                        node["velocity"][xyz] = (
                                            node["velocity"][xyz] / 2
                                        )
                                    else:
                                        node["velocity"][xyz] = 0
                                elif collider["cType"] == "rebound":
                                    node["velocity"][xyz] = (
                                        -node["velocity"][xyz] + self.gravity[xyz]
                                    )

                        node["node"].setPos(
                            node["node"].getPos()[0] + node["velocity"][0],
                            node["node"].getPos()[1] + node["velocity"][1],
                            node["node"].getPos()[2] + node["velocity"][2],
                        )
