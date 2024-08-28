import os
class openWorldFile():
    def start(self):
        self.folderPath = "PyCraft/Worlds/"

        if os.path.exists(self.folderPath) == True:
            self
        else:
            open(self.folderPath, "x")
        
        self.worldListFileLocation = (self.folderPath +".list.dat1")
        self.worldListFile = open(self.worldListFileLocation, "r")
        self.Worlds = self.worldListFile.readlines()
        self.worldListFile.close()

    def returnWorldList(self):
        self.worldListFile = open(self.worldListFileLocation, "r")
        self.Worlds = self.worldListFile.readlines()
        self.worldListFile.close()
        worldList = []
        for current_world in self.Worlds:
            worldList.append(current_world)
        return worldList
    
    def namecheck(self, name):
        worldList = self.returnWorldList()
        testname = (self.folderPath +name +".dat")
        for worldNameCheck in worldList:
            if worldNameCheck == testname:
                return 0
            else: return 1

    def makeNewWorld(self, name):
        if self.namecheck(name=name) == 1:
            open(self.folderPath +name +".dat", "x")
            self.worldListFile = open(self.worldListFileLocation, "a")
            self.worldListFile.write(self.folderPath +name +".dat" +"\n")
            self.worldListFile.close()
        else: print("File already exists")
    
    def removeWorldEntry(self, name):
        with open(self.worldListFileLocation,"r+") as file:
            new_f = file.readlines()
            file.seek(0)
            for line in new_f:
                if name not in line:
                    file.write(line)
            file.truncate()
    
    
    def deleteWorld(self, name):
        worldList = self.returnWorldList()
        world = list(name)
        world.reverse()
        if world[0] == '\n':
            world[0] = ''
        world.reverse()
        world = ''.join(world)
        for worldNameCheck in worldList:
            if worldNameCheck == name:
                os.remove(world)
                self.removeWorldEntry(name=name)
        
    
    def readWorldFile(self, name):
        data = []
        world = list(name)
        world.reverse()
        world[0] = ''
        world.reverse()
        world = ''.join(world)
        worldData = open(world)
        for worldLine in worldData:
            data.append(worldLine)
        return data
    
    def saveWorld(self, worldARR, name):
        world = list(name)
        world.reverse()
        world[0] = ''
        world.reverse()
        world = ''.join(world)
        open(world, "w").close()
        file = open(world, "a")
        for i in worldARR:
            file.write(i +"\n")

mgr = openWorldFile()
