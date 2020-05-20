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
        self.listBattleImg = listdir(cwd + "/res/battle")
        self.switch = False
        self.connectSwitch = False
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.autoOff = self.cwd + "/res/panel/other/autoOff.png"
        self.autoOn = self.cwd + "/res/panel/other/autoOn.png"
    
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
        isFirstTurn = True
        self.switch = switchI

        if self.switch:
            twiceTry = 0
            while self.switch:
                isSSSuccess = self.adb.screenShot(pngName = 'check')
                if not isSSSuccess:
                    toast.broadcastMsg("ArkHelper", "获取屏幕信息失败，请重启模拟器", self.ico)
                    print('unable to get screenshot')
                    self.switch = False
                    break

                picInfoCompare = pictureFind.matchImg(self.screenShot, self.cwd + "/bin/adb/check.png", confidencevalue= 0.9)
                if picInfoCompare != None:
                    twiceTry += 1
                else:
                    twiceTry = 0
                if twiceTry > 1:
                    twiceTry -= 1
                    continue
                
                self.adb.screenShot()
                #判断代理指挥是否勾选
                if isFirstTurn:
                    isFirstTurn = False
                    picStartA = pictureFind.matchImg(self.screenShot, self.cwd + "/res/battle/startApart.png", confidencevalue= 0.9)
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
                for eachObj in self.listBattleImg:
                    if self.switch:
                        if eachObj == "end.png":
                            confidence = 0.8
                        else:
                            confidence = 0.9
                        #print(self.screenShot + ' ' + self.cwd + '/res/battle/' + eachObj)
                        picInfo = pictureFind.matchImg(self.screenShot, self.cwd + '/res/battle/' + eachObj, confidence)
                        #print(eachObj+ '：', picInfo)
                        if picInfo != None:
                            picPos = picInfo['result']
                            self.adb.click(picPos[0], picPos[1], isSleep = False)
                            if eachObj == "cancel.png":
                                self.switch = False
                                toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                            break
                #sleep(1)
    def stop(self):
        self.connectSwitch = False
        self.switch = False