from os import getcwd, listdir
from sys import path
from time import sleep

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.win import toast

class BattleLoop:
    def __init__(self, adb, cwd, ico):
        self.cwd = cwd
        self.adb = adb
        self.ico = ico
        self.switch = False
        self.connectSwitch = False
        self.autoRecMed = False
        self.autoRecStone = False
        self.stoneMaxNum = 0


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
        restStone = self.stoneMaxNum
        #isFirstTurn = True
        self.switch = switchI

        if self.switch:
            OFCount = 0
            twiceTry = 0
            while self.switch:
                self.adb.screenShot()
                #判断代理指挥是否勾选
                '''if isFirstTurn:
                    isFirstTurn = False'''
                picStartA = pictureFind.matchImg(self.screenShot, self.startA, confidencevalue= 0.9)
                if picStartA != None and self.switch:
                    print('> auto mode check <')
                    picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                    if picAutoOn == None and self.switch:
                        picAutoOff = pictureFind.matchImg(self.screenShot, self.autoOff)
                        if picAutoOff != None and self.switch:
                            posAutoOff = picAutoOff['result']
                            self.adb.click(posAutoOff[0], posAutoOff[1])
                            continue

                    '''isDelayExit = False #加载延迟是否出现，即检查到开始行动A但实际上是正在进入关卡前的状态
                    for i in range(5):
                        if not self.switch:
                            break
                        isSSSuccess = self.adb.screenShot()
                        if not isSSSuccess:
                            print('unable to get screenshot')
                            self.switchB = False
                            return False
                        for eachObj in self.listBattleImg:
                            picInfo = pictureFind.matchImg(self.screenShot, eachObj, 0.8)
                            if picInfo != None:
                                if eachObj['obj'] != "startApart.png":
                                    isDelayExit  = True
                                    break

                        picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                        if picAutoOn != None or isDelayExit:
                            if isDelayExit:
                                print("start delay exit")
                            break'''

                #sleep(1)
                for eachObj in self.listImg:
                    if self.switch:
                        if eachObj['obj'] == "end.png":
                            confidence = 0.8
                        else:
                            confidence = 0.9
                        #print(self.screenShot + ' ' + self.cwd + '/res/battle/' + eachObj)
                        picInfo = pictureFind.matchImg(self.screenShot, eachObj, confidence)
                        #print(eachObj+ '：', picInfo)
                        if picInfo != None:
                            if picInfo['result'][1] < 270:
                                continue

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
                                        toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
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
                                        toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                else:
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    self.switch = False
                                    toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                            elif eachObj['obj'] == "stoneLack.png":
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
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

                            break
                if isInBattle:
                    sleep(1)
    def stop(self):
        self.connectSwitch = False
        self.switch = False