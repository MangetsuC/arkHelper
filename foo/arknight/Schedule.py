from os import getcwd, listdir
from sys import path
from time import sleep
from json import loads
from PyQt5.QtCore import pyqtSignal, QObject

path.append(getcwd())
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
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.act = self.cwd + "/res/panel/other/act.png"
        self.battle = self.cwd + "/res/panel/other/battle.png"
        self.home = self.cwd + "/res/panel/other/home.png"
        self.visitNext = self.cwd + "/res/panel/other/visitNext.png"
        self.listBattleImg = pictureFind.picRead([self.cwd + "/res/battle/" + i for i in listdir(self.cwd + "/res/battle")])
        self.startA = pictureFind.picRead(self.cwd + "/res/battle/startApart.png")
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
            if self.adb.screenShot():
                picTh = pictureFind.matchImg(self.screenShot, self.sign)
                if picTh != None:
                    break
            else:
                print('Fail to get screenshot')
                return False
            if self.adb.screenShot():
                picAct = pictureFind.matchImg(self.screenShot, self.act)
                if picAct != None:
                    posAct = picAct['result']
                    self.adb.click(posAct[0], posAct[1])
                else:
                    picHome = pictureFind.matchImg(self.screenShot, self.home)
                    if picHome != None:
                        posHome = picHome['result']
                        self.adb.click(posHome[0], posHome[1])
                        if self.adb.screenShot():
                            picBattle = pictureFind.matchImg(self.screenShot, self.battle)
                            if picBattle != None:
                                posBattle = picBattle['result']
                                self.adb.click(posBattle[0], posBattle[1])
                            else:
                                continue
                        else:
                            print('Fail to get screenshot')
                            return False
                    else:
                        tempCount += 1
                        if tempCount > 5:
                            print('unable to init')
                            return False
                        else:
                            continue
                
            else:
                print('Fail to get screenshot')
                return False

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
                self.adb.screenShot()
                picEx = pictureFind.matchImg(self.screenShot, self.exSymbol)
                if picEx != None:
                    break
            else:
                return False
            for i in range(5):
                self.adb.click(720, 405) #存在不小心点开剿灭关卡无法切换关卡的可能性
                sleep(1)
                self.adb.screenShot()
                picExChap = pictureFind.matchImg(self.screenShot, self.exIV["exSwitch"])
                if picExChap != None:
                    self.adb.click(picExChap['result'][0], picExChap['result'][1])
                    sleep(0.5)
                    break
            else:
                return False
            for i in range(5):
                self.adb.screenShot()
                picLevelOn = pictureFind.matchImg(self.screenShot,self.startA)
                if picLevelOn != None:
                    return True
                picExObj = pictureFind.matchImg(self.screenShot, self.exIV[objLevel])
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
                self.adb.screenShot()
                levelOnScreen = pictureFind.levelOcr(self.screenShot)
                if levelOnScreen != None:
                    if objLevel in levelOnScreen:
                        self.adb.click(levelOnScreen[objLevel][0],levelOnScreen[objLevel][1])
                        picLevelOn = pictureFind.matchImg(self.screenShot,self.startA)
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
        self.adb.screenShot()
        if chap == 'external' or chap == 'tempE':
            picChap = pictureFind.matchImg(self.screenShot, self.III['ex'])
            if picChap != None:
                self.adb.click(325, 600)
                return True
        elif chap.isdigit():
            #主线
            nowChap = -1
            if int(chap) <= 3:
                self.adb.click(165, 160)
            elif int(chap) <= 8:
                self.adb.click(165, 595)
            for eachChap in range(1, 9):
                picChap = pictureFind.matchImg(self.screenShot, self.III[str(eachChap)])
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
                        self.adb.screenShot()
                        picChap = pictureFind.matchImg(self.screenShot, self.III[chap])
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
                        self.adb.screenShot()
                        picChap = pictureFind.matchImg(self.screenShot, self.III[chap])
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
                self.adb.screenShot()
                picChap = pictureFind.matchImg(self.screenShot, self.III[chap])
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
            
            self.adb.screenShot()
            #判断代理指挥是否勾选
            picStartA = pictureFind.matchImg(self.screenShot, self.startA, confidencevalue= 0.9)
            if picStartA != None and self.switch and self.switchB:
                picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                if picAutoOn == None and self.switch and self.switchB:
                    picAutoOff = pictureFind.matchImg(self.screenShot, self.autoOff)
                    if picAutoOff != None and self.switch and self.switchB:
                        posAutoOff = picAutoOff['result']
                        self.adb.click(posAutoOff[0], posAutoOff[1])
                        continue

            isInBattle = False
            #sleep(1)
            for eachObj in self.listBattleImg:
                if self.switch and self.switchB:
                    if eachObj['obj'] == "end.png" or eachObj['obj'] == "levelup.png":
                        confidence = 0.8
                    else:
                        confidence = 0.9
                    #print(self.screenShot + ' ' + self.cwd + '/res/battle/' + eachObj)
                    picInfo = pictureFind.matchImg(self.screenShot, eachObj, confidence)
                    #print(eachObj+ '：', picInfo)
                    if picInfo != None:
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
                                    for i in range(10):
                                        temp = pictureFind.imreadCH(self.screenShot)#改用picRead
                                        self.adb.screenShot()
                                        if pictureFind.matchImg(temp, self.screenShot, confidencevalue=0.99) != None:
                                            break
                                        sleep(1)
                                    bootyTotalCount += self.BootyDetect.bootyCheck(bootyName, self.screenShot)
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
                                medInfo = pictureFind.matchImg(self.screenShot, self.recMed)
                                stoneInfo = pictureFind.matchImg(self.screenShot, self.recStone)
                                confirmInfo = pictureFind.matchImg(self.screenShot, self.confirm)
                                if (not self.autoRecMed) and (self.autoRecStone):
                                    if medInfo != None and stoneInfo == None:
                                        self.adb.click(medInfo['result'][0]+350, medInfo['result'][1], isSleep= True)
                                        self.adb.screenShot()
                                        medInfo = pictureFind.matchImg(self.screenShot, self.recMed)
                                        stoneInfo = pictureFind.matchImg(self.screenShot, self.recStone)
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
                                    picLackInfo = pictureFind.matchImg(self.screenShot, lackTem, 0.9)
                                    if picLackInfo:
                                        self.adb.click(picLackInfo['result'][0], picLackInfo['result'][1], isSleep = True)
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                    else:
                                        self.adb.click(picPos[0], picPos[1], isSleep = True)
                                        if eachObj['obj'] == 'startApartOF.png':
                                            self.adb.screenShot()
                                            OFend = pictureFind.matchImg(self.screenShot, self.cwd + '/res/act/OFend.png', 0.8)
                                            if OFend != None:
                                                self.switch = False
                                                toast.broadcastMsg("ArkHelper", "黑曜石节门票不足", self.ico)
                                else:
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    if eachObj['obj'] == 'startApartOF.png':
                                        self.adb.screenShot()
                                        OFend = pictureFind.matchImg(self.screenShot, self.cwd + '/res/act/OFend.png', 0.8)
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
        self.levelSchedule = self.readJson()
        levelList = self.levelSchedule['main'][0]['sel']
        for eachLevel in levelList:
            if not self.switch:
                break
            if eachLevel['part'] == 'THIS':
                self.switchB = True
            else:
                self.switchB = self.goLevel(eachLevel)
            if self.switchB and self.switch:
                levelCondition = self.runTimes(times=eachLevel['times'])
                if not levelCondition:
                    self.stop()
                    break

    def stop(self):
        self.switch = False
        self.switchB = False