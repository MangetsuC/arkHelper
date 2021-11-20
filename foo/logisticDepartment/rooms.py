from os import getcwd
from sys import path
from time import sleep, time
from random import randint

from cv2 import resize

path.append(getcwd())
from foo.pictureR import pictureFind, ocr, wordsTemplate
from foo.adb import adbCtrl
from foo.logisticDepartment import ruleEncoder
from common import user_data
from foo.pictureR.colorDetect import findColorBlock
from common2 import adb

from foo.ocr.ocr import getText, findTextPos, findTextPos_all


class Room:
    def __init__(self, adb, roomName, roomDirect):
        adb = adb

        self.roomName = roomName
        self.roomDirect = roomDirect
        self.roomCoor = []

        self.runFlag = False

    def click(self, picResult):
        adb.click(picResult[0]/1440*adb.screenX, picResult[1]/810*adb.screenY)

    def swipe(self, startPoint, endPoint, lastTime = 200):
        adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = lastTime)

    def clickCenter(self):
        adb.click(adb.screenX/2, adb.screenY/2)

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
            if pictureFind.matchImg(adb.getScreen_std(), submitting, confidencevalue = 0.7) == None: #等待提交完成
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
                screenShot = adb.getScreen_std()
                isScreenStop = pictureFind.matchImg_T(screenShot, lastScreen, confidencevalue=0.99, targetSize = (0,0))
                if isScreenStop != None:
                    break
                else:
                    lastScreen = screenShot
                    sleep(0.5)
            else:
                lastScreen = adb.getScreen_std()
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
            screenShot = adb.getScreen_std()
            if lastScreen is not None:
                isScreenStop = pictureFind.matchImg_T(screenShot, lastScreen, confidencevalue=0.99, targetSize = (0,0))
                if isScreenStop != None:
                    break
                else:
                    lastScreen = screenShot
                    sleep(0.5)
            else:
                lastScreen = adb.getScreen_std()
        return 0

    def backToOneLayer(self, layerMark):
        '回到某一层'
        startTime = time()
        while findTextPos(getText(adb.getScreen_std(True)), [layerMark], []) == None:
            if not self.runFlag:
                break
            adb.clickBack()
            if time() - startTime > 30:
                return -1
        return 0

    def findOpOnScreen(self, operatorName):
        '找到指定干员在屏幕上的位置'
        fontsize = wordsTemplate.getFontSize_name(adb.getResolution())
        picInfo = pictureFind.matchImg(adb.getScreen_std(), wordsTemplate.getTemplatePic_CH(operatorName, fontsize[0]),
                                        targetSize = fontsize[1], confidencevalue = 0.6)
        if picInfo != None:
            return ((int(picInfo['result'][0]/fontsize[1][0]*1440), int(picInfo['result'][1]/fontsize[1][0]*1440)), 
                    (int(picInfo['rectangle'][3][0]/fontsize[1][0]*1440), int(picInfo['rectangle'][3][1]/fontsize[1][0]*1440)))
        else:
            return False

    def checkOpAvailable(self, basePoint):
        screenShot = adb.getScreen_std()
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
        screenShot = adb.getScreen_std()
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
        return self.backToOneLayer('进驻总览')

    def findAllRooms(self):
        '找到本类所有房间'
        self.swipeScreen()
        ans = findTextPos_all(getText(adb.getScreen_std(True)), [self.roomName], [])
        for i in ans:
            self.roomCoor.append(i[0])

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
            startTime = time()
            while True:
                if not self.runFlag:
                    break
                if time() - startTime > 5:
                    return 2 #房间名称不匹配
                adb.click(oneRoom[0], oneRoom[1])
                if findTextPos(getText(adb.getScreen_std(True)), ['设施信息'], []) != None:
                    self.clickCenter()
                    break
            return 1
        return -1

    def checkRoomVacancy(self):
        '检查房间有几个空位'
        ocrResult = getText(adb.getScreen_std(True))
        ans = findTextPos(ocrResult, ['进驻信息'], [])
        if ans != None:
            adb.click(ans[0][0], ans[0][1])
        
        for i in range(5):
            if findTextPos(getText(adb.getScreen_std(True)), ['当前房间入住'], []) != None:
                break

        ocrResult = getText(adb.getScreen_std(True))
        ans = findTextPos_all(ocrResult, ['进驻'], ['信', '息', '人'])
        if ans != None:
            return len(ans)
        else:
            return 0

    def dispatchOperator(self, roomRule, roomType, needNum):
        ocrResult = getText(adb.getScreen_std(True))
        ans = findTextPos(ocrResult, ['进驻'], ['信息'])
        if ans != None:
            adb.click(ans[0][0], ans[0][1])
        else:
            return 

        unFit = []
        searched = []
        myRuleList = roomRule.copy()
        myRuleList.reverse()

        temp = getText(adb.getScreen_std(True))
        leftLine = adb.homePos[0]
        ocrResult = []
        for i in temp:
            if i[0][0][0] > leftLine:
                ocrResult.append(i)

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

                        ans = findTextPos(ocrResult, [realName], [])
                        if ans != None:
                            availableNum += 1
                        else:
                            availableNum = -1
                            break
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
                ans = findTextPos(ocrResult, [opFinding], [])
                if ans != None:
                    adb.click(ans[0][0], ans[0][1])
                    if findTextPos(getText(adb.getScreen_std(True)), ['点击干员', '查看详情'], []) != None:
                        adb.click(ans[0][0], ans[0][1])
                        continue
                    needNum -= 1
                    print(f'在{self.roomName}布置了干员{opFinding}')
                
        while self.runFlag: #确认
            ocrResult = getText(adb.getScreen_std(True))
            ans = findTextPos(ocrResult, ['确认'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
            
            if findTextPos(getText(adb.getScreen_std(True)), [self.roomName], []) != None:
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
        img = adb.getScreen_std(True)
        ocrResult = getText(img)
        for i in ['作战记录', '赤金', '源石']:
            if findTextPos(ocrResult, [i], []) != None:
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
            adb.click(10, adb.screenY - 10)
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            temp = findTextPos(ocrResult, ['龙门', '开采'], [])
            if temp != None:
                if '龙门' in temp[2]:
                    ans = '$'
                else:
                    ans = '*'
                break
            else:
                ans = '$' #默认龙门币
        self.backToOneLayer('设施信息') #认为不会出错
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
        self.sendClue = pictureFind.picRead(getcwd() + '/res/logistic/meeting/sendClue.png')
        self.noExtraClue = pictureFind.picRead(getcwd() + '/res/logistic/meeting/noExtraClue.png')

        self.sendBtn = [(1340, 145), (1340, 315), (1340, 470), (1340, 645)]

    def bactToMeetingIndex(self, point = (350, 700)):
        self.backToOneLayer('设施信息')
        adb.click(10, adb.screenY - 10)

    def setClue(self):
        img = adb.getScreen_std(True)
        ocrResult = getText(img)

        ans = findTextPos_all(ocrResult, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], [])
        lackClues = []
        for i in ans:
            if i[2].isdigit():
                lackClues.append(i)
        
        for i in lackClues:
            adb.click(i[0][0], i[0][1])
            img = adb.getScreen_std(True)
            ocrResult = getText(img)
            ans = findTextPos(ocrResult, ['相关搜集者', '暂无线索'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
            self.bactToMeetingIndex()

    def uniqueFunc(self):
        #会客室特殊操作先暂停使用
        return 
        self.bactToMeetingIndex()

        self.setClue()#先添加一次线索，以便于线索赠送
        self.bactToMeetingIndex((750, 700))

        if user_data.get('logistic.meetingroom.send'):
            #线索赠送
            while pictureFind.matchImg(adb.getScreen_std(), self.sendClue, confidencevalue = 0.7) == None:
                if not self.runFlag:
                    return 
                self.click((1350, 440))

            luckyFriend = self.sendBtn.copy()
            maxPages = 3 #最多只有10个线索，每页4个好友
            while pictureFind.matchImg(adb.getScreen_std(), self.noExtraClue, confidencevalue = 0.6) == None:
                if maxPages == 0:
                    break
                if not self.runFlag:
                    return 
                if luckyFriend == []:
                    self.click((1360, 765))
                    luckyFriend = self.sendBtn.copy()
                    maxPages -= 1
                self.click((100, 250))
                self.click(luckyFriend.pop(randint(0, len(luckyFriend) - 1)))
            while pictureFind.matchImg(adb.getScreen_std(), self.confidential, confidencevalue = 0.7) == None:
                if not self.runFlag:
                    return 
                self.click((1400, 40)) #返回
        

        if user_data.get('logistic.meetingroom.daily'):
            self.click((1350, 205)) #线索收集
            self.click((900, 650))
            self.click((1115, 115))

        if not self.runFlag:
            return 

        self.click((1345, 325)) #接收线索赠送
        self.click((1200, 760))

        if not self.runFlag:
            return 

        self.bactToMeetingIndex((750, 700))

        self.setClue()#添加线索
        if not self.runFlag: return 
        if user_data.get('logistic.meetingroom.use'):
            adb.click(adb.screenX/2, 810/900*adb.screenY)
            #开启线索交流

operatorEnter = pictureFind.picRead(getcwd() + '/res/logistic/general/operatorEnter.png') #进驻界面的空位
overviewEntry = pictureFind.picRead(getcwd() + '/res/logistic/general/overviewEntry.png') #进驻总览按钮
resting = pictureFind.picRead(getcwd() + '/res/logistic/general/resting.png')
working = pictureFind.picRead(getcwd() + '/res/logistic/general/working.png')
submitting = pictureFind.picRead(getcwd() + '/res/logistic/general/submitting.png')
