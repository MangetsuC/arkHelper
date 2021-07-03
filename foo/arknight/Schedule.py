from os import getcwd, listdir
from sys import path
from time import sleep
from json import loads
from PyQt5.QtCore import pyqtSignal, QObject

from foo.pictureR import pictureFind
from foo.pictureR import bootyCount
from foo.win import toast

class BattleSchedule(QObject):
    errorSignal = pyqtSignal(str)
    def __init__(self, adb, cwd, dataPath, ico):
        super(BattleSchedule, self).__init__()
        self.cwd = cwd
        self.adb = adb
        self.ico = ico
        self.json = dataPath + '/schedule.json'
        self.levelSchedule = self.readJson()
        self.switch = False
        self.switchB = False
        self.autoRecMed = False
        self.autoRecStone = False

        self.isWaitingUser = False
        self.isRecovered = False

        self.stoneMaxNum = 0
        self.BootyDetect = bootyCount.Booty(self.cwd)
        self.imgInit()

    def recChange(self, num, inputData):
        if num == 0:
            self.autoRecMed = inputData
        elif num == 1:
            self.autoRecStone = inputData
        elif num == 2:
            self.stoneMaxNum = inputData

    def imgInit(self):
        self.recMed = pictureFind.picRead(self.cwd + "/res/panel/recovery/medicament.png")
        self.recStone = pictureFind.picRead(self.cwd + "/res/panel/recovery/stone.png")
        self.confirm = pictureFind.picRead(self.cwd + "/res/panel/recovery/confirm.png")
        self.sign = pictureFind.picRead(self.cwd + "/res/panel/level/sign.png")

        #self.exPos = {'ex1':(220,280),'ex2':(845,580),'ex3':(1230,340)}
        #self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.act = self.cwd + "/res/panel/other/act.png"
        self.battle = self.cwd + "/res/panel/other/battle.png"
        self.home = self.cwd + "/res/panel/other/home.png"
        self.visitNext = self.cwd + "/res/panel/other/visitNext.png"
        self.listBattleImg = pictureFind.picRead([self.cwd + "/res/battle/" + i for i in listdir(self.cwd + "/res/battle")])
        self.startA = pictureFind.picRead(self.cwd + "/res/battle/startApart.png")
        self.startB = pictureFind.picRead(self.cwd + "/res/battle/startBpart.png")
        self.autoOff = pictureFind.picRead(self.cwd + "/res/panel/other/autoOff.png")
        self.autoOn = pictureFind.picRead(self.cwd + "/res/panel/other/autoOn.png")
        self.II = {'MAIN':self.cwd + "/res/panel/level/I/main.png", 'EX':self.cwd + "/res/panel/level/I/exterminate.png",\
            'RS':self.cwd + "/res/panel/level/I/resource.png", 'PR':self.cwd + "/res/panel/level/I/chip.png"}
        self.III = {'A':self.cwd + "/res/panel/level/II/A.png", 'B':self.cwd + "/res/panel/level/II/B.png",\
                'C':self.cwd + "/res/panel/level/II/C.png", 'D':self.cwd + "/res/panel/level/II/D.png",\
                'AP':self.cwd + "/res/panel/level/II/AP.png", 'CA':self.cwd + "/res/panel/level/II/CA.png",\
                'CE':self.cwd + "/res/panel/level/II/CE.png", 'SK':self.cwd + "/res/panel/level/II/SK.png",\
                'LS':self.cwd + "/res/panel/level/II/LS.png", \
                '0':self.cwd + "/res/panel/level/II/ep0.png", '1':self.cwd + "/res/panel/level/II/ep1.png",\
                '2':self.cwd + "/res/panel/level/II/ep2.png", '3':self.cwd + "/res/panel/level/II/ep3.png",\
                '4':self.cwd + "/res/panel/level/II/ep4.png", '5':self.cwd + "/res/panel/level/II/ep5.png",\
                '6':self.cwd + "/res/panel/level/II/ep6.png", '7':self.cwd + "/res/panel/level/II/ep7.png",\
                '8':self.cwd + "/res/panel/level/II/ep8.png",\
                'ex': self.cwd + "/res/panel/level/II/EX.png"}
        self.exIV = {'ex1':self.cwd + "/res/panel/level/III/e01.png",'ex2':self.cwd + "/res/panel/level/III/e02.png", 'ex3':self.cwd + "/res/panel/level/III/e03.png",\
                    'ex4':self.cwd + "/res/panel/level/III/e04.png", 'exSwitch':self.cwd + "/res/panel/level/III/exSwitch.png"}
        self.exSymbol = self.cwd + "/res/panel/other/exSymbol.png"

    def goLevel(self, level):
        tempCount = 0
        part = level['part']
        chap = level['chap']
        objLevel = level['objLevel']

        #前往一级菜单
        while self.switch:
            picTh = pictureFind.matchImg(self.adb.getScreen_std(), self.sign)
            if picTh != None:
                break

            picAct = pictureFind.matchImg(self.adb.getScreen_std(), self.act)
            if picAct != None:
                posAct = picAct['result']
                self.adb.click(posAct[0], posAct[1])
            else:
                picHome = pictureFind.matchImg(self.adb.getScreen_std(), self.home)
                if picHome != None:
                    posHome = picHome['result']
                    self.adb.click(posHome[0], posHome[1])

                    picBattle = pictureFind.matchImg(self.adb.getScreen_std(), self.battle)
                    if picBattle != None:
                        posBattle = picBattle['result']
                        self.adb.click(posBattle[0], posBattle[1])
                    else:
                        continue
                else:
                    tempCount += 1
                    if tempCount > 5:
                        print('unable to init')
                        return False
                    else:
                        continue


        #二级菜单的选择
        if part == 'MAIN':
            self.adb.click(305,750)
        elif part == 'EX':
            self.adb.click(1125,750)
        elif part == 'RS' or part == 'PR':
            self.adb.click(920,750)
        else:
            return False

        sleep(1)
        #三级菜单的选择
        #主线MIAN，物资RS，芯片PR
        if not self.chooseChap(chap):
            return False

        #关卡选择
        if part == 'EX':
            for i in range(5):
                picEx = pictureFind.matchImg(self.adb.getScreen_std(), self.exSymbol)
                if picEx != None:
                    break
            else:
                return False
            for i in range(5):
                self.adb.click(720, 405) #存在不小心点开剿灭关卡无法切换关卡的可能性
                sleep(1)
                picExChap = pictureFind.matchImg(self.adb.getScreen_std(), self.exIV["exSwitch"])
                if picExChap != None:
                    self.adb.click(picExChap['result'][0], picExChap['result'][1])
                    sleep(0.5)
                    break
            else:
                return False
            for i in range(5):
                screenshot = self.adb.getScreen_std()
                picLevelOn = pictureFind.matchImg(screenshot,self.startA)
                if picLevelOn != None:
                    return True
                picExObj = pictureFind.matchImg(screenshot, self.exIV[objLevel])
                if picExObj != None:
                    if objLevel == 'ex4':
                        self.adb.click(picExObj['result'][0], picExObj['result'][1] + 80)
                    else:
                        self.adb.click(picExObj['result'][0], picExObj['result'][1])
                    return True
            else:
                return False
        else:
            self.adb.speedToLeft()
            for i in range(25):
                if not self.switch:
                    break
                levelOnScreen = pictureFind.levelOcr(self.adb.getScreen_std())
                if levelOnScreen != None:
                    if objLevel in levelOnScreen:
                        self.adb.click(levelOnScreen[objLevel][0],levelOnScreen[objLevel][1])
                        picLevelOn = pictureFind.matchImg(self.adb.getScreen_std(),self.startA)
                        if picLevelOn != None:
                            return True
                    else:
                        self.adb.onePageRight()
                else:
                    print(f'skip {objLevel}')
                    return False
            else:
                return False


    def chooseChap(self,chap):
        if chap == 'external' or chap == 'tempE':
            picChap = pictureFind.matchImg(self.adb.getScreen_std(), self.III['ex'])
            if picChap != None:
                self.adb.click(picChap['result'][0], picChap['result'][1])
                return True
        elif chap.isdigit():
            #主线
            nowChap = -1
            if int(chap) <= 3:
                self.adb.click(165, 160)
            elif int(chap) <= 8:
                self.adb.click(165, 595)
            for eachChap in range(0, 9): #0-8章
                picChap = pictureFind.matchImg(self.adb.getScreen_std(), self.III[str(eachChap)])
                if picChap != None:
                    nowChap = eachChap
                    break
            if nowChap < 0:
                self.adb.mainToLeft()
            else:
                if int(chap) == nowChap:
                    self.adb.click(1050, 400)
                    return True
                elif int(chap) > nowChap:
                    for i in range(10):
                        if not self.switch:
                            break
                        picChap = pictureFind.matchImg(self.adb.getScreen_std(), self.III[chap])
                        if not self.switch:
                            break
                        elif picChap == None:
                            self.adb.mainToNextChap()
                        else:
                            self.adb.click(1050, 400)
                            return True
                elif int(chap) < nowChap:
                    for i in range(10):
                        if not self.switch:
                            break
                        picChap = pictureFind.matchImg(self.adb.getScreen_std(), self.III[chap])
                        if not self.switch:
                            break
                        elif picChap == None:
                            self.adb.mainToPreChap()
                        else:
                            self.adb.click(1050, 400)
                            return True
        else:
            #各类资源
            self.adb.swipe(1050, 400, 1440, 400, 200) #左滑，避免关卡全开的情况
            for i in range(20):
                if not self.switch:
                    break
                picChap = pictureFind.matchImg(self.adb.getScreen_std(), self.III[chap])
                if not self.switch:
                    break
                elif picChap == None:
                    self.adb.onePageRight()
                else:
                    self.adb.click(picChap['result'][0],picChap['result'][1])
                    return True
        return False

    def runTimes(self, times = 1):
        bootyName = None
        if isinstance(times, dict):
            bootyMode = True
            bootyName = times['bootyName']
            times = int(times['bootyNum'])
        else:
            bootyMode = False
            times = int(times)

        #isFirstTurn = True
        countStep = 0
        totalCount = 0
        bootyTotalCount = 0
        errorCount = 0
        while self.switch and self.switchB:
            
            screenshot = self.adb.getScreen_std()
            #判断代理指挥是否勾选
            picStartA = pictureFind.matchImg(screenshot, self.startA, confidencevalue= 0.9)
            if picStartA != None and self.switch and self.switchB:
                picAutoOn = pictureFind.matchImg(screenshot, self.autoOn)
                if picAutoOn == None and self.switch and self.switchB:
                    picAutoOff = pictureFind.matchImg(screenshot, self.autoOff)
                    if picAutoOff != None and self.switch and self.switchB:
                        posAutoOff = picAutoOff['result']
                        self.adb.click(posAutoOff[0], posAutoOff[1])
                        continue

            isInBattle = False
            #sleep(1)
            for eachObj in self.listBattleImg:
                if self.switch and self.switchB:
                    confidence = self.adb.getTagConfidence()
                    picInfo = pictureFind.matchImg(screenshot, eachObj, confidence)
                    #print(eachObj+ '：', picInfo)
                    if picInfo != None:
                        if 'startApart' in eachObj['obj']:
                            BInfo = pictureFind.matchImg(screenshot, self.startB, confidence)
                                #避免是因为匹配到了队伍配置界面低栏上的行动二字
                            if BInfo != None:
                                picInfo = BInfo
                        if picInfo['result'][1] < 270:
                            continue

                        if eachObj['obj'] == "error.png" or eachObj['obj'] == "giveup.png":
                            errorCount += 1
                            if errorCount > 2:
                                self.errorSignal.emit('schedule')
                                sleep(1)
                                while self.isWaitingUser:
                                    sleep(5)
                                if not self.isRecovered:
                                    self.switch = False
                                    self.switchB = False
                                self.isRecovered = False
                            break
                        else:
                            errorCount = 0

                        if eachObj['obj'] == "startBpart.png":
                            isInBattle = True
                        else:
                            isInBattle = False
                        

                        picPos = picInfo['result']
                        if countStep == 0:
                            if eachObj['obj'] == 'startBpart.png':
                                countStep += 1
                        elif countStep == 1:
                            if eachObj['obj'] == 'endNormal.png':
                                countStep += 1
                                if bootyMode:
                                    lastPic = None
                                    for i in range(10):
                                        nowPic = nowPic = self.adb.getScreen_std()
                                        if lastPic is not None:
                                            if pictureFind.matchImg(lastPic, nowPic, confidencevalue=0.99) != None:
                                                break
                                        lastPic = nowPic
                                        sleep(1)
                                    bootyTotalCount += self.BootyDetect.bootyCheck(bootyName, nowPic)
                                    print(f'{bootyName} 应获得：{times} 实获得：{bootyTotalCount}')
                                    
                        elif countStep == 2:
                            if eachObj['obj'] == 'startApart.png':
                                countStep += 1
                        if countStep == 3:
                            countStep =0
                            totalCount += 1
                        if (totalCount == times) and (not bootyMode):
                            self.switchB = False
                            return True
                        if (bootyTotalCount >= times) and bootyMode:
                            self.adb.click(picPos[0], picPos[1], isSleep = True)
                            self.switchB = False
                            return True
                        if eachObj['obj'] == "cancel.png":
                            if self.autoRecMed or self.autoRecStone:
                                screenshot = self.adb.getScreen_std()
                                medInfo = pictureFind.matchImg(screenshot, self.recMed)
                                stoneInfo = pictureFind.matchImg(screenshot, self.recStone)
                                confirmInfo = pictureFind.matchImg(screenshot, self.confirm)
                                if (not self.autoRecMed) and (self.autoRecStone):
                                    if medInfo != None and stoneInfo == None:
                                        self.adb.click(medInfo['result'][0]+350, medInfo['result'][1], isSleep= True)
                                        screenshot = self.adb.getScreen_std()
                                        medInfo = pictureFind.matchImg(screenshot, self.recMed)
                                        stoneInfo = pictureFind.matchImg(screenshot, self.recStone)
                                        if medInfo == None and stoneInfo != None:
                                            if self.restStone >0:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                self.restStone -= 1
                                                break
                                    elif medInfo == None and stoneInfo != None:
                                        if self.restStone >0:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                self.restStone -= 1
                                                break
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    self.switch = False
                                    self.switchB = False
                                    toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                    return False
                                else:
                                    if self.autoRecMed:
                                        if medInfo != None:
                                            self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                            break
                                    if self.autoRecStone:
                                        if stoneInfo != None:
                                            if self.restStone >0:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                self.restStone -= 1
                                                break
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    self.switch = False
                                    self.switchB = False
                                    toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                    return False
                            else:
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
                                self.switch = False
                                self.switchB = False
                                toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                return False
                        elif eachObj['obj'] == "stoneLack.png":
                            self.adb.click(picPos[0], picPos[1], isSleep = True)
                            self.switch = False
                            self.switchB = False
                            toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                            return False
                        elif eachObj['obj'] == 'levelup.png':
                                lackTem = False
                                for eachTem in self.listBattleImg:
                                    if eachTem['obj'] == 'stoneLack.png':
                                        lackTem = eachTem
                                        break
                                if lackTem:
                                    picLackInfo = pictureFind.matchImg(screenshot, lackTem, 0.9)
                                    if picLackInfo:
                                        self.adb.click(picLackInfo['result'][0], picLackInfo['result'][1], isSleep = True)
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                    else:
                                        self.adb.click(picPos[0], picPos[1], isSleep = True)
                                        if eachObj['obj'] == 'startApartOF.png':
                                            OFend = pictureFind.matchImg(self.adb.getScreen_std(), self.cwd + '/res/act/OFend.png', 0.8)
                                            if OFend != None:
                                                self.switch = False
                                                toast.broadcastMsg("ArkHelper", "黑曜石节门票不足", self.ico)
                                else:
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    if eachObj['obj'] == 'startApartOF.png':
                                        OFend = pictureFind.matchImg(self.adb.getScreen_std(), self.cwd + '/res/act/OFend.png', 0.8)
                                        if OFend != None:
                                            self.switch = False
                                            toast.broadcastMsg("ArkHelper", "黑曜石节门票不足", self.ico)
                        else:
                            self.adb.click(picPos[0], picPos[1], isSleep = True)
                        break
                else:
                    break
            if isInBattle:
                sleep(1)
                
    def readJson(self):
        with open(self.json,'r', encoding='UTF-8') as s:
            data = s.read()
        data = loads(data)
        return data

    def run(self, switchI):
        self.switch = switchI
        self.restStone = self.stoneMaxNum
        print('正在获取用户配置的计划')
        self.levelSchedule = self.readJson()
        print('用户配置读取成功')
        levelList = self.levelSchedule['main'][0]['sel']
        for eachLevel in levelList:
            if not self.switch:
                break
            if eachLevel['part'] == 'THIS':
                self.switchB = True
            else:
                targetLevel = eachLevel['objLevel']
                if targetLevel[0] == 'S':
                    targetLevel = 'L' + targetLevel
                print(f'正在前往指定关卡{targetLevel}')
                self.switchB = self.goLevel(eachLevel)
            if self.switchB and self.switch:
                levelCondition = self.runTimes(times=eachLevel['times'])
                if not levelCondition:
                    self.stop()
                    break

    def stop(self):
        self.switch = False
        self.switchB = False