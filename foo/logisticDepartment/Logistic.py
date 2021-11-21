from os import getcwd
from sys import path
from time import sleep, time
from re import compile as recompile

from cv2 import TermCriteria_COUNT

path.append(getcwd())
from foo.adb import adbCtrl
from foo.pictureR import pictureFind, ocr
from foo.pictureR.colorDetect import findColorBlock
from foo.logisticDepartment import rooms, ruleEncoder
from common2 import adb

from foo.ocr.ocr import getText, findTextPos, findTextPos_all

class Logistic:
    def __init__(self, defaultRuleName, rule, moodThreshold = 0, dormThreshold = 24):
        self.cwd = getcwd()
        self.screenShot = self.cwd + '/res/gui/launchWindow.png'

        self.runFlag = False

        self.operatorPosOffset = [757-1355, 885-1355, 1009-1355, 1137-1355, 1264-1355]
        self.opPos = None
        self.seperator = None
        self.moodsPos = [(353, 577, 87, 35), (353, 614, 87, 35), (353, 650, 87, 35), (353, 686, 87, 35), (353, 722, 87, 35)]
        self.relaxPos = self.getOpPos(12)

        self.moodThreshold = moodThreshold #撤下阈值
        self.dormThreshold = dormThreshold #上班阈值
        self.enableRooms = ['制造站', '贸易站', '发电站', '办公室', '会客室']

        self.rooms = {  '制造站':rooms.Manufactory(adb),
                        '贸易站':rooms.Trade(adb),
                        '发电站':rooms.PowerRoom(adb),
                        '办公室':rooms.OfficeRoom(adb),
                        '会客室':rooms.ReceptionRoom(adb)}

        self.ruleName = defaultRuleName
        self.rule = rule

        self.resourceInit()

    def getOpPos(self, num):
        baseX = 540
        baseY = [240, 550]
        pos = []
        for i in range(num-1, -1, -1):
            pos.append((baseX + int(i/2)*160, baseY[i%2]))
        return pos

    def getRealDormPos(self, workingPos):
        '去除按心情排序界面工作中的干员'
        ans = self.relaxPos.copy()
        if workingPos != None:
            for i in workingPos:
                i = [i[0]/adb.screenY*810, i[1]/adb.screenY*810]
                for j in self.relaxPos:
                    if ((i[0] - j[0])**2 + (i[1] - j[1])**2) < 1000:
                        ans.remove(j)
        ans.reverse()
        if len(ans) >= 5:
            ans = ans[0:5]
        ans.reverse()
        return ans

    def setEnableRooms(self, enableRooms):
        self.enableRooms = enableRooms

    def setRuleName(self, ruleName):
        self.ruleName = ruleName

    def setMoodThreshold(self, threshold):
        self.moodThreshold = threshold

    def setDormThreshold(self, threshold):
        self.dormThreshold = threshold

    def getScreen(self):
        self.screenShot = adb.getScreen_std()

    def click(self, picResult):
        adb.click(picResult[0]/1440*adb.screenX, picResult[1]/810*adb.screenY)

    def clickBack(self):
        adb.clickBack()
        #self.click((100,50))

    def enterLogisticPanel(self):
        print('正在进入基建界面...')
        while self.runFlag:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                ans = findTextPos(ocrResult, ['基建'], [])
                adb.click(ans[0][0], ans[0][1])
                for i in range(5):
                    if not self.runFlag: return 
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['进驻总览'], [])
                    if temp != None:
                        return 
            
            adb.clickHome()
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['基建'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
            
            for i in range(5):
                if not self.runFlag: return 
                temp = findTextPos(getText(adb.getScreen_std(True)), ['进驻总览'], [])
                if temp != None:
                    return 

    def swipe(self, startPoint, endPoint, stopCheck = True):
        adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = 500)
        adb.swipe(endPoint[0], endPoint[1], endPoint[0], endPoint[1], lastTime = 200)
        if stopCheck:
            lastScreen = None
            while True:
                #判断滑动已完全停止
                if not self.runFlag:
                    return -2
                self.getScreen()
                if lastScreen is not None:
                    isScreenStop = pictureFind.matchImg_T(self.screenShot, lastScreen, confidencevalue=0.99, targetSize = 0)
                    if isScreenStop != None:
                        break
                    else:
                        lastScreen = self.screenShot
                        sleep(0.5)
                else:
                    lastScreen = self.screenShot


    def matchPic(self, obj):
        return pictureFind.matchImg_T(self.screenShot, obj, confidencevalue = 0.7)

    def matchMultPics(self, obj):
        ans = pictureFind.matchMultiImg(self.screenShot, obj, confidencevalue = 0.7)
        return ans[0] if ans != None else None

    def backToHome(self):
        while self.runFlag:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                return 
            
            adb.clickHome()
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['首页'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
            
            for i in range(5):
                if not self.runFlag: return 
                temp = findTextPos(getText(adb.getScreen_std(True)), ['采购中心'], [])
                if temp != None:
                    return 

    def resourceInit(self):
        #总览界面
        self.freeOperator_sel = pictureFind.picRead(self.cwd + '/res/logistic/general/freeOperator_sel.png')
        self.freeOperator_unSel = pictureFind.picRead(self.cwd + '/res/logistic/general/freeOperator_unSel.png')
        self.roomFlag = pictureFind.picRead(self.cwd + '/res/logistic/general/roomFlag.png')
        self.roomFlagNormal = pictureFind.picRead(self.cwd + '/res/logistic/general/roomFlagNormal.png')
        self.unDetected = pictureFind.picRead(self.cwd + '/res/logistic/general/unDetected.png')
        self.vacancy = pictureFind.picRead(self.cwd + '/res/logistic/general/vacancy.png')
        self.confirmInDorm = pictureFind.picRead(self.cwd + '/res/logistic/general/confirmInDorm.png')
        #基建主界面
        self.overviewEntry = pictureFind.picRead(self.cwd + '/res/logistic/general/overviewEntry.png')
        self.exit_icon_small = pictureFind.picRead(self.cwd + '/res/logistic/general/exit_icon_small.png')
        self.exit_icon_large = pictureFind.picRead(self.cwd + '/res/logistic/general/exit_icon_large.png')
        self.todoList_unSel = pictureFind.picRead(self.cwd + '/res/logistic/general/todoList_unSel.png')
        self.todoList_sel = pictureFind.picRead(self.cwd + '/res/logistic/general/todoList_sel.png')
        self.todoList_no = pictureFind.picRead(self.cwd + '/res/logistic/general/todoList_no.png')
        self.emergency = pictureFind.picRead(self.cwd + '/res/logistic/general/emergency.png')
        self.exitroom = pictureFind.picRead(self.cwd + '/res/logistic/general/exitroom.png')
        self.submitting = pictureFind.picRead(self.cwd + '/res/logistic/general/submitting.png') #正在连接神经网络
        self.todoListPic = [pictureFind.picRead(self.cwd + '/res/logistic/general/manufactory_output.png'),
                            pictureFind.picRead(self.cwd + '/res/logistic/general/trade_output.png'),
                            pictureFind.picRead(self.cwd + '/res/logistic/general/trust_touch.png')]

        self.working = pictureFind.picRead(getcwd() + '/res/logistic/general/working.png')
        self.resting = pictureFind.picRead(getcwd() + '/res/logistic/general/resting.png')

        self.actBtn = pictureFind.picRead(self.cwd + '/res/panel/other/act.png')
        self.homeBtn = pictureFind.picRead(self.cwd + '/res/panel/other/mainpage.png')
        self.exitComfirm = pictureFind.picRead(self.cwd + '/res/panel/other/confirm.png')

    def enterOverview(self):
        '进入进驻总览'
        class EnterOverviewError(Exception):
            def __str__(self):
                return '进入进驻总览出错'

        print('正在进入进驻总览...')
        for i in range(5):
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos_all(ocrResult, ['进驻总览', '蓝图预览'], [])
            for j in ans:
                if '蓝图预览' in j[2]:
                    return 
            else:
                for j in ans:
                    if '进驻总览' in j[2]:
                        adb.click(j[0][0], j[0][1])
        else:
            raise EnterOverviewError

    def clickFreeOpBtn(self):
        class EnterOverviewError(Exception):
            def __str__(self):
                return '未找到撤下干员按键'


        img = adb.getScreen_std(True)
        ocrResult = getText(img)

        ans = findTextPos(ocrResult, ['撤下干员', '撒下千员', '撤下千员', '撒下干员'], [])
        if ans != None:
            adb.click(ans[0][0], ans[0][1])
            if self.opPos == None:
                rightLine = ans[1][1][0]
                temp = findTextPos(ocrResult, ['进驻总览'], [])
                if temp != None:
                    leftLine = temp[1][1][0]
                    tempAns = []
                    gap = int((rightLine - leftLine)/5)
                    for i in range(5):
                        tempAns.append(int(gap/2) + i*gap + leftLine)
                    self.opPos = tempAns
                    self.seperator = leftLine

        else:
            raise EnterOverviewError

    def getRealRoomName(self, ocrResult):
        for eachRoom in ['控制中枢', '会客室', '贸易站', '制造站', '发电站', '宿舍', '加工站', '办公室', '训练室']:
            if eachRoom in ocrResult:
                return eachRoom
        else:
            return ''

    def waitSubmit(self):
        print('正在等待提交.....', end = '')
        while findTextPos(getText(adb.getScreen_std(True)), ['提交反馈'], []) != None:
            sleep(0.5)
        print('成功')

    def freeOperator(self):
        '撤下心情低于设定值的工作中干员以及心情高于设定值的宿舍中的干员'
        print('开始撤出干员')
        print('正在进入撤下干员模式...')
        freeCount = 0
        tryCount = 0
        
        self.clickFreeOpBtn()

        tryCount = 0
        trainRoomCount = 0
        isLastTurn = False
        while not isLastTurn:
            if not self.runFlag:
                return -2
            ocrResult = getText(adb.getScreen_std(True))

            roomsOnScreen = findTextPos_all(ocrResult, ['控制中枢', '会客室', '贸易站', '制造站', '发电站', '宿舍', '办公室', '加工站', '训练室'], [])
            floorUndetect = findTextPos(ocrResult, ['无法检测到信号'], [])

            if floorUndetect != None:
                isLastTurn = True
            if roomsOnScreen != []:
                tryCount = 0
                roomsOnScreen.sort(key = lambda x:x[0][1])
                if len(roomsOnScreen) >= 1:
                    if len(roomsOnScreen) == 1:
                        isLastTurn = True
                    upper = roomsOnScreen[0]
                    lower = roomsOnScreen[-1]
                    for eachRoom in roomsOnScreen:
                        if not self.runFlag:
                            return -2
                        isDorm = False
                        roomName = self.getRealRoomName(eachRoom[2])
                        if roomName not in self.enableRooms:
                            if roomName == '宿舍':
                                isDorm = True
                            elif roomName == '控制中枢':
                                pass
                            elif roomName == '训练室':
                                trainRoomCount += 1
                                if trainRoomCount >= 2: #为了保证检查到B4的宿舍
                                    isLastTurn = True
                                    print('已到达基建尾部')
                                continue
                            else:
                                continue
                        adb.click(eachRoom[0][0], eachRoom[0][1])

                        ocrResult = getText(adb.getScreen_std(True), 1600)
                        temp = findTextPos_all(ocrResult, ['/24', '未进驻', '注意力'], [])
                        ans = []
                        for i in temp:
                            if i[0][0] < self.seperator:
                                ans.append(i)
                        ans.sort(key = lambda x:x[0][1])
                        moods = []
                        pattern = recompile('[0-9]+/24')
                        for i in ans:
                            if '未进驻' in i[2]:
                                moods.append(-1)
                            elif '注意力' in i[2]:
                                moods.append(0)
                            else:
                                i[2] = i[2].replace('@', '0')
                                temp = pattern.findall(i[2])
                                if len(temp) > 0:
                                    moods.append(int(temp[0].split('/')[0]))

                        if len(moods) > 5:
                            moods = moods[0:5] #草率处理出现重复的情况
                        elif len(moods) < 5:
                            while len(moods) != 5:
                                moods.append(-1)
                        
                        moodsForPrint = []
                        for printMood in range(len(moods)):
                            if moods[printMood] > -1:
                                moodsForPrint.append(str(moods[printMood]))
                            else:
                                moodsForPrint.append('-')
                            if printMood != len(moods) - 1:
                                moodsForPrint.append('|')
                        moodsForPrint = ''.join(moodsForPrint)
                        print(f'(有重复){roomName}各干员心情为:{moodsForPrint}')
                        
                        for eachOpMood in range(len(moods)):
                            if moods[eachOpMood] > -1:
                                #该位置有人
                                if (isDorm and moods[eachOpMood] >= self.dormThreshold) or \
                                    ((not isDorm) and moods[eachOpMood] <= self.moodThreshold):
                                    #已降到阈值以下 或 宿舍满心情
                                    adb.click(self.opPos[eachOpMood], eachRoom[1][2][1])
                                    
                                    self.waitSubmit()

                                    if not isDorm:
                                        freeCount += 1
                    if not isLastTurn:
                        self.swipe((550, lower[0][1]/adb.screenY*810), (550, upper[0][1]/adb.screenY*810))
            else:
                tryCount += 1
                if tryCount > 3:
                    print('err:未能匹配到房间位置')
                    return -1
        return freeCount

    def relaxOperator(self, num):
        '安排指定数量的干员进入宿舍，num需大于0'
        #要求num > 0
        print('开始安排干员休息...')
        print('正在退出撤出干员模式...')
        tryCount = 0
        need2relax = num #需进入宿舍干员数
        relaxing = 0 #已进入宿舍干员数
        
        self.clickFreeOpBtn()

        isLastTurn = False
        while not isLastTurn:
            if not self.runFlag:
                return -2

            ocrResult = getText(adb.getScreen_std(True))

            roomsOnScreen = findTextPos_all(ocrResult, ['控制中枢', '会客室', '贸易站', '制造站', '发电站', '宿舍', '办公室', '加工站', '训练室'], [])
            if roomsOnScreen != None:
                roomsOnScreen.sort(key = lambda x:x[0][1])
                upper = roomsOnScreen[-1]
                lower = roomsOnScreen[0]
                while True:
                    if len(roomsOnScreen) > 0:
                        eachRoom = roomsOnScreen.pop()
                    else:
                        break
                    if not self.runFlag:
                        return -2

                    roomName = self.getRealRoomName(eachRoom[2])
                    if roomName == '宿舍':
                        adb.click(eachRoom[0][0], eachRoom[0][1])

                        ocrResult = getText(adb.getScreen_std(True))
                        temp = findTextPos_all(ocrResult, ['/24', '未进驻', '注意力'], [])
                        ans = []
                        for i in temp:
                            if i[0][0] < self.seperator:
                                ans.append(i)
                        ans.sort(key = lambda x:x[0][1])
                        moods = []
                        pattern = recompile('[0-9]+/24')
                        for i in ans:
                            if '未进驻' in i[2]:
                                moods.append(-1)
                            elif '注意力' in i[2]:
                                moods.append(0)
                            else:
                                moods.append(int(pattern.findall(i[2])[0].split('/')[0]))

                        vacancyNum = moods.count(-1)

                        if vacancyNum > 0:
                            #仍有空位
                            adb.click(self.opPos[0], eachRoom[1][2][1])
                            while findTextPos(getText(adb.getScreen_std(True)), ['确认'], []) == None:
                                sleep(0.5)

                            ocrResult = getText(adb.getScreen_std(True))
                            ans = findTextPos_all(ocrResult, ['工作中', '休息中'], [])
                            notAvaliablePos = []
                            for i in ans:
                                notAvaliablePos.append(i[0])

                            relaxPosThisDorm = self.getRealDormPos(notAvaliablePos)

                            if len(relaxPosThisDorm) != 0:
                                try:
                                    for i in self.dormRange(need2relax - relaxing, vacancyNum, len(relaxPosThisDorm)):
                                        self.click(relaxPosThisDorm[i])
                                        relaxing += 1
                                except IndexError:
                                    if vacancyNum > (i + 1): #进驻数比空房间数少，再进驻一次
                                        roomsOnScreen.append(eachRoom)
                            ans = findTextPos(ocrResult, ['确认'], [])
                            if ans != None:
                                adb.click(ans[0][0], ans[0][1])
                            while findTextPos(getText(adb.getScreen_std(True)), ['蓝图预览'], []) == None:
                                sleep(0.5)
                            #此处应当判断有无回到总览界面
                            
                            if relaxing >= need2relax:
                                print('所有干员已安排进入宿舍')
                                isLastTurn = True
                                break
                    elif roomName == '控制中枢':
                        isLastTurn = True
                        print('已回到基建头部')
                if not isLastTurn:
                    self.swipe((550, lower[0][1]/adb.screenY*810), (550, upper[0][1]/adb.screenY*810))

        return need2relax - relaxing if need2relax > relaxing else 0

    def checkToDoList(self):
        '收获制造站产出，交付订单，获取信赖'
        print('开始收获制造站产出，交付订单，获取信赖')
        ans = findColorBlock(adb.getScreen_std(), [(40, 55), (160, 175), (215, 230)])
        if ans != None:
            for i in range(5):
                adb.click(ans[0], ans[1])
                img = adb.getScreen_std(True)
                ocrResult = getText(img)

                ans = findTextPos(ocrResult, ['待办事项'], [])
                if ans != None:
                    break
            
            ans = findTextPos_all(ocrResult, ['收获', '订单', '干员'], [])
            ans.sort(key = lambda x:x[1], reverse = True)
            for i in ans:
                adb.click(i[0][0], i[0][1])
                self.waitSubmit()






    def resizeLogisticPanel(self):
        '恢复基建页面标准大小'
        self.getScreen()
        smallIcon = self.matchPic(self.exit_icon_small)
        if smallIcon != None:
            self.click(smallIcon['result'])
            while True:
                self.getScreen()
                if self.matchPic(self.exitroom) != None:
                    break
                else:
                    sleep(0.5)
            self.clickBack()
            while True:
                self.getScreen()
                if (self.matchPic(self.exitroom) == None) and (self.matchPic(self.exit_icon_large) != None):
                    break
                else:
                    sleep(0.5)
        return 0

    def checkDormVacancy(self, basePoint):
        '判断此宿舍是否还有空位，返回一个列表，[0]为剩余空位数，[1]为最左侧空位对应的坐标'
        vacancyPos = pictureFind.matchMultiImg_roi(self.screenShot, self.vacancy, 
                                    roi = (basePoint[0] - 652, basePoint[1] - 64, 625, 125), 
                                    confidencevalue = 0.7)
        if vacancyPos != None:
            return [len(vacancyPos), vacancyPos[0]] if 0 < len(vacancyPos) <= 5 else [0, None]
        else:
            return [0, None]

    def dormRange(self, remaingNum, vacancyNum, freeNumOnScreen):
        '适用于填充宿舍时的range函数'
        if remaingNum >= vacancyNum:
            return range(0, vacancyNum)
        else:
            if freeNumOnScreen - 1 < 4:
                if freeNumOnScreen > remaingNum:
                    return range(freeNumOnScreen - remaingNum, freeNumOnScreen)
                else:
                    return range(remaingNum)
            return range(5 - remaingNum, 5)

    def returnToWork(self, room, roomRule):
        room.findAllRooms()
        while True:
            isInCorrectRoom = room.enterRoom()
            if isInCorrectRoom <= 0:
                break
            if not self.runFlag:
                break
            if isInCorrectRoom != 2: #房间名称不匹配
                roomType = room.checkType()
                if not self.runFlag:
                    break
                vacancyNum = room.checkRoomVacancy()
                if not self.runFlag:
                    break
                if vacancyNum > 0:
                    roomRule = room.dispatchOperator(roomRule, roomType, vacancyNum)
                if not self.runFlag:
                    break
                room.uniqueFunc()
            if not self.runFlag:
                break
            room.backToMain()

    def run(self, flag):
        self.runFlag = flag
        self.enterLogisticPanel()
        if not self.runFlag: return 0
        print('正在重新进入，以刷新右上角弹出的信息')
        self.backToHome() #重新进入，刷新掉右上角弹出的提示
        self.enterLogisticPanel()
        if not self.runFlag: return 0
        self.checkToDoList()
        if not self.runFlag: return 0
        print('正在重新进入，以恢复页面大小')
        self.backToHome() #重新进入，恢复页面大小
        if not self.runFlag: return 0
        self.enterLogisticPanel()
        if not self.runFlag: return 0
        self.enterOverview()
        if not self.runFlag: return 0
        need2relax = self.freeOperator()
        if not self.runFlag: return 0
        print(f'需要休息的人数：{need2relax}')
        if need2relax > 0:
            restNum = self.relaxOperator(need2relax)
            if restNum > 0:
                print(f'仍有{restNum}位干员为安排进宿舍休息，后续可能出现将这些干员重新安排进工作的情况')

        if not self.runFlag: return 0
        print('返回基建主页')
        self.enterLogisticPanel()

        if not self.runFlag: return 0
        for eachRoom in self.enableRooms:
            print(f'开始检查{eachRoom}...')
            self.rooms[eachRoom].startPermission()
            self.returnToWork(self.rooms[eachRoom], self.rule.getOneRule(self.ruleName)[eachRoom])
            if not self.runFlag:
                return 0
        self.backToHome()
        self.stop()
        return 0

    def stop(self):
        self.runFlag = False
        for eachRoom in self.enableRooms:
            self.rooms[eachRoom].stop()

if __name__ == '__main__':
    adb = adbCtrl.Adb(getcwd() + '/res/ico.ico', getcwd() + '/bin/adb')
    adb.connect()
    test = Logistic(adb, '示例配置', ruleEncoder.RuleEncoder(getcwd() + '/logisticRule.ahrule'))
    test.run()
    
    
    #print(test.findOpOnScreen('德克萨斯'))
