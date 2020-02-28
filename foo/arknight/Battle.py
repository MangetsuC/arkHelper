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
    
    def run(self):
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
                
                sleep(1)
                for eachObj in self.listBattleImg:
                    if self.switch:
                        if eachObj == "end.png":
                            confidence = 0.8
                        else:
                            confidence = 0.9
                        print(self.cwd + '/bin/adb/arktemp.png', self.cwd + '/res/battle/' + eachObj)
                        picInfo = pictureFind.matchImg(self.cwd + '/bin/adb/arktemp.png', self.cwd + '/res/battle/' + eachObj, confidence)
                        print(eachObj+ '：', picInfo)
                        if picInfo != None:
                            picPos = picInfo['result']
                            self.adb.click(picPos[0], picPos[1])
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