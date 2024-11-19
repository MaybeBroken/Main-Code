def int_to_item(num:int) -> str:
    if num == 0:
        return 'dirt'
    elif num == 1:
        return 'grass'
    elif num == 2:
        return 'sand'
    elif num == 3:
        return 'stone'
    elif num == 4:
        return 'ancient_debris'
    elif num == 5:
        return 'glass'
    elif num == 6:
        return 'glow'
    else:
        return 'none'

def item_to_int(item:str) -> int:
    if item == 'dirt':
        return 0
    elif item == 'grass':
        return 1
    elif item == 'sand':
        return 2
    elif item == 'stone':
        return 3
    elif item == 'ancient_debris':
        return 4
    elif item == 'glass':
        return 5
    elif item == 'glow':
        return 6
    else:
        return None

def item_to_nodePath(item, MainApp) -> None:
    if item == 'grass':
        return MainApp.grassBlock
    elif item == 'dirt':
        return MainApp.dirtBlock
    elif item == 'stone':
        return MainApp.stoneBlock
    elif item == 'sand':
        return MainApp.sandBlock
    elif item == 'ancient_debris':
        return MainApp.ancient_debrisBlock
    elif item == 'glass':
        return MainApp.glassBlock
    elif item == 'glow':
        return MainApp.glowBlock

def nodePath_to_item(nodePath, MainApp) -> str:
    if nodePath == MainApp.grassBlock:
        return 'grass'
    elif nodePath == MainApp.dirtBlock:
        return 'dirt'
    elif nodePath == MainApp.stoneBlock:
        return 'stone'
    elif nodePath == MainApp.sandBlock:
        return 'sand'
    elif nodePath == MainApp.ancient_debrisBlock:
        return 'ancient_debris'
    elif nodePath == MainApp.glassBlock:
        return 'glass'
    elif nodePath == MainApp.glowBlock:
        return 'glow'
