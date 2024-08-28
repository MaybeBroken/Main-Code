worldz = 0    # vertical z

octaves=0
dens = 16
seed = int('0000001')

speed = 100    # mostly just a percentage, with 100 being normal, 1000 as the max, and 1 for the minimum.
swingSpeed = 100  # same as above

renderDist = 40
audioVolume = 80

currentGenBlock = 0

camFOV=110

hotbar = [None, None, None, None, None, None, None, None, None]
hotbarCt = [0, 0, 0, 0, 0, 0, 0, 0, 0]
selectedSlot = 0
inventory = [
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
]
inventoryCt = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]

allBlocks = []
allItems = []
kinds_of_blocks = [['dirt', 0.6], ['grass', 0.6], ['sand', 0.6], ['stone', 1.5], ['ancient_debris', 8], ['glass', 0.01], ['glow', 0.01]]
hp = 10

reachDistance=12

difficulty = "Normal"

font = "Minecraft"

camX = 0
camY = 0
camZ = 0

camH = 0
camP = 0
camR = 0

resolution = [1920, 1080]
supportedResolutions = []
winMode = 'full-win'
selectedBlock = None
inMenu = False
inInventory = False
saving = False
inEscape = True
relaunching = False