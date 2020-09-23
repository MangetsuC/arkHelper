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
        isFirstTurn = True
        self.switch = switchI

        if self.switch:
            OFCount = 0
            twiceTry = 0
            while self.switch:
                self.adb.screenShot()
                #判断代理指挥是否勾选
                if isFirstTurn:
                    isFirstTurn = False
                    picStartA = pictureFind.matchImg(self.screenShot, self.startA, confidencevalue= 0.9)
                    if picStartA != None:
                        print('> auto mode check <')
                        picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                        if picAutoOn == None:
                            picAutoOff = pictureFind.matchImg(self.screenShot, self.autoOff)
                            if picAutoOff != None:
                                posAutoOff = picAutoOff['result']
                                self.adb.click(posAutoOff[0], posAutoOff[1])

                        isSSSuccess = self.adb.screenShot()
                        if not isSSSuccess:
                            toast.broadcastMsg("ArkHelper", "获取屏幕信息失败，请重启模拟器", self.ico)
                            print('unable to get screenshot')
                            self.switch = False
                            break
                        picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                        if picAutoOn == None:
                            toast.broadcastMsg("ArkHelper", "无法勾选代理指挥", self.ico)
                            print('auto mode still off')
                            self.switch = False
                            break

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