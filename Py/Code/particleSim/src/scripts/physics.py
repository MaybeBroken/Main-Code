import direct.stdpy.threading as thread
class physicsMgr:
    def enable(self, minimum_motion_check=0.0001, drag=0):
        self.minimum_motion_check = minimum_motion_check
        self.drag = drag
        self.registeredObjects = []
        self.colliders = []
        self.updating = True
    def registerObject(self, object, velocity:list, name:str):
        self.registeredObjects.append([object, name, velocity])
    def registerCollider(self, object, pos:int, name:str, orientation='+x'):
        self.colliders.append([object, name, pos, orientation])
    def removeObject(self, object:None, name:str):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                self.registeredObjects.remove(node)
    def removeCollider(self, object:None, name:str):
        for node in self.colliders:
            if node[0] == object or node[1] == name:
                self.colliders.remove(node)
    def addVectorForce(self, object:None, name:str, vector:list):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                if len(vector)==len(node[2]):
                    node[2][0]+=vector[0]
                    node[2][1]+=vector[1]
                    node[2][2]+=vector[2]
                else:
                    exit('Warning: incorrect vector addition for ' +str(node[2]) +' and ' +str(vector))
    def removeVectorForce(self, object:None, name:str):
        for node in self.registeredObjects:
            if node[0] == object or node[1] == name:
                node[2]=(0, 0)
    def updateWorld(self):
            for node in self.registeredObjects:
                if len(self.colliders) == 0:
                    node[0].setPos(node[0].getPos()[0] + node[2][0], node[0].getPos()[1] + node[2][1],node[0].getPos()[2] + node[2][2])
                else:
                    for collider in self.colliders:
                        if collider[3]=='+x':
                            if node[0].getPos()[0] + node[2][0] <= collider[2]:
                                node[2][0] = - node[2][0]
                        if collider[3]=='-x':
                            if node[0].getPos()[0] + node[2][0] >= collider[2]:
                                node[2][0] = - node[2][0]
                        if collider[3]=='+y':
                            if node[0].getPos()[2] + node[2][2] <= collider[2]:
                                node[2][2] = - node[2][2]
                        if collider[3]=='-y':
                            if node[0].getPos()[2] + node[2][2] >= collider[2]:
                                node[2][2] = - node[2][2]

                    node[0].setPos(node[0].getPos()[0] + node[2][0], node[0].getPos()[1] + node[2][1],node[0].getPos()[2] + node[2][2])

                for i in range(len(node[2])):
                    if abs(node[2][i]) > self.minimum_motion_check:
                        if node[2][i]>0:
                            node[2][i]-=self.drag
                        if node[2][i]<0:
                            node[2][i]+=self.drag
                    else:
                        node[2][i] = 0