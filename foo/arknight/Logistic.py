from os import getcwd, listdir
from sys import path
from time import sleep

path.append(getcwd())
from foo.adb import adbCtrl
from foo.pictureR import pictureFind, ocr

class Logistic:
    def __init__(self, adb, cwd):
        self.adb = adb
        self.cwd = cwd
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'

        self.similarChar = {'巧':15}
        self.operatorPosOffset = [757-1355, 885-1355, 1009-1355, 1137-1355, 1264-1355]
        self.moodsPos = [(353, 577, 87, 35), (353, 614, 87, 35), (353, 650, 87, 35), (353, 686, 87, 35), (353, 722, 87, 35)]

        self.moodThreshold = 0
        self.enableRooms = ['制', '造', '会', '客', '贸', '易', '发', '电', '办', '公']

        self.resourceInit()
    
    def getScreen(self):
        self.adb.screenShot()

    def click(self, picResult):
        self.adb.click(picResult[0], picResult[1])

    def swipe(self, startPoint, endPoint):
        self.adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = 500)
        self.adb.swipe(endPoint[0], endPoint[1], endPoint[0], endPoint[1], lastTime = 200)

    def matchPic(self, obj):
        return pictureFind.matchImg(self.screenShot, obj, confidencevalue = 0.7)

    def matchMultPics(self, obj):
        ans = pictureFind.matchMultiImg(self.screenShot, obj, confidencevalue = 0.7)
        return ans[0] if ans != None else None

    def getDormMoods(self):
        ans = []
        for i in self.moodsPos:
            isFull = pictureFind.matchImg_roi(self.screenShot, self.full, i, confidencevalue = 0.75)
            if isFull != None:
                ans.append('0/24') #即认为已疲劳，后续处理撤下
            else:
                ans.append('') #认为此处无人，不操作
        return ans

    def resourceInit(self):
        self.freeOperator_sel = pictureFind.picRead(self.cwd + '/res/logistic/general/freeOperator_sel.png')
        self.freeOperator_unSel = pictureFind.picRead(self.cwd + '/res/logistic/general/freeOperator_unSel.png')
        self.roomFlag = pictureFind.picRead(self.cwd + '/res/logistic/general/roomFlag.png')
        self.unDetected = pictureFind.picRead(self.cwd + '/res/logistic/general/unDetected.png')
        self.zero = pictureFind.picRead(self.cwd + '/res/logistic/general/zero.png')
        self.full = pictureFind.picRead(self.cwd + '/res/logistic/general/full.png')

    def freeOperator(self):
        freeCount = 0
        tryCount = 0
        while True:
            #进入撤下干员模式
            self.getScreen()
            freeSel = self.matchPic(self.freeOperator_sel)
            freeUnsel = self.matchPic(self.freeOperator_unSel)
            if freeUnsel != None and freeSel == None:
                self.click(freeUnsel['result'])
            elif freeSel != None and freeUnsel == None:
                break
            else:
                tryCount += 1
                if tryCount > 3:
                    print('err:未找到撤下干员按钮')
                    return -1 #出错
                continue
            tryCount = 0

        tryCount = 0
        endCount = 0
        isLastTurn = False
        while not isLastTurn:
            self.getScreen()
            roomsOnScreen = self.matchMultPics(self.roomFlag)
            floorUndetect = self.matchPic(self.unDetected)
            if floorUndetect != None:
                isLastTurn = True
            if roomsOnScreen != None:
                tryCount = 0
                roomsOnScreen.sort(key = lambda x:x[1])
                if len(roomsOnScreen) >= 1:
                    if len(roomsOnScreen) == 1:
                        isLastTurn = True
                    upper = roomsOnScreen[0]
                    lower = roomsOnScreen[-1]
                    for eachRoom in roomsOnScreen:
                        isDorm = False
                        roomName = ocr.ocr_roomName(self.screenShot, eachRoom, self.adb.getResolution())
                        if '训' in roomName or '练' in roomName:
                            endCount += 1
                            if endCount > 1:
                                isLastTurn = True
                            continue
                        elif '中' in roomName or '枢' in roomName:
                            continue
                        elif '宿' in roomName or '舍' in roomName:
                            isDorm = True
                        else:
                            #只操作启用的房间
                            isDisable = True
                            for i in self.enableRooms:
                                if i in roomName:
                                    isDisable = False
                                    break
                            if isDisable:
                                continue
                        self.click((eachRoom[0] - 785, eachRoom[1] + 6))
                        self.getScreen()
                        if isDorm:
                            moods = self.getDormMoods()
                        else:
                            moods = ocr.ocr_operatorMood(self.screenShot, roi = (344, 574, 455 - 344, 761 - 574),
                                                                                 resolution = self.adb.getResolution())
                        for eachOperator in range(len(moods)):
                            if moods[eachOperator] != '':
                                #该位置有人
                                restMood = ''
                                for eachChar in moods[eachOperator]:
                                    if ord('0') <= ord(eachChar) <= ord('9'):
                                        restMood += eachChar
                                    elif restMood == '' and eachOperator in self.similarChar.keys():
                                        restMood = self.similarChar[eachOperator]
                                        break
                                    else:
                                        if restMood.isdigit():
                                            if '2' in restMood:
                                                #检测0
                                                isZero = pictureFind.matchImg_roi(self.screenShot, self.zero, 
                                                                        self.moodsPos[eachOperator], confidencevalue = 0.75)
                                                if isZero != None:
                                                    if len(restMood) == 1:
                                                        restMood = '0'
                                                    elif len(restMood) == 2:
                                                        restMood = restMood[0] + '0'
                                                    else:
                                                        print('err:错误的心情')
                                                        restMood = '24'
                                            restMood = int(restMood)
                                            break
                                else:
                                    if restMood.isdigit():
                                        restMood = int(restMood)
                                    else:
                                        continue
                                #已获取此位置心情
                                if restMood <= self.moodThreshold:
                                    #已降到阈值以下
                                    self.click((eachRoom[0] + self.operatorPosOffset[eachOperator], eachRoom[1]))
                                    freeCount += 1
                    self.swipe((550, lower[1]), (550, upper[1] + 70))

                    lastScreen = None
                    while True:
                        #判断滑动已完全停止
                        self.getScreen()
                        if lastScreen != None:
                            isScreenStop = pictureFind.matchImg(self.screenShot, lastScreen, confidencevalue=0.999)
                            if isScreenStop != None:
                                break
                            else:
                                lastScreen = pictureFind.picRead(self.screenShot)
                                sleep(0.5)
                        else:
                            lastScreen = pictureFind.picRead(self.screenShot)

            else:
                tryCount += 1
                if tryCount > 3:
                    print('err:未能匹配到房间位置')
                    return -1
        return freeCount

if __name__ == '__main__':
    adb = adbCtrl.Adb(getcwd() + '/res/ico.ico', getcwd() + '/bin/adb')
    adb.connect()
    test = Logistic(adb, getcwd())
    test.freeOperator()
