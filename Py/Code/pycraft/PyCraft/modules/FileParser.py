import PyCraft.modules.vars as WorldVars
import PyCraft.modules.utils as utils
class get():
    def decodeFile(self, fileARR) -> list:
        blockARR = []
        for index, data in enumerate(fileARR):
            x=0
            y=0
            z=0
            h=0
            p=0
            r=0
            blocktype = ''
            data = list(data)
            data.reverse()
            data[0] = ''
            data.reverse()
            data = ''.join(data)
            if data[0] == '#':
                data = list(data)
                data[0] = ''
                data = ''.join(data)
                for i in range(len(data)):
                    if i<6:
                        if i==0:
                            x=x+(int(data[i])*100000)
                        if i==1:
                            x=x+(int(data[i])*10000)
                        if i==2:
                            x=x+(int(data[i])*1000)
                        if i==3:
                            x=x+(int(data[i])*100)
                        if i==4:
                            x=x+(int(data[i])*10)
                        if i==5:
                            x=x+(int(data[i])*1)
                    if i==6 and(data[i]=='-'):
                        x=(-x)
                    if i>6 and(i<13):
                        if i==7:
                            y=y+(int(data[i])*100000)
                        if i==8:
                            y=y+(int(data[i])*10000)
                        if i==9:
                            y=y+(int(data[i])*1000)
                        if i==10:
                            y=y+(int(data[i])*100)
                        if i==11:
                            y=y+(int(data[i])*10)
                        if i==12:
                            y=y+(int(data[i])*1)
                    if i==13 and(data[i]=='-'):
                        y=(-y)
                    if i>13 and(i<20):
                        if i==14:
                            z=z+(int(data[i])*100000)
                        if i==15:
                            z=z+(int(data[i])*10000)
                        if i==16:
                            z=z+(int(data[i])*1000)
                        if i==17:
                            z=z+(int(data[i])*100)
                        if i==18:
                            z=z+(int(data[i])*10)
                        if i==19:
                            z=z+(int(data[i])*1)
                    if i==20 and(data[i]=='-'):
                        z=(-z)
                    if i>20 and(i<24):
                        if i==21:
                            h=h+(int(data[i])*100)
                        if i==22:
                            h=h+(int(data[i])*10)
                        if i==23:
                            h=h+(int(data[i])*1)
                    if i==24 and(data[i]=='-'):
                        h=(-h)
                    if i>24 and(i<28):
                        if i==21:
                            p=p+(int(data[i])*100)
                        if i==22:
                            p=p+(int(data[i])*10)
                        if i==23:
                            p=p+(int(data[i])*1)
                    if i==28 and(data[i]=='-'):
                        p=(-p)
                    if i>28 and(i<32):
                        if i==21:
                            r=r+(int(data[i])*100)
                        if i==22:
                            r=r+(int(data[i])*10)
                        if i==23:
                            r=r+(int(data[i])*1)
                    if i==32 and(data[i]=='-'):
                        r=(-r)
                    
                    WorldVars.camX = x
                    WorldVars.camY = y
                    WorldVars.camZ = z

            elif data[0] == '!':
                data = list(data)
                data[0] = ''
                data = ''.join(data)
                invIndex = 0
                itemIndex = 0
                itemAmount = 0
                for i in range(len(data)):
                    if i==0:
                        invIndex += (int(data[i])*10)
                    if i==1:
                        invIndex += (int(data[i])*1)

                    if i==3:
                        itemAmount += (int(data[i])*10)
                    if i==4:
                        itemAmount += (int(data[i])*1)

                    if i==6:
                        itemIndex += (int(data[i])*100)
                    if i==7:
                        itemIndex += (int(data[i])*10)
                    if i==8:
                        itemIndex += (int(data[i])*1)
                invIndex -= 1
                if invIndex < 9:
                    WorldVars.hotbar[invIndex] = utils.int_to_item(itemIndex)
                    WorldVars.hotbarCt[invIndex] = itemAmount
                elif invIndex >= 9:
                    rIndex = None
                    if invIndex < 18:
                        rIndex = 0
                    elif invIndex >= 18 and invIndex < 27:
                        rIndex = 1
                    elif invIndex >= 27 and invIndex < 36:
                        rIndex = 2
                    WorldVars.inventory[rIndex][invIndex] = utils.int_to_item(itemIndex)
                    WorldVars.inventoryCt[rIndex][invIndex] = itemAmount

            else:
                for i in range(21):
                    if i<6:
                        if i==0:
                            x=x+(int(data[i])*100000)
                        if i==1:
                            x=x+(int(data[i])*10000)
                        if i==2:
                            x=x+(int(data[i])*1000)
                        if i==3:
                            x=x+(int(data[i])*100)
                        if i==4:
                            x=x+(int(data[i])*10)
                        if i==5:
                            x=x+(int(data[i])*1)
                    if i==6 and(data[i]=='-'):
                        x=(-x)
                    if i>6 and(i<13):
                        if i==7:
                            y=y+(int(data[i])*100000)
                        if i==8:
                            y=y+(int(data[i])*10000)
                        if i==9:
                            y=y+(int(data[i])*1000)
                        if i==10:
                            y=y+(int(data[i])*100)
                        if i==11:
                            y=y+(int(data[i])*10)
                        if i==12:
                            y=y+(int(data[i])*1)
                    if i==13 and(data[i]=='-'):
                        y=(-y)
                    if i>13 and(i<20):
                        if i==14:
                            z=z+(int(data[i])*100000)
                        if i==15:
                            z=z+(int(data[i])*10000)
                        if i==16:
                            z=z+(int(data[i])*1000)
                        if i==17:
                            z=z+(int(data[i])*100)
                        if i==18:
                            z=z+(int(data[i])*10)
                        if i==19:
                            z=z+(int(data[i])*1)
                    if i==20 and(data[i]=='-'):
                        z=(-z)
                blocktype = utils.int_to_item(int(data[21]))
                blockARR.append([x, y, z, blocktype])
        return blockARR

class saveWorld():
    def worldToText(self, worldARR:list) -> list:
        returnlist = []
        test = [WorldVars.camX, WorldVars.camY, WorldVars.camZ, WorldVars.camH, WorldVars.camP, WorldVars.camR]
        x=round(test[0])
        y=round(test[1])
        z=round(test[2])
        h=round(test[3])
        p=round(test[4])
        r=round(test[5])
        xamount = list(str(x))
        yamount = list(str(y))
        zamount = list(str(z))
        hamount = list(str(h))
        pamount = list(str(p))
        ramount = list(str(r))
        xamount.reverse()
        yamount.reverse()
        zamount.reverse()
        hamount.reverse()
        pamount.reverse()
        ramount.reverse()
        xMain = 6
        yMain = 6
        zMain = 6
        hMain = 3
        pMain = 3
        rMain = 3
        for blank in xamount:
            xMain = xMain - 1
        for blank in yamount:
            yMain = yMain - 1
        for blank in zamount:
            zMain = zMain - 1
        for blank in hamount:
            hMain = hMain - 1
        for blank in pamount:
            pMain = pMain - 1
        for blank in ramount:
            rMain = rMain - 1
        for blank in range(xMain):
            xamount.append("0")
        for blank in range(yMain):
            yamount.append("0")
        for blank in range(zMain):
            zamount.append("0")
        for blank in range(hMain):
            hamount.append("0")
        for blank in range(pMain):
            pamount.append("0")
        for blank in range(rMain):
            ramount.append("0")
        xamount.reverse()
        yamount.reverse()
        zamount.reverse()
        hamount.reverse()
        pamount.reverse()
        ramount.reverse()
        xamount = ''.join(xamount)
        yamount = ''.join(yamount)
        zamount = ''.join(zamount)
        hamount = ''.join(hamount)
        pamount = ''.join(pamount)
        ramount = ''.join(ramount)
        
        xamount = xamount.replace('-', '0')
        yamount = yamount.replace('-', '0')
        zamount = zamount.replace('-', '0')
        hamount = hamount.replace('-', '0')
        pamount = pamount.replace('-', '0')
        ramount = ramount.replace('-', '0')
        
        xIsPos = " "
        yIsPos = " "
        zIsPos = " "
        hIsPos = " "
        pIsPos = " "
        rIsPos = " "
        
        if x < 0:
            xIsPos = "-"
        else:
            xIsPos = " "
        if y < 0:
            yIsPos = "-"
        else:
            yIsPos = " "
        if z < 0:
            zIsPos = "-"
        else:
            zIsPos = " "
        if h < 0:
            hIsPos = "-"
        else:
            hIsPos = " "
        if p < 0:
            pIsPos = "-"
        else:
            pIsPos = " "
        if r < 0:
            rIsPos = "-"
        else:
            rIsPos = " "
        returnAmount = ('#' +str(xamount) +xIsPos +str(yamount) +yIsPos +str(zamount) +zIsPos +str(hamount) +hIsPos +str(pamount) +pIsPos +str(ramount) +rIsPos)
        returnlist.append(returnAmount)
        
        i=0
        for blank in worldARR:
            test = list(worldARR[i])
            x=int(round(test[0]))
            y=int(round(test[1]))
            z=int(round(test[2]))
            block=test[3]
            xamount = list(str(x))
            yamount = list(str(y))
            zamount = list(str(z))
            xamount.reverse()
            yamount.reverse()
            zamount.reverse()
            xMain = 6
            yMain = 6
            zMain = 6
            for blank in xamount:
                xMain = xMain - 1
            for blank in yamount:
                yMain = yMain - 1
            for blank in zamount:
                zMain = zMain - 1
            for blank in range(xMain):
                xamount.append("0")
            for blank in range(yMain):
                yamount.append("0")
            for blank in range(zMain):
                zamount.append("0")
            xamount.reverse()
            yamount.reverse()
            zamount.reverse()
            xamount = ''.join(xamount)
            yamount = ''.join(yamount)
            zamount = ''.join(zamount)
            block= utils.item_to_int(block)
            
            xamount = xamount.replace('-', '0')
            yamount = yamount.replace('-', '0')
            zamount = zamount.replace('-', '0')
            
            xIsPos = " "
            yIsPos = " "
            zIsPos = " "
            if x < 0:
                xIsPos = "-"
            else:
                xIsPos = " "

            if y < 0:
                yIsPos = "-"
            else:
                yIsPos = " "

            if z < 0:
                zIsPos = "-"
            else:
                zIsPos = " "
            returnAmount = (str(xamount) +xIsPos +str(yamount) +yIsPos +str(zamount) +zIsPos +str(block))
            returnlist.append(returnAmount)
            i=i+1
        

        for index in range(len(WorldVars.hotbar)):
            item = WorldVars.hotbar[index]
            pos = WorldVars.hotbar.index(item) + 1
            amount = WorldVars.hotbarCt[pos-1]

            posamount = list(str(pos))
            posamount.reverse()
            posMain = 2

            itemAmount = list(str(amount))
            itemAmount.reverse()
            itemMain = 2

            block = list(str(utils.item_to_int(item)))
            block.reverse()
            blockMain = 3

            for blank in posamount:
                posMain = posMain - 1
            
            for blank in itemAmount:
                itemMain = itemMain - 1

            for blank in block:
                blockMain = blockMain - 1


            for blank in range(posMain):
                posamount.append("0")
            
            for blank in range(itemMain):
                itemAmount.append("0")

            for blank in range(blockMain):
                block.append("0")

            posamount.reverse()
            posamount = ''.join(posamount)

            itemAmount.reverse()
            itemAmount = ''.join(itemAmount)

            block.reverse()
            block = ''.join(block)

            returnAmount = ('!' +str(posamount) +" " +str(itemAmount) +" " +str(block))
            if item != None and (block != None):
                returnlist.append(returnAmount)


        return returnlist