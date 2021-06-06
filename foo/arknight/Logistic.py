from os import getcwd, listdir
from sys import path
from time import sleep

path.append(getcwd())
from foo.adb import adbCtrl
from foo.pictureR import pictureFind, ocr, wordsTemplate

class Logistic:
    def __init__(self, adb, cwd):
        self.adb = adb
        self.cwd = cwd
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'

        self.similarChar = {'巧':15}
        self.operatorPosOffset = [757-1355, 885-1355, 1009-1355, 1137-1355, 1264-1355]
        self.moodsPos = [(353, 577, 87, 35), (353, 614, 87, 35), (353, 650, 87, 35), (353, 686, 87, 35), (353, 722, 87, 35)]

        self.moodThreshold = 0
        self.enableRooms = ['制造站', '贸易站', '发电站', '办公室', '会客室']

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
        dormCount = 0
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
                        if roomName not in self.enableRooms:
                            if roomName == '宿舍':
                                isDorm = True
                                dormCount += 1
                                if dormCount >= 4:
                                    isLastTurn = True
                        self.click((eachRoom[0] - 785, eachRoom[1] + 6))
                        self.getScreen()
                        #if isDorm:
                        #    moods = self.getDormMoods()
                        #else:
                        moods = ocr.ocr_operatorMood(self.screenShot, roi = (355, 576.5, 85, 180))
                        for eachOpMood in range(len(moods)):
                            if moods[eachOpMood] > -1:
                                #该位置有人
                                if (isDorm and moods[eachOpMood] == 24) or \
                                    ((not isDorm) and moods[eachOpMood] <= self.moodThreshold):
                                    #已降到阈值以下 或 宿舍满心情
                                    self.click((eachRoom[0] + self.operatorPosOffset[eachOpMood], eachRoom[1]))
                                    freeCount += 1
                    if not isLastTurn:
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

    def findOpOnScreen(self, operatorName):
        self.getScreen()
        picInfo = pictureFind.matchImg(self.screenShot, wordsTemplate.getTemplatePic_CH(operatorName, 23), confidencevalue = 0.7)
        if picInfo != None:
            return picInfo['result']
        else:
            return False
        

if __name__ == '__main__':
    adb = adbCtrl.Adb(getcwd() + '/res/ico.ico', getcwd() + '/bin/adb')
    adb.connect()
    test = Logistic(adb, getcwd())
    test.freeOperator()
    #print(test.findOpOnScreen('梓兰'))
