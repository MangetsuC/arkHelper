from os import getcwd
from sys import path
from time import sleep, time

from cv2 import resize

path.append(getcwd())
from foo.pictureR import pictureFind, ocr, wordsTemplate
from foo.adb import adbCtrl
from foo.logisticDepartment import ruleEncoder

class Room:
    def __init__(self, adb, roomName, roomDirect):
        self.adb = adb
        self.screenShot = getcwd() + '/bin/adb/arktemp.png'

        self.roomName = roomName
        self.roomDirect = roomDirect
        self.roomCoor = []

        self.runFlag = False

    def getScreen(self):
        self.adb.screenShot()

    def click(self, picResult):
        self.adb.click(picResult[0], picResult[1])

    def swipe(self, startPoint, endPoint, lastTime = 200):
        self.adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = lastTime)

    def clickCenter(self):
        self.click((720, 405))

    def clickBack(self):
        self.click((100,50))

    def checkSubmitting(self):
        while True:
            self.getScreen()
            if pictureFind.matchImg(self.screenShot, submitting, confidencevalue = 0.7) == None: #等待提交完成
                break

    def swipeToOperatorHead(self):
        '选择干员界面回到最左侧'
        lastScreen = None
        while True:
            #判断滑动已完全停止
            if lastScreen != None:
                self.swipe((500, 400), (1300, 400))
                sleep(2)
                self.getScreen()
                isScreenStop = pictureFind.matchImg(self.screenShot, lastScreen, confidencevalue=0.99, targetSize = (0,0))
                if isScreenStop != None:
                    break
                else:
                    lastScreen = pictureFind.picRead(self.screenShot)
                    sleep(0.5)
            else:
                self.getScreen()
                lastScreen = pictureFind.picRead(self.screenShot)
        return 0

    def swipeToNextOperatorPage(self):
        '往右划一些'
        lastScreen = None
        self.swipe((1000, 400), (600, 400), lastTime = 500)
        self.swipe((600, 400), (600, 400), lastTime = 200)
        while True:
            #判断滑动已完全停止
            self.getScreen()
            if lastScreen != None:
                isScreenStop = pictureFind.matchImg(self.screenShot, lastScreen, confidencevalue=0.99, targetSize = (0,0))
                if isScreenStop != None:
                    break
                else:
                    lastScreen = pictureFind.picRead(self.screenShot)
                    sleep(0.5)
            else:
                lastScreen = pictureFind.picRead(self.screenShot)
        return 0

    def backToOneLayer(self, layerMark):
        '回到某一层'
        startTime = time()
        while pictureFind.matchImg(self.screenShot, layerMark, confidencevalue = 0.7) == None:
            self.clickBack()
            self.getScreen()
            if time() - startTime > 30:
                return -1
        return 0

    def findOpOnScreen(self, operatorName):
        '找到指定干员在屏幕上的位置'
        self.getScreen()
        picInfo = pictureFind.matchImg(self.screenShot, wordsTemplate.getTemplatePic_CH(operatorName, 30), 
                                        targetSize = (1920, 1080), confidencevalue = 0.65)
        if picInfo != None:
            return ((int(picInfo['result'][0]/1920*1440), int(picInfo['result'][1]/1920*1440)), 
                    (int(picInfo['rectangle'][3][0]/1920*1440), int(picInfo['rectangle'][3][1]/1920*1440)))
        else:
            return False

    def checkOpAvailable(self, basePoint):
        workingPic = pictureFind.matchImg_roi(self.screenShot, working,
                                                roi = (basePoint[0] - 130, basePoint[1] - 162, 135, 85),
                                                confidencevalue = 0.6)#以干员名称右下角为基准点的偏移量
        if workingPic != None:
            return False
        restingPic = pictureFind.matchImg_roi(self.screenShot, resting,
                                                roi = (basePoint[0] - 130, basePoint[1] - 162, 135, 85),
                                                confidencevalue = 0.6)
        if restingPic != None:
            return False
        return True

    def checkSwipeEnd(self, operatorList):
        '判断是否还需要继续右划'
        self.getScreen()
        workingPic = pictureFind.matchImg(self.screenShot, working, confidencevalue = 0.7)
        restingPic = pictureFind.matchImg(self.screenShot, resting, confidencevalue = 0.7)
        if workingPic != None:
            if workingPic['result'][0] > 800:
                return False
        if restingPic != None:
            if restingPic['result'][0] > 800:
                return False
        thisScreen = pictureFind.imreadCH(self.screenShot)
        thisScreen = resize(thisScreen, (1920, 1080))
        for i in operatorList:
            i = i.strip('+').strip('|').strip('*').strip('$')
            if pictureFind.matchImg(thisScreen, wordsTemplate.getTemplatePic_CH(i, 30),
                                targetSize = (0, 0), confidencevalue = 0.7) != None:
                return True
        return False

    def backToMain(self):
        '回到基建首页'
        return self.backToOneLayer(overviewEntry)

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
        vacancyCoor = pictureFind.matchMultiImg(self.screenShot, operatorEnter, confidencevalue = 0.7)
        if vacancyCoor != None:
            vacancyCoor = vacancyCoor[0]
            if vacancyCoor != None:
                return len(vacancyCoor)
        return 0

    def dispatchOperator(self, roomRule, roomType, needNum):
        self.click((1170, 155))
        unFit = []
        myRuleList = roomRule.copy()
        myRuleList.reverse()
        while needNum != 0:
            if not self.runFlag:
                break
            try:
                opFinding = myRuleList.pop()
                print(f'正在寻找干员{opFinding}')
            except IndexError:
                break
            if '+' in opFinding:
                availableNum = 0
                tempOpList = [opFinding]
                while True:
                    tempOp = myRuleList.pop()
                    tempOpList.append(tempOp)
                    if not ('+' in tempOp):
                        break
                if len(tempOpList) > needNum:
                    #组合人数大于空位数
                    unFit.extend(tempOpList)
                    continue
                else:
                    for eachOp in tempOpList:
                        if '|' in eachOp or '*' in eachOp or '$' in eachOp:
                            if not (roomType in eachOp):
                                availableNum = -1 #组合类型与房间类型不匹配 为什么不能让我方便的跳出双层循环！
                                break
                        realName = eachOp.strip('+').strip('|').strip('*').strip('$')
                        self.swipeToOperatorHead()
                        self.getScreen()
                        opCoor = self.findOpOnScreen(realName) #先寻找一次
                        if opCoor:
                            if self.checkOpAvailable(opCoor[1]):
                                availableNum += 1
                            else:
                                break
                        else:
                            isAvailable = True
                            while self.checkSwipeEnd(myRuleList): #初次找不到再继续右划
                                self.getScreen()
                                opCoor = self.findOpOnScreen(opFinding)
                                if opCoor:
                                    if self.checkOpAvailable(opCoor[1]):
                                        availableNum += 1
                                        break
                                    else:
                                        isAvailable = False
                                        break
                            else:
                                break
                            if not isAvailable:
                                break #有组合内的干员不可选取 不再检查其它角色
                    if availableNum == -1:
                        unFit.extend(tempOpList)
                        continue
                    elif availableNum == len(tempOpList):
                        for eachOp in tempOpList:
                            myRuleList.append(eachOp.strip('+').strip('|').strip('*').strip('$')) 
                            #把这几位干员以非组合的方式重新压回规则
            else:
                if '|' in opFinding or '*' in opFinding or '$' in opFinding:
                    if not (roomType in opFinding):
                        unFit.append(opFinding)
                        continue
                opFinding = opFinding.strip('+').strip('|').strip('*').strip('$')
                self.swipeToOperatorHead()
                self.getScreen()
                opCoor = self.findOpOnScreen(opFinding) #先寻找一次
                if opCoor:
                    if self.checkOpAvailable(opCoor[1]):
                        self.click(opCoor[0])
                        needNum -= 1
                else:
                    while self.checkSwipeEnd(myRuleList): #初次找不到再继续右划
                        self.swipeToNextOperatorPage()
                        self.getScreen()
                        opCoor = self.findOpOnScreen(opFinding)
                        if opCoor:
                            if self.checkOpAvailable(opCoor[1]):
                                self.click(opCoor[0])
                                needNum -= 1
                            break
        while self.runFlag: #确认
            self.click((1325, 760))
            self.getScreen()
            if pictureFind.matchImg_roi(self.screenShot, wordsTemplate.getTemplatePic_CH(self.roomName, 28), 
                                        roi = (475, 25, 170, 35), confidencevalue = 0.7) != None:
                break
        myRuleList.extend(reversed(unFit))
        return list(reversed(myRuleList))

    def stop(self):
        self.runFlag = False

    def startPermission(self):
        self.runFlag = True


class Manufactory(Room):
    '制造站'
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

class Trade(Room):
    '贸易站'
    def __init__(self, adb):
        super(Trade, self).__init__(adb, '贸易站', 'LEFT')
        self.layer1Mark = pictureFind.picRead(getcwd() + '/res/logistic/trade/tradeLayer1Mark.png')
        self.money = pictureFind.picRead(getcwd() + '/res/logistic/trade/money.png')
        self.stone = pictureFind.picRead(getcwd() + '/res/logistic/trade/stone.png')

    def checkType(self):
        ans = False
        for i in range(5):
            self.click((80, 700))
            self.getScreen()
            isMoney = pictureFind.matchImg_roi(self.screenShot, self.money, roi = (1060, 625, 255, 165),
                                                confidencevalue = 0.7)
            isStone = pictureFind.matchImg_roi(self.screenShot, self.stone, roi = (1060, 625, 255, 165),
                                                confidencevalue = 0.7)
            if isMoney != None:
                ans = '$'
                break
            if isStone != None:
                ans = '*'
                break
        self.backToOneLayer(self.layer1Mark) #认为不会出错
        return ans

class PowerRoom(Room):
    '发电站'
    def __init__(self, adb):
        super(PowerRoom, self).__init__(adb, '发电站', 'LEFT')

    def checkType(self):
        return ''

class OfficeRoom(Room):
    '办公室'
    def __init__(self, adb):
        super(OfficeRoom, self).__init__(adb, '办公室', 'RIGHT')

    def checkType(self):
        return ''

class ReceptionRoom(Room):
    '会客室'
    #不完整，暂未完成自动收发线索功能
    def __init__(self, adb):
        super(ReceptionRoom, self).__init__(adb, '会客室', 'RIGHT')

    def checkType(self):
        sleep(10) #低效，为了不被右上角弹出来的各类通知遮挡，后续调整
        return ''

operatorEnter = pictureFind.picRead(getcwd() + '/res/logistic/general/operatorEnter.png') #进驻界面的空位
overviewEntry = pictureFind.picRead(getcwd() + '/res/logistic/general/overviewEntry.png') #进驻总览按钮
resting = pictureFind.picRead(getcwd() + '/res/logistic/general/resting.png')
working = pictureFind.picRead(getcwd() + '/res/logistic/general/working.png')
submitting = pictureFind.picRead(getcwd() + '/res/logistic/general/submitting.png')

if __name__ == '__main__':
    rule = ruleEncoder.RuleEncoder(getcwd() + '/logisticRule.ahrule')
    adb = adbCtrl.Adb(getcwd() + '/res/ico.ico', getcwd() + '/bin/adb')
    adb.connect()
    testT = Trade(adb)
    testT.findAllRooms()
    tempRule = rule.getOneRule('示例配置')['贸易站']
    while testT.enterRoom() > 0:
        roomType = testT.checkType()
        vacancyNum = testT.checkRoomVacancy()
        if vacancyNum > 0:
            tempRule = testT.dispatchOperator(tempRule, roomType, vacancyNum)
        testT.backToMain()

