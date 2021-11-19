from os import getcwd
from sys import path
from time import sleep, time

path.append(getcwd())
from common2 import adb
from foo.ocr.ocr import getText, findTextPos, findTextPos_all
from foo.pictureR.pictureFind import matchMultiImg



def spoilsCheck():
    topLine = 0


    img = adb.getScreen_std(True)
    ocrResult = getText(img)
    
    ans = findTextPos(ocrResult, ['行动结束'], [])
    ans1 = findTextPos(ocrResult, ['龙门币'], [])
    if ans != None and ans1 != None:
        topLine = ans[1][0][1] #行动结束的上边沿
        bottomLine = ans1[1][0][1] #龙门币的上边沿
        leftLine = ans1[1][1][0] #龙门币的右边沿

        temp1 = matchMultiImg(adb.getScreen_std(), './res/booty/num/1.png', targetSize=1080)
        temp2 = matchMultiImg(adb.getScreen_std(), './res/booty/num/2.png', targetSize=1080)

        allNums = []
        for i in range(len(temp1[0])):
            if topLine < temp1[0][i][1] < bottomLine and temp1[0][i][0] > leftLine:
                allNums.append([temp1[0][i], temp1[2][i], '1'])
        for i in range(len(temp2[0])):
            if topLine < temp2[0][i][1] < bottomLine and temp2[0][i][0] > leftLine:
                allNums.append([temp2[0][i], temp2[2][i], '2'])

        if allNums != []:
            spoils = dict()
            for i in allNums:
                adb.click(i[0][0], i[0][1])
                temp = getText(adb.getScreen_std(True))
                
                tempAns = findTextPos(temp, ['库存'], [])
                nameLine = tempAns[1][0][1] #库存所在的水平线
                tempAns = findTextPos_all(temp, [''], ['库存'])
                thisName = None
                yDistance = adb.screenY
                for j in tempAns:
                    if abs(j[0][1] - nameLine) < yDistance:
                        yDistance = abs(j[0][1] - nameLine)
                        thisName = j[2]
                spoils[thisName] = int(i[2])
                adb.click(i[0][0], i[0][1])
            return spoils
        else:
            return dict()
    else:
        return dict()






















