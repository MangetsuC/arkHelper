from os import getcwd, listdir
from sys import path
from time import sleep
from threading import Thread

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.win import toast

class BattleSchedule:
    def __init__(self, adb, app):
        self.cwd = getcwd().replace('\\', '/')
        self.adb = adb
        self.app = app
        self.listBattleImg = listdir(cwd + "/res/battle")
        self.switch = False
        self.connectSwitch = False
        self.imgInit()

    def imgInit(self):
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.act = self.cwd + "/res/panel/other/act.png"
        self.autoOff = self.cwd + "/res/panel/other/autoOff.png"
        self.autoOn = self.cwd + "/res/panel/other/autoOn.png"
        self.back = self.cwd + "/res/panel/other/back.png"
        self.battle = self.cwd + "/res/panel/other/battle.png"
        self.confirm = self.cwd + "/res/panel/other/confirm.png"
        self.friendList = self.cwd + "/res/panel/other/friendList.png"
        self.get = self.cwd + "/res/panel/other/get.png"
        self.home = self.cwd + "/res/panel/other/home.png"
        self.task = self.cwd + "/res/panel/other/task.png"
        self.visit = self.cwd + "/res/panel/other/visit.png"
        self.visitFinish = self.cwd + "/res/panel/other/visitFinish.png"
        self.visitNext = self.cwd + "/res/panel/other/visitNext.png"
        self.I = {'TH':self.cwd + "/res/panel/level/I/thread.png", 'EX':self.cwd + "/res/panel/level/I/exterminate.png",\
            'RS':self.cwd + "/res/panel/level/I/resource.png", 'PR':self.cwd + "/res/panel/level/I/chip.png"}
        self.II = {'A':self.cwd + "/res/panel/level/II/A.png", 'B':self.cwd + "/res/panel/level/II/B.png",\
                'C':self.cwd + "/res/panel/level/II/C.png", 'D':self.cwd + "/res/panel/level/II/D.png",\
                'AP':self.cwd + "/res/panel/level/II/AP.png", 'CA':self.cwd + "/res/panel/level/II/CA.png",\
                'CE':self.cwd + "/res/panel/level/II/CE.png", 'SK':self.cwd + "/res/panel/level/II/SK.png",\
                'LS':self.cwd + "/res/panel/level/II/LS.png", '01':self.cwd + "/res/panel/level/II/e01.png",\
                '02':self.cwd + "/res/panel/level/II/e02.png", '03':self.cwd + "/res/panel/level/II/e03.png",\
                '0':self.cwd + "/res/panel/level/II/ep0.png", '1':self.cwd + "/res/panel/level/II/ep1.png",\
                '2':self.cwd + "/res/panel/level/II/ep2.png", '3':self.cwd + "/res/panel/level/II/ep3.png",\
                '4':self.cwd + "/res/panel/level/II/ep4.png", '5':self.cwd + "/res/panel/level/II/ep5.png",\
                '6':self.cwd + "/res/panel/level/II/ep6.png"}

    def goLevel(self, level):
        levelList = level.split(':')
        levelList = levelList[0].split('-')
        for i in range(2):
            levelList[0][i] = levelList[0][i].upper()

        if levelList[0][0] == 'PR':
            levelName = ''.join(levelList[0])
        else:
            levelName = levelList[0][1] + levelList[0][2]

        if levelList[0][0] == 'TH' and 'S' in levelList[0][1]:
            levelList[0][1] = levelList[0][1][1]

        #前往一级菜单
        while True:
            if self.adb.screenShot():
                picTh = pictureFind.matchImg(self.screenShot, self.I['TH'])
                if picTh != None:
                    break
            else:
                return 'Fail to get screenshot'
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
                            return 'Fail to get screenshot'
                    else:
                        self.runTimes()
                        return 'Now in battle'
                
            else:
                return 'Fail to get screenshot'

        #二级菜单的选择
        if self.adb.screenShot():
            picColumn = pictureFind.matchImg(self.screenShot, self.I[levelList[0]])
            if picColumn != None:
                posColumn = picColumn['result']
                self.adb.click(posColumn[0], posColumn[1])
            else:
                return 'Column Choice Wrong'
        else:
            return 'Fail to get screenshot'

        #三级菜单的选择
        if levelList[0] == 'TH':
            #主线
            pass
        elif levelList[0] == 'RS':
            #物资筹备
            pass
        elif levelList[0] == 'PR':
            #芯片搜索
            if self.adb.screenShot():
                picChoice = pictureFind.matchImg(self.screenShot, self.II[levelList[1]])
                if picChoice != None:
                    posChoice = picChoice['result']
                    self.adb.click(posChoice[0], posChoice[1])
                else:
                    return 'Unoppen today'
            else:
                return 'Fail to get screenshot'
        elif levelList[0] == 'EX':
            #剿灭
            if self.adb.screenShot():
                picChoice = pictureFind.matchImg(self.screenShot, self.II[levelList[1]])
                if picChoice != None:
                    posChoice = picChoice['result']
                    self.adb.click(posChoice[0], posChoice[1])
                    self.runTimes(levelList[1])
                    return 'Finish'
            else:
                return 'Fail to get screenshot'
            pass
        else:
            return 'Wrong Input'


    def runTimes(self, times = 1):
        isFirstTurn = True
        self.connectSwitch = True
        times = int(times)
        for tryTimes in range(20):
            if self.connectSwitch:
                self.switch = self.adb.connect()
                if self.switch:
                    break
                tryTimes += 1
            else:
                break
        
        print(self.switch)
        if (not self.switch) and self.connectSwitch:
            self.app.setButton(1)
            self.app.setState("连接失败，请检查配置文件或重启模拟器")
            toast.broadcastMsg("ArkHelper", "连接失败，请检查配置文件或重启模拟器", self.app.icon)
        else:
            while self.switch and (times > 0 or times == -1):
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
                            self.adb.click(picPos[0], picPos[1])
                            if eachObj == "end.png":
                                if times != -1:
                                    times -= 1
                            elif eachObj == "cancel.png":
                                self.switch = False
                                self.app.setState("理智耗尽")
                                toast.broadcastMsg("ArkHelper", "理智耗尽", self.app.icon)
                                self.app.setButton(1)
                                break
                sleep(1)
    def stop(self):
        self.connectSwitch = False
        self.switch = False