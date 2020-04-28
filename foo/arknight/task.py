from os import getcwd, listdir
from sys import path
#from time import sleep

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.win import toast

class Task:
    def __init__(self, adb, cwd):
        self.adb = adb
        self.cwd = cwd
        self.switch = False
        self.icon = self.cwd + "/res/ico.ico"
        self.home = self.cwd + "/res/panel/other/home.png"
        self.mainpage = self.cwd + "/res/panel/other/mainpage.png"
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.task = self.cwd + "/res/panel/other/task.png"
        self.taskNo = self.cwd + "/res/panel/other/taskNo.png"
        self.get = self.cwd + "/res/panel/other/get.png"
        self.getMaterial = self.cwd + "/res/panel/other/getMaterial.png"
        self.daySel = self.cwd + "/res/panel/other/dailyTaskSelect.png"
        self.weekUnSel = self.cwd + "/res/panel/other/weeklyTaskUnSelect.png"
        self.weekSel = self.cwd + "/res/panel/other/weeklyTaskSelect.png"
        self.mainpageMark = self.cwd + "/res/panel/other/act.png"

        self.listGoTo = [self.mainpage, self.home, self.mainpageMark]

    def goToMainpage(self):
        listGoToTemp = self.listGoTo.copy()
        tryCount = 0
        while self.switch:
            self.adb.screenShot()
            for eachStep in listGoToTemp:
                bInfo = pictureFind.matchImg(self.screenShot, eachStep)
                if bInfo != None:
                    listGoToTemp.remove(eachStep)
                    break
            else:
                listGoToTemp = self.listGoTo.copy()
                tryCount += 1
                if tryCount > 5:
                    return False

            if bInfo != None:
                if bInfo['obj'] == 'act.png':
                    return True
                else:
                    self.adb.click(bInfo['result'][0], bInfo['result'][1])

        '''self.adb.screenShot()
        if pictureFind.matchImg(self.screenShot, self.mainpageMark) == None:
            bInfo = pictureFind.matchImg(self.screenShot, self.home)
            if bInfo == None:
                return False
            else:
                self.adb.click(bInfo['result'][0], bInfo['result'][1])
                self.adb.screenShot()
                bInfo = pictureFind.matchImg(self.screenShot, self.mainpage)
                self.adb.click(bInfo['result'][0], bInfo['result'][1])'''

    def checkTask(self):
        tryCount = 0
        self.adb.screenShot()
        cInfo = pictureFind.matchImg(self.screenShot, self.task)
        if cInfo == None:
            return False
        else:
            while self.switch:
                self.adb.click(cInfo['result'][0], cInfo['result'][1])
                
                self.adb.screenShot()
                if pictureFind.matchImg(self.screenShot, self.daySel) != None:
                    return True
                else:
                    tryCount += 1
                    if tryCount > 5:
                        return False

    def submitTask(self):
        while self.switch:
            gInfo = pictureFind.matchImg(self.screenShot, self.get, 1.0)
            if gInfo == None:
                return True
                #break
            self.adb.click(gInfo['result'][0], gInfo['result'][1])
            self.adb.screenShot()
            mInfo = pictureFind.matchImg(self.screenShot, self.getMaterial)
            if mInfo != None:
                self.adb.click(mInfo['result'][0], mInfo['result'][1])
                self.adb.screenShot()

    def oneByOne(self):
        tryCount = 0
        self.submitTask()
        while self.switch:
            wInfo = pictureFind.matchImg(self.screenShot, self.weekUnSel)
            self.adb.click(wInfo['result'][0], wInfo['result'][1])
            self.adb.screenShot()
            wInfo = pictureFind.matchImg(self.screenShot, self.weekSel)
            if wInfo != None:
                break
            else:
                tryCount += 1
                if tryCount > 5:
                    return False
        self.submitTask()



    def run(self, switchI):
        self.switch = switchI
        condition0 = self.goToMainpage()
        if condition0:
            condition1 = self.checkTask()
            if condition1:
                self.oneByOne()
        if (not condition0) and self.switch:
            toast.broadcastMsg("ArkHelper", "任务交付出错", self.icon)

        elif not condition1:
            toast.broadcastMsg("ArkHelper", "无需任务交付", self.icon)
            
        else:
            self.goToMainpage()
            toast.broadcastMsg("ArkHelper", "任务交付完成", self.icon)
            
        self.switch = False

    def stop(self):
        self.switch = False