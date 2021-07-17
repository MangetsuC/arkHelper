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

        self.roomName = roomName
        self.roomDirect = roomDirect
        self.roomCoor = []

        self.runFlag = False

    def click(self, picResult):
        self.adb.click(picResult[0], picResult[1])

    def swipe(self, startPoint, endPoint, lastTime = 200):
        self.adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = lastTime)

    def clickCenter(self):
        self.click((720, 405))

    def clickBack(self):
        self.click((100,50))

    def checkType(self):
        return ''

    def uniqueFunc(self):
        return None

    def checkSubmitting(self):
        while True:
            if not self.runFlag:
                break
            if pictureFind.matchImg(self.adb.getScreen_std(), submitting, confidencevalue = 0.7) == None: #等待提交完成
                break

    def getRealName(self, name):
        prefixSign = ['+', '*', '|', '$', '.']
        while name[0] in prefixSign:
            name = name.strip('+').strip('|').strip('*').strip('$').strip('.')
        return name

    def swipeToOperatorHead(self):
        '选择干员界面回到最左侧'
        lastScreen = None
        while True:
            #判断滑动已完全停止
            if not self.runFlag:
                break
            if lastScreen is not None:
                self.swipe((500, 400), (1300, 400))
                sleep(2)
                screenShot = self.adb.getScreen_std()
                isScreenStop = pictureFind.matchImg(screenShot, lastScreen, confidencevalue=0.99, targetSize = (0,0))
                if isScreenStop != None:
                    break
                else:
                    lastScreen = screenShot
                    sleep(0.5)
            else:
                lastScreen = self.adb.getScreen_std()
        return 0

    def swipeToNextOperatorPage(self):
        '往右划一些'
        lastScreen = None
        self.swipe((1000, 400), (600, 400), lastTime = 500)
        self.swipe((600, 400), (600, 400), lastTime = 200)
        while True:
            #判断滑动已完全停止
            if not self.runFlag:
                break
            screenShot = self.adb.getScreen_std()
            if lastScreen is not None:
                isScreenStop = pictureFind.matchImg(screenShot, lastScreen, confidencevalue=0.99, targetSize = (0,0))
                if isScreenStop != None:
                    break
                else:
                    lastScreen = screenShot
                    sleep(0.5)
            else:
                lastScreen = self.adb.getScreen_std()
        return 0

    def backToOneLayer(self, layerMark):
        '回到某一层'
        startTime = time()
        while pictureFind.matchImg(self.adb.getScreen_std(), layerMark, confidencevalue = 0.7) is None:
            if not self.runFlag:
                break
            self.clickBack()
            if time() - startTime > 30:
                return -1
        return 0

    def findOpOnScreen(self, operatorName):
        '找到指定干员在屏幕上的位置'
        picInfo = pictureFind.matchImg(self.adb.getScreen_std(), wordsTemplate.getTemplatePic_CH(operatorName, 30),
                                        targetSize = (1920, 1080), confidencevalue = 0.6)
        if picInfo != None:
            return ((int(picInfo['result'][0]/1920*1440), int(picInfo['result'][1]/1920*1440)), 
                    (int(picInfo['rectangle'][3][0]/1920*1440), int(picInfo['rectangle'][3][1]/1920*1440)))
        else:
            return False

    def checkOpAvailable(self, basePoint):
        screenShot = self.adb.getScreen_std()
        workingPic = pictureFind.matchImg_roi(screenShot, working,
                                                roi = (basePoint[0] - 130, basePoint[1] - 162, 135, 85),
                                                confidencevalue = 0.6)#以干员名称右下角为基准点的偏移量
        if workingPic != None:
            return False
        restingPic = pictureFind.matchImg_roi(screenShot, resting,
                                                roi = (basePoint[0] - 130, basePoint[1] - 162, 135, 85),
                                                confidencevalue = 0.6)
        if restingPic != None:
            return False
        return True

    def checkSwipeEnd(self, operatorList):
        '判断是否还需要继续右划'
        screenShot = self.adb.getScreen_std()
        workingPic = pictureFind.matchImg(screenShot, working, confidencevalue = 0.7)
        restingPic = pictureFind.matchImg(screenShot, resting, confidencevalue = 0.7)
        if workingPic != None:
            if workingPic['result'][0] > 800:
                return False
        if restingPic != None:
            if restingPic['result'][0] > 800:
                return False
        thisScreen = pictureFind.imreadCH(screenShot)
        thisScreen = resize(thisScreen, (1920, 1080))
        for i in operatorList:
            i = self.getRealName(i)
            if pictureFind.matchImg(thisScreen, wordsTemplate.getTemplatePic_CH(i, 30),
                                targetSize = (0, 0), confidencevalue = 0.7) != None:
                return True
        return False

    def backToMain(self):
        '回到基建首页'
        print('正在回到基建首页...')
        return self.backToOneLayer(overviewEntry)

    def findAllRooms(self):
        '找到本类所有房间'
        self.swipeScreen()
        picInfo = pictureFind.matchMultiImg(self.adb.getScreen_std(), wordsTemplate.getTemplatePic_CH(self.roomName, 27),
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
        print('正在进入房间...')
        if self.swipeScreen() != -1:
            try:
                oneRoom = self.roomCoor.pop()
            except IndexError:
                return 0
            while True:
                if not self.runFlag:
                    break
                self.click(oneRoom)
                if pictureFind.matchImg_roi(self.adb.getScreen_std(), wordsTemplate.getTemplatePic_CH(self.roomName, 28),
                                            roi = (475, 25, 170, 35), confidencevalue = 0.7) != None:
                    self.clickCenter()
                    break
            return 1
        return -1

    def checkRoomVacancy(self):
        '检查房间有几个空位'
        self.click((75, 325))
        vacancyCoor = pictureFind.matchMultiImg(self.adb.getScreen_std(), operatorEnter, confidencevalue = 0.7)
        if vacancyCoor != None:
            vacancyCoor = vacancyCoor[0]
            if vacancyCoor != None:
                return len(vacancyCoor)
        return 0

    def dispatchOperator(self, roomRule, roomType, needNum):
        self.click((1170, 155))
        unFit = []
        searched = []
        myRuleList = roomRule.copy()
        myRuleList.reverse()
        while needNum != 0:
            if not self.runFlag:
                break
            try:
                opFinding = myRuleList.pop()
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
                        realName = self.getRealName(eachOp)
                        print(f'正在检查干员{realName}的可用状态...')
                        self.swipeToOperatorHead()
                        opCoor = self.findOpOnScreen(realName) #先寻找一次
                        if opCoor:
                            if self.checkOpAvailable(opCoor[1]):
                                availableNum += 1
                            else:
                                print(f'干员{realName}正在工作或休息，组合{tempOpList}不可用')
                                break
                        else:
                            isAvailable = True
                            while self.checkSwipeEnd(myRuleList): #初次找不到再继续右划
                                if not self.runFlag:
                                    break
                                self.swipeToNextOperatorPage()
                                opCoor = self.findOpOnScreen(opFinding)
                                if opCoor:
                                    if self.checkOpAvailable(opCoor[1]):
                                        availableNum += 1
                                        break
                                    else:
                                        isAvailable = False
                                        print(f'干员{realName}正在工作或休息，组合{tempOpList}不可用')
                                        break
                            else:
                                print(f'干员{realName}暂不可用，组合{tempOpList}不可用')
                                break
                            if not isAvailable:
                                break #有组合内的干员不可选取 不再检查其它角色
                    if availableNum == -1:
                        unFit.extend(tempOpList)
                        continue
                    elif availableNum == len(tempOpList):
                        for eachOp in tempOpList:
                            myRuleList.append('.' + self.getRealName(eachOp)) 
                            #把这几位干员以非组合的方式重新压回规则
            else:
                if opFinding in searched:
                    continue
                searched.append(opFinding)
                if '|' in opFinding or '*' in opFinding or '$' in opFinding:
                    if not (roomType in opFinding):
                        unFit.append(opFinding)
                        continue
                opFinding = self.getRealName(opFinding)
                print(f'正在寻找干员{opFinding}...')
                self.swipeToOperatorHead()
                opCoor = self.findOpOnScreen(opFinding) #先寻找一次
                if opCoor:
                    if self.checkOpAvailable(opCoor[1]):
                        self.click(opCoor[0])
                        needNum -= 1
                        print(f'干员{opFinding}可用，已选定')
                    else:
                        print(f'发现干员{opFinding}正在工作或休息，跳过')
                else:
                    while self.checkSwipeEnd(myRuleList): #初次找不到再继续右划
                        if not self.runFlag:
                            break
                        self.swipeToNextOperatorPage()
                        opCoor = self.findOpOnScreen(opFinding)
                        if opCoor:
                            if self.checkOpAvailable(opCoor[1]):
                                self.click(opCoor[0])
                                needNum -= 1
                                print(f'干员{opFinding}可用，已选定')
                            else:
                                print(f'发现干员{opFinding}正在工作或休息，跳过')
                            break
                    else:
                        print(f'干员{opFinding}不可用')
        while self.runFlag: #确认
            self.click((1325, 760))
            if pictureFind.matchImg_roi(self.adb.getScreen_std(), wordsTemplate.getTemplatePic_CH(self.roomName, 28),
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
        screenShot = self.adb.getScreen_std()
        for i in ['作战记录', '赤金', '源石']:
            if pictureFind.matchImg_roi(screenShot, wordsTemplate.getTemplatePic_CH(i, 28),
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
            screenShot = self.adb.getScreen_std()
            isMoney = pictureFind.matchImg_roi(screenShot, self.money, roi = (1060, 625, 255, 165),
                                                confidencevalue = 0.7)
            isStone = pictureFind.matchImg_roi(screenShot, self.stone, roi = (1060, 625, 255, 165),
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


class OfficeRoom(Room):
    '办公室'
    def __init__(self, adb):
        super(OfficeRoom, self).__init__(adb, '办公室', 'RIGHT')

class ReceptionRoom(Room):
    '会客室'
    #不完整，暂未完成自动收发线索功能
    def __init__(self, adb):
        super(ReceptionRoom, self).__init__(adb, '会客室', 'RIGHT')
        self.clear = pictureFind.picRead(getcwd() + '/res/logistic/meeting/clear.png')
        self.opened = pictureFind.picRead(getcwd() + '/res/logistic/meeting/opened.png')
        self.confidential = pictureFind.picRead(getcwd() + '/res/logistic/meeting/confidential.png')
        self.clues = [pictureFind.picRead(getcwd() + f'/res/logistic/meeting/{x}.png') for x in range(1, 8)]
        self.noClue = pictureFind.picRead(getcwd() + '/res/logistic/meeting/noClue.png')
        self.communication = pictureFind.picRead(getcwd() + '/res/logistic/meeting/communication.png')

    def checkRoomVacancy(self):
        '检查房间有几个空位'
        self.click((75, 325))
        while True:
            screenshot = self.adb.getScreen_std()
            if pictureFind.matchImg(screenshot, self.opened, confidencevalue = 0.7) == None:
                self.click((75, 325))
            else:
                if pictureFind.matchImg(screenshot, self.clear, confidencevalue = 0.7) != None:
                    break
        vacancyCoor = pictureFind.matchMultiImg(self.adb.getScreen_std(), operatorEnter, confidencevalue = 0.7)
        if vacancyCoor != None:
            vacancyCoor = vacancyCoor[0]
            if vacancyCoor != None:
                return len(vacancyCoor)
        return 0

    def bactToMeetingIndex(self, point = (350, 700)):
        while pictureFind.matchImg(self.adb.getScreen_std(), self.confidential, confidencevalue = 0.7) == None:
            self.click(point)
            if pictureFind.matchImg(self.adb.getScreen_std(), self.communication, confidencevalue = 0.7) != None:
                self.backToOneLayer(self.confidential)

    def uniqueFunc(self):
        self.bactToMeetingIndex()

        self.click((1350, 205)) #线索收集
        self.click((900, 650))
        self.click((1115, 115))

        self.click((1345, 325)) #接收线索赠送
        self.click((1200, 760))

        self.bactToMeetingIndex((750, 700))

        clueNotExit = 0
        isUIDeviate= False
        for clue in self.clues: #添加线索
            lackClue = pictureFind.matchImg(self.adb.getScreen_std(), clue, confidencevalue = 0.7)
            if lackClue != None:
                isUIDeviate = True
                self.click(lackClue['result'])
                if pictureFind.matchImg_roi(self.adb.getScreen_std(), self.noClue, (1080, 350, 240, 110), 
                    confidencevalue = 0.7) == None:
                    self.click((1150, 270))
                else:
                    clueNotExit += 1
        if clueNotExit == 0:
            if isUIDeviate:
                self.click((450, 735))
            else:
                self.click((780, 735))
            #开启线索交流

operatorEnter = pictureFind.picRead(getcwd() + '/res/logistic/general/operatorEnter.png') #进驻界面的空位
overviewEntry = pictureFind.picRead(getcwd() + '/res/logistic/general/overviewEntry.png') #进驻总览按钮
resting = pictureFind.picRead(getcwd() + '/res/logistic/general/resting.png')
working = pictureFind.picRead(getcwd() + '/res/logistic/general/working.png')
submitting = pictureFind.picRead(getcwd() + '/res/logistic/general/submitting.png')
