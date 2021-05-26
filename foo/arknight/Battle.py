from os import getcwd, listdir
from sys import path
from time import sleep
from PyQt5.QtCore import pyqtSignal, QObject

path.append(getcwd())
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
            if self.connectSwitch:
                if self.adb.connect():
                    return True
            else:
                return False
        
        else:
            if broadcast:
                toast.broadcastMsg("ArkHelper", "连接模拟器失败，请检查设置和模拟器", self.ico)
                print('unable to connect simulator')
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

        if self.switch:
            errorCount = 0
            while self.switch:
                self.adb.screenShot()
                #判断代理指挥是否勾选
                '''if isFirstTurn:
                    isFirstTurn = False'''
                picStartA = pictureFind.matchImg(self.screenShot, self.startA, confidencevalue= 0.9)
                if picStartA != None and self.switch:
                    picIsUseless = pictureFind.matchImg(self.screenShot, self.uselessLevel)
                    if picIsUseless and (not self.isUselessContinue):
                        self.isWaitingUser = True
                        self.noBootySignal.emit()
                        while self.isWaitingUser:
                            sleep(1)
                        continue
                    else:
                        picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                        if picAutoOn == None and self.switch:
                            picAutoOff = pictureFind.matchImg(self.screenShot, self.autoOff)
                            if picAutoOff != None and self.switch:
                                posAutoOff = picAutoOff['result']
                                self.adb.click(posAutoOff[0], posAutoOff[1])
                                continue

                for eachObj in self.listImg:
                    if self.switch:
                        if eachObj['obj'] == "end.png" or eachObj['obj'] == "levelup.png":
                            confidence = 0.8
                        elif eachObj['obj'] == 'endExterminate.png':
                            confidence = self.adb.getTagConfidence()
                        else:
                            confidence = 0.9
                        picInfo = pictureFind.matchImg(self.screenShot, eachObj, confidence)
                        if picInfo != None:
                            if picInfo['result'][1] < 270:
                                continue
                            
                            if eachObj['obj'] == 'startApart.png' or eachObj['obj'] == 'startApartOF.png':
                                if loopTime == self.battleLoopTimes:
                                    self.switch = False
                                    toast.broadcastMsg("ArkHelper", f"达到设定次数，共循环{loopTime}次", self.ico)
                                    break

                            if eachObj['obj'] != lastFoundPic:
                                errorCount = 0
                                lastFoundPic = eachObj['obj']
                                if eachObj['obj'] == "endNormal.png":
                                    loopTime += 1

                            if eachObj['obj'] == "error.png" or eachObj['obj'] == "giveup.png":
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

                            if eachObj['obj'] == "startBpart.png":
                                isInBattle = True
                            else:
                                isInBattle = False

                            picPos = picInfo['result']
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
                            elif eachObj['obj'] == 'stoneLack.png':
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
                                self.switch = False
                                toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                            elif eachObj['obj'] == 'levelup.png':
                                lackTem = False
                                for eachTem in self.listImg:
                                    if eachTem['obj'] == 'stoneLack.png':
                                        lackTem = eachTem
                                        break
                                if lackTem:
                                    picLackInfo = pictureFind.matchImg(self.screenShot, lackTem, 0.9)
                                    if picLackInfo:
                                        self.adb.click(picLackInfo['result'][0], picLackInfo['result'][1], isSleep = True)
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"理智耗尽，共循环{loopTime}次", self.ico)
                                    else:
                                        self.adb.click(picPos[0], picPos[1], isSleep = True)
                                        if eachObj['obj'] == 'startApartOF.png':
                                            self.adb.screenShot()
                                            OFend = pictureFind.matchImg(self.screenShot, self.cwd + '/res/act/OFend.png', 0.8)
                                            if OFend != None:
                                                self.switch = False
                                                toast.broadcastMsg("ArkHelper", f"黑曜石节门票不足，共循环{loopTime}次", self.ico)
                                else:
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    if eachObj['obj'] == 'startApartOF.png':
                                        self.adb.screenShot()
                                        OFend = pictureFind.matchImg(self.screenShot, self.cwd + '/res/act/OFend.png', 0.8)
                                        if OFend != None:
                                            self.switch = False
                                            toast.broadcastMsg("ArkHelper", f"黑曜石节门票不足，共循环{loopTime}次", self.ico)
                            else:
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
                                if eachObj['obj'] == 'startApartOF.png':
                                    self.adb.screenShot()
                                    OFend = pictureFind.matchImg(self.screenShot, self.cwd + '/res/act/OFend.png', 0.8)
                                    if OFend != None:
                                        self.switch = False
                                        toast.broadcastMsg("ArkHelper", f"黑曜石节门票不足，共循环{loopTime}次", self.ico)

                            break
                if isInBattle:
                    sleep(1)
    def stop(self):
        self.connectSwitch = False
        self.switch = False