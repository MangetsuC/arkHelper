from os import getcwd, listdir
from sys import path
from time import sleep
from threading import Thread

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.win import toast

class BattleLoop:
    def __init__(self, adb, cwd, app):
        self.cwd = cwd
        self.adb = adb
        self.app = app
        self.listBattleImg = listdir(cwd + "/res/battle")
        self.switch = False
        self.connectSwitch = False
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.autoOff = self.cwd + "/res/panel/other/autoOff.png"
        self.autoOn = self.cwd + "/res/panel/other/autoOn.png"
    
    def run(self):
        isFirstTurn = True
        self.connectSwitch = True
        for times in range(20):
            if self.connectSwitch:
                self.switch = self.adb.connect()
                if self.switch:
                    break
                times += 1
            else:
                break
        
        print(self.switch)
        if (not self.switch) and self.connectSwitch:
            self.app.setButton(1)
            self.app.setState("连接失败，请检查配置文件或重启模拟器")
            toast.broadcastMsg("ArkHelper", "连接失败，请检查配置文件或重启模拟器", self.app.icon)
        else:
            while self.switch:
                self.app.setState("正在获取并分析屏幕信息")
                
                isSSSuccess = self.adb.screenShot()
                if not isSSSuccess:
                    self.app.setState("获取屏幕信息失败，请重启模拟器")
                    toast.broadcastMsg("ArkHelper", "获取屏幕信息失败，请重启模拟器", self.app.icon)
                    self.app.setButton(1)
                    self.switch = False
                    break
                #判断代理指挥是否勾选
                if isFirstTurn:
                    isFirstTurn = False
                    picStartA = pictureFind.matchImg(self.screenShot, self.cwd + "/res/battle/startApart.png", confidencevalue= 0.9)
                    if picStartA != None:
                        print('here')
                        picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                        if picAutoOn == None:
                            picAutoOff = pictureFind.matchImg(self.screenShot, self.autoOff)
                            if picAutoOff != None:
                                posAutoOff = picAutoOff['result']
                                self.adb.click(posAutoOff[0], posAutoOff[1])

                        isSSSuccess = self.adb.screenShot()
                        if not isSSSuccess:
                            self.app.setState("获取屏幕信息失败，请重启模拟器")
                            toast.broadcastMsg("ArkHelper", "获取屏幕信息失败，请重启模拟器", self.app.icon)
                            self.app.setButton(1)
                            self.switch = False
                            break
                        picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                        if picAutoOn == None:
                            self.app.setState("无法勾选代理指挥")
                            toast.broadcastMsg("ArkHelper", "无法勾选代理指挥", self.app.icon)
                            self.app.setButton(1)
                            self.switch = False
                            break

                sleep(1)
                for eachObj in self.listBattleImg:
                    if self.switch:
                        if eachObj == "end.png":
                            confidence = 0.8
                        else:
                            confidence = 0.9
                        print(self.screenShot, self.cwd + '/res/battle/' + eachObj)
                        picInfo = pictureFind.matchImg(self.screenShot, self.cwd + '/res/battle/' + eachObj, confidence)
                        print(eachObj+ '：', picInfo)
                        if picInfo != None:
                            picPos = picInfo['result']
                            self.adb.click(picPos[0], picPos[1], isSleep = False)
                            if eachObj == "cancel.png":
                                self.switch = False
                                self.app.setState("理智耗尽")
                                toast.broadcastMsg("ArkHelper", "理智耗尽", self.app.icon)
                                self.app.setButton(1)
                                break
                sleep(1)
    def stop(self):
        self.connectSwitch = False
        self.switch = False