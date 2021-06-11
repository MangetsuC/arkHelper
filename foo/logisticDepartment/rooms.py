from os import getcwd
from sys import path
from time import sleep

path.append(getcwd())
from foo.pictureR import pictureFind, ocr, wordsTemplate
from foo.adb import adbCtrl

class Room:
    def __init__(self, adb, roomName, roomDirect):
        self.adb = adb
        self.screenShot = getcwd() + '/bin/adb/arktemp.png'

        self.roomName = roomName
        self.roomDirect = roomDirect
        self.roomCoor = []

        self.operatorEnter = pictureFind.picRead(getcwd() + '/res/logistic/general/operatorEnter.png')
        self.overviewEntry = pictureFind.picRead(getcwd() + '/res/logistic/general/overviewEntry.png')

    def getScreen(self):
        self.adb.screenShot()

    def click(self, picResult):
        self.adb.click(picResult[0], picResult[1])

    def swipe(self, startPoint, endPoint):
        self.adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = 200)

    def clickCenter(self):
        self.click((720, 405))

    def clickBack(self):
        self.click((100,50))

    def swipeToOperatorHead(self):
        '选择干员界面回到最左侧'
        lastScreen = None
        while True:
            #判断滑动已完全停止
            self.swipe((500, 400), (1300, 400))
            sleep(2)
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
        return 0

    def backToOneLevel(self, layerMark):
        '回到某一层'
        tryTime = 0
        while pictureFind.matchImg(self.screenShot, layerMark, confidencevalue = 0.7) == None:
            self.clickBack()
            self.getScreen()
            tryTime += 1
            if tryTime > 5:
                return -1
        return 0

    def findOpOnScreen(self, operatorName):
        '找到指定干员在屏幕上的位置'
        self.getScreen()
        picInfo = pictureFind.matchImg(self.screenShot, wordsTemplate.getTemplatePic_CH(operatorName, 30), 
                                        targetSize = (1920, 1080), confidencevalue = 0.7)
        if picInfo != None:
            return (int(picInfo['result'][0]/1920*1440), int(picInfo['result'][1]/1920*1440))
        else:
            return False

    def backToMain(self):
        '回到基建首页'
        return self.backToOneLevel(self.overviewEntry)

    def findAllRooms(self):
        '找到本类所有房间'
        self.swipeScreen()
        self.getScreen()
        picInfo = pictureFind.matchMultiImg(self.screenShot, wordsTemplate.getTemplatePic_CH(self.roomName, 27), 
                                            confidencevalue = 0.5)
        if picInfo != None:
            picInfo = picInfo[0]
            if picInfo != None:
                self.roomCoor.extend(picInfo)

        return 0

    def swipeScreen(self):
        '基建移到左侧或右侧'
        if self.roomDirect == 'LEFT':
            self.swipe((100, 400), (1200, 400))
            return 0
        elif self.roomDirect == 'RIGHT':
            self.swipe((1200, 400), (100, 400))
            return 0
        else:
            return -1

    def enterRoom(self):
        '进入房间'
        if self.swipeScreen() != -1:
            try:
                oneRoom = self.roomCoor.pop()
            except IndexError:
                return 0
            while True:
                self.click(oneRoom)
                self.getScreen()
                if pictureFind.matchImg_roi(self.screenShot, wordsTemplate.getTemplatePic_CH(self.roomName, 28), 
                                            roi = (475, 25, 170, 35), confidencevalue = 0.7) != None:
                    self.clickCenter()
                    break
            return 1
        return -1

    def checkRoomVacancy(self):
        self.click((75, 325))
        self.getScreen()
        vacancyCoor = pictureFind.matchMultiImg(self.screenShot, self.operatorEnter, confidencevalue = 0.7)
        if vacancyCoor != None:
            vacancyCoor = vacancyCoor[0]
            if vacancyCoor != None:
                return len(vacancyCoor)
        return 0

    def dispatchOperator(self):
        self.click((1170, 155))


class Manufactory(Room):
    def __init__(self, adb):
        super(Manufactory, self).__init__(adb, '制造站', 'LEFT')

    def checkType(self):
        trans = {'作战记录':'|', '赤金':'$', '源石':'*'}
        self.getScreen()
        for i in ['作战记录', '赤金', '源石']:
            if pictureFind.matchImg_roi(self.screenShot, wordsTemplate.getTemplatePic_CH(i, 28),
                                        roi = (150, 685, 200, 50), confidencevalue = 0.7) != None:
                return trans[i]
        else:
            return False

if __name__ == '__main__':
    adb = adbCtrl.Adb(getcwd() + '/res/ico.ico', getcwd() + '/bin/adb')
    adb.connect()
    testM = Manufactory(adb)
    testM.findAllRooms()
    while testM.enterRoom() > 0:
        print(testM.checkType())
        print(testM.checkRoomVacancy())
        testM.dispatchOperator()
        testM.swipeToOperatorHead()
        testM.backToMain()