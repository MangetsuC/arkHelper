from os import getcwd, listdir
from sys import path
from time import sleep, time
from PyQt5.QtCore import pyqtSignal, QObject

from foo.pictureR import pictureFind
from foo.win import toast

class BattleLoop(QObject):
    noBootySignal = pyqtSignal()
    errorSignal = pyqtSignal(str)
    def __init__(self, adb, cwd, ico):
        super(BattleLoop, self).__init__()
        self.cwd = cwd
        self.adb = adb
        self.ico = ico
        self.switch = False
        self.connectSwitch = False
        self.autoRecMed = False
        self.autoRecStone = False
        self.stoneMaxNum = 0

        self.isWaitingUser = False
        self.isUselessContinue = False
        self.isRecovered = False

        self.battleLoopTimes = -1

        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.listBattleImg = pictureFind.picRead([self.cwd + "/res/battle/" + i for i in listdir(self.cwd + "/res/battle")])
        self.listActImg = pictureFind.picRead([self.cwd + "/res/actBattle/" + i for i in listdir(self.cwd + "/res/actBattle")])
        
        self.listImg = self.listActImg + self.listBattleImg

        self.startA = pictureFind.picRead(self.cwd + "/res/battle/startApart.png")
        self.startB = pictureFind.picRead(self.cwd + "/res/battle/startBpart.png")
        self.autoOff = pictureFind.picRead(self.cwd + "/res/panel/other/autoOff.png")
        self.autoOn = pictureFind.picRead(self.cwd + "/res/panel/other/autoOn.png")

        self.recMed = pictureFind.picRead(self.cwd + "/res/panel/recovery/medicament.png")
        self.recStone = pictureFind.picRead(self.cwd + "/res/panel/recovery/stone.png")
        self.confirm = pictureFind.picRead(self.cwd + "/res/panel/recovery/confirm.png")

        self.uselessLevel = pictureFind.picRead(self.cwd + "/res/panel/other/uselessLevel.png")
    
    def setLoopTimes(self, times):
        self.battleLoopTimes = times

    def getLoopTimes(self):
        return self.battleLoopTimes

    def recChange(self, num, inputData):
        if num == 0:
            self.autoRecMed = inputData
        elif num == 1:
            self.autoRecStone = inputData
        elif num == 2:
            self.stoneMaxNum = inputData
    
    def connect(self, broadcast = True):
        self.connectSwitch = True
        for times in range(10):
            print(f'正在连接adb...第{times+1}次')
            if self.connectSwitch:
                if self.adb.connect():
                    return True
                else:
                    print(f'第{times+1}次连接尝试失败')
            else:
                print('收到用户指令，中断')
                return False
        
        else:
            if broadcast:
                toast.broadcastMsg("ArkHelper", "连接模拟器失败，请检查设置和模拟器", self.ico)
                print('连接adb失败')
            else:
                print("INIT:adb connect failed")
            return False


    def run(self, switchI):
        isInBattle = False
        lastFoundPic = 'start'
        loopTime = 0
        restStone = self.stoneMaxNum
        #isFirstTurn = True
        self.switch = switchI
        self.isUselessContinue = False

        confidence = self.adb.getTagConfidence()

        sleepTime = None
        isFirstWait = False

        if self.switch:
            errorCount = 0
            while self.switch:
                screenshot = self.adb.getScreen_std()
                picStartA = pictureFind.matchImg(screenshot, self.startA, confidencevalue= 0.8)
                if picStartA != None and self.switch:
                    picIsUseless = pictureFind.matchImg(screenshot, self.uselessLevel)
                    if picIsUseless and (not self.isUselessContinue):
                        self.isWaitingUser = True
                        self.noBootySignal.emit()
                        while self.isWaitingUser:
                            sleep(1)
                        continue

                picAutoOn = pictureFind.matchImg(screenshot, self.autoOn)
                if picAutoOn == None and self.switch:
                    picAutoOff = pictureFind.matchImg(screenshot, self.autoOff)
                    if picAutoOff != None and self.switch:
                        posAutoOff = picAutoOff['result']
                        self.adb.click(posAutoOff[0], posAutoOff[1])
                        continue

                for eachObj in self.listImg:
                    if self.switch:
                        picInfo = pictureFind.matchImg(screenshot, eachObj, confidence)
                        if picInfo != None:
                            if picInfo['result'][1] < 270 and ('FIN_TS' not in picInfo['obj']):
                                #FIN_TS为活动连锁竞赛，结束标志在上半屏幕
                                continue
                            
                            if 'startApart' in picInfo['obj']:
                                BInfo = pictureFind.matchImg(screenshot, self.startB, confidence)
                                #避免是因为匹配到了队伍配置界面低栏上的行动二字
                                if BInfo != None:
                                    picInfo = BInfo
                                else:
                                    if loopTime == self.battleLoopTimes:
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"达到设定次数，共循环{loopTime}次", self.ico)
                                        break

                            if picInfo['obj'] != lastFoundPic:
                                errorCount = 0
                                lastFoundPic = picInfo['obj']
                                if 'endNormal' in picInfo['obj']:
                                    loopTime += 1

                            if 'error' in picInfo['obj']:
                                errorCount += 1
                                if errorCount > 2:
                                    self.errorSignal.emit('loop')
                                    sleep(1)
                                    while self.isWaitingUser:
                                        sleep(5)
                                    if not self.isRecovered:
                                        self.switch = False
                                        self.isRecovered = False
                                break

                            if 'startBpart' in picInfo['obj']:
                                isInBattle = True
                                isFirstWait = True
                                startTime = time()
                            else:
                                if sleepTime == None and isInBattle:
                                    sleepTime = int(time() - startTime)
                                isInBattle = False

                            picPos = picInfo['result']
                            if picInfo['obj'] == "cancel.png":
                                if self.autoRecMed or self.autoRecStone:
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
                                                if restStone >0:
                                                    self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                    restStone -= 1
                                                    break
                                        elif medInfo == None and stoneInfo != None:
                                            if restStone >0:
                                                    self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                    restStone -= 1
                                                    break
                                        self.adb.click(picPos[0], picPos[1], isSleep = True)
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                                    else:
                                        if self.autoRecMed:
                                            if medInfo != None:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                break
                                        if self.autoRecStone:
                                            if stoneInfo != None:
                                                if restStone >0:
                                                    self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                    restStone -= 1
                                                    break
                                        self.adb.click(picPos[0], picPos[1], isSleep = True)
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                                else:
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    self.switch = False
                                    toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                            elif picInfo['obj'] == 'stoneLack.png':
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
                                self.switch = False
                                toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                            elif picInfo['obj'] == 'levelup.png':
                                lackTem = False
                                for eachTem in self.listImg:
                                    if eachTem['obj'] == 'stoneLack.png':
                                        lackTem = eachTem
                                        break
                                if lackTem:
                                    picLackInfo = pictureFind.matchImg(screenshot, lackTem, 0.9)
                                    if picLackInfo:
                                        self.adb.click(picLackInfo['result'][0], picLackInfo['result'][1], isSleep = True)
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                                    else:
                                        self.adb.click(picPos[0], picPos[1], isSleep = True)
                                        if picInfo['obj'] == 'startApartOF.png':
                                            OFend = pictureFind.matchImg(self.adb.getScreen_std(), self.cwd + '/res/act/OFend.png', 0.8)
                                            if OFend != None:
                                                self.switch = False
                                                toast.broadcastMsg("ArkHelper", f"黑曜石节门票不足，共循环{loopTime}次", self.ico)
                                else:
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    if picInfo['obj'] == 'startApartOF.png':
                                        OFend = pictureFind.matchImg(self.adb.getScreen_std(), self.cwd + '/res/act/OFend.png', 0.8)
                                        if OFend != None:
                                            self.switch = False
                                            toast.broadcastMsg("ArkHelper", f"黑曜石节门票不足，共循环{loopTime}次", self.ico)
                            else:
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
                                if picInfo['obj'] == 'startApartOF.png':
                                    OFend = pictureFind.matchImg(self.adb.getScreen_std(), self.cwd + '/res/act/OFend.png', 0.8)
                                    if OFend != None:
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"黑曜石节门票不足，共循环{loopTime}次", self.ico)

                            break
                if isInBattle:
                    if sleepTime == None:
                        sleep(1)
                    else:
                        if not isFirstWait:
                            sleep(1)
                        else:
                            for i in range(sleepTime):
                                sleep(1)
                                if not self.switch:
                                    return
                            else:
                                isFirstWait = False
    def stop(self):
        self.connectSwitch = False
        self.switch = False