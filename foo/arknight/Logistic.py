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
        self.relaxPos = [(855, 240), (700, 550), (700, 240), (540, 550), (540, 240)] #宿舍5 4 3 2 1

        self.moodThreshold = 0 #撤下阈值
        self.dormThreshold = 24 #上班阈值
        self.enableRooms = ['制造站', '贸易站', '发电站', '办公室', '会客室']

        self.resourceInit()
    
    def getScreen(self):
        self.adb.screenShot()

    def click(self, picResult):
        self.adb.click(picResult[0], picResult[1])

    def clickBack(self):
        self.click((100,50))

    def swipe(self, startPoint, endPoint, stopCheck = True):
        self.adb.swipe(startPoint[0], startPoint[1], endPoint[0], endPoint[1], lastTime = 500)
        self.adb.swipe(endPoint[0], endPoint[1], endPoint[0], endPoint[1], lastTime = 200)
        if stopCheck:
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


    def matchPic(self, obj):
        return pictureFind.matchImg(self.screenShot, obj, confidencevalue = 0.7)

    def matchMultPics(self, obj):
        ans = pictureFind.matchMultiImg(self.screenShot, obj, confidencevalue = 0.7)
        return ans[0] if ans != None else None


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
        self.exitroom = pictureFind.picRead(self.cwd + '/res/logistic/general/exitroom.png')
        self.submitting = pictureFind.picRead(self.cwd + '/res/logistic/general/submitting.png')
        self.todoListPic = [pictureFind.picRead(self.cwd + '/res/logistic/general/manufactory_output.png'),
                            pictureFind.picRead(self.cwd + '/res/logistic/general/trade_output.png'),
                            pictureFind.picRead(self.cwd + '/res/logistic/general/trust_touch.png')]

        #self.back = pictureFind.picRead(self.cwd + '/res/panel/other/back.png')

    def freeOperator(self):
        '撤下心情低于设定值的工作中干员以及心情高于设定值的宿舍中的干员'
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
        trainRoomCount = 0
        isLastTurn = False
        while not isLastTurn:
            self.getScreen()
            roomsOnScreen = self.matchMultPics(self.roomFlag)
            floorUndetect = self.matchPic(self.unDetected) #基建还未开完
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
                        roomName = ocr.ocr_roomName(self.screenShot, eachRoom)
                        if roomName not in self.enableRooms:
                            if roomName == '宿舍':
                                isDorm = True
                            elif roomName == '训练室':
                                trainRoomCount += 1
                                if trainRoomCount >= 2: #为了保证检查到B4的宿舍
                                    isLastTurn = True
                                continue
                        self.click((eachRoom[0] - 785, eachRoom[1] + 6))
                        self.getScreen()
                        moods = ocr.ocr_operatorMood(self.screenShot, roi = (355, 576.5, 85, 180))
                        for eachOpMood in range(len(moods)):
                            if moods[eachOpMood] > -1:
                                #该位置有人
                                if (isDorm and moods[eachOpMood] >= self.dormThreshold) or \
                                    ((not isDorm) and moods[eachOpMood] <= self.moodThreshold):
                                    #已降到阈值以下 或 宿舍满心情
                                    self.click((eachRoom[0] + self.operatorPosOffset[eachOpMood], eachRoom[1]))
                                    if not isDorm:
                                        freeCount += 1
                    if not isLastTurn:
                        self.swipe((550, lower[1]), (550, upper[1] + 70))
            else:
                tryCount += 1
                if tryCount > 3:
                    print('err:未能匹配到房间位置')
                    return -1
        return freeCount

    def relaxOperator(self, num):
        '安排指定数量的干员进入宿舍，num需大于0'
        #要求num > 0
        tryCount = 0
        need2relax = num #需进入宿舍干员数
        relaxing = 0 #已进入宿舍干员数
        while True:
            #退出撤下干员模式
            self.getScreen()
            freeSel = self.matchPic(self.freeOperator_sel)
            freeUnsel = self.matchPic(self.freeOperator_unSel)
            if freeUnsel == None and freeSel != None:
                self.click(freeSel['result'])
            elif freeSel == None and freeUnsel != None:
                break
            else:
                tryCount += 1
                if tryCount > 3:
                    print('err:退出撤下模式失败')
                    return -1 #出错
                continue
            tryCount = 0

        isLastTurn = False
        while not isLastTurn:
            self.getScreen()
            roomsOnScreen = self.matchMultPics(self.roomFlagNormal)
            if roomsOnScreen != None:
                roomsOnScreen.sort(key = lambda x:x[1], reverse = True)
                upper = roomsOnScreen[-1]
                lower = roomsOnScreen[0]
                for eachRoom in roomsOnScreen:
                    self.getScreen()
                    roomName = ocr.ocr_roomName(self.screenShot, eachRoom)
                    if roomName == '宿舍':
                        vacancyNum = self.checkDormVacancy(eachRoom)
                        if vacancyNum[0] > 0:
                            #仍有空位
                            self.click(vacancyNum[1])
                            while True:
                                self.getScreen()
                                if self.matchPic(self.confirmInDorm) != None:
                                    break
                            
                            for i in self.dormRange(need2relax - relaxing, vacancyNum[0]):
                                self.click(self.relaxPos[i])
                                relaxing += 1
                            self.click((1325, 760)) #确认按钮的坐标
                            #此处应当判断有无回到总览界面
                            while True:
                                self.getScreen()
                                if self.matchPic(self.freeOperator_unSel) != None:
                                    break
                                else:
                                    sleep(0.5)
                            if relaxing >= need2relax:
                                isLastTurn = True
                                break
                    elif roomName == '控制中枢':
                        isLastTurn = True
                if not isLastTurn:
                    self.swipe((550, upper[1] + 70), (550, lower[1]))
            else:
                return -1
        return need2relax - relaxing if need2relax > relaxing else 0

    def checkToDoList(self):
        '收获制造站产出，交付订单，获取信赖'
        self.getScreen()
        isTodoListExist = self.matchPic(self.todoList_unSel)
        isTodoListSel = self.matchPic(self.todoList_sel)
        if isTodoListExist != None or isTodoListSel != None:
            if isTodoListExist:
                self.click(isTodoListExist['result'])
                while True:
                    self.getScreen()
                    if self.matchPic(self.todoList_sel) != None:
                        break
            interactTodo = []
            for i in self.todoListPic:
                interactBtn = self.matchPic(i)
                if interactBtn != None:
                    interactTodo.append(interactBtn['result'])
            interactTodo.sort(key = lambda x:x[0], reverse = True)
            for i in interactTodo:
                self.click(i)
                while True:
                    self.getScreen()
                    if self.matchPic(self.submitting) == None: #等待提交完成
                        break
        return 0

    def checkDormVacancy(self, basePoint):
        vacancyPos = pictureFind.matchMultiImg_roi(self.screenShot, self.vacancy, 
                                    roi = (basePoint[0] - 652, basePoint[1] - 64, 625, 125), 
                                    confidencevalue = 0.7)
        if vacancyPos != None:
            return [len(vacancyPos), vacancyPos[0]] if 0 < len(vacancyPos) <= 5 else [0, None]
        else:
            return [0, None]

    def dormRange(self, remaingNum, vacancyNum):
        if remaingNum >= vacancyNum:
            return range(vacancyNum)
        else:
            return range(vacancyNum - remaingNum, vacancyNum)

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
    test.checkToDoList()
    '''
    need2relax = test.freeOperator()
    print(f'需要休息的人数：{need2relax}')
    if need2relax > 0:
        test.relaxOperator(need2relax)
    '''
    #print(test.findOpOnScreen('梓兰'))
