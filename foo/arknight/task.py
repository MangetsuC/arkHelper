from os import getcwd, listdir
from sys import path
#from time import sleep

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.win import toast

class Task:
    def __init__(self, adb, cwd, ico):
        self.adb = adb
        self.cwd = cwd
        self.switch = False
        self.icon = ico
        self.home = pictureFind.picRead(self.cwd + "/res/panel/other/home.png")
        self.mainpage = pictureFind.picRead(self.cwd + "/res/panel/other/mainpage.png")
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.task = pictureFind.picRead(self.cwd + "/res/panel/other/task.png")
        self.taskNo = pictureFind.picRead(self.cwd + "/res/panel/other/taskNo.png")
        self.get = pictureFind.picRead(self.cwd + "/res/panel/other/get.png")
        self.getMaterial = pictureFind.picRead(self.cwd + "/res/panel/other/getMaterial.png")
        self.daySel = pictureFind.picRead(self.cwd + "/res/panel/other/dailyTaskSelect.png")
        self.actSel = pictureFind.picRead(self.cwd + "/res/panel/other/actSelect.png")
        self.weekUnSel = pictureFind.picRead(self.cwd + "/res/panel/other/weeklyTaskUnSelect.png")
        self.weekSel = pictureFind.picRead(self.cwd + "/res/panel/other/weeklyTaskSelect.png")
        self.mainpageMark = pictureFind.picRead(self.cwd + "/res/panel/other/act.png")
        self.waitForNew = pictureFind.picRead(self.cwd + "/res/panel/other/waitForNew.png")

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
                elif pictureFind.matchImg(self.screenShot, self.actSel) != None:
                    return True
                else:
                    tryCount += 1
                    if tryCount > 5:
                        return False

    def submitTask(self):
        while self.switch:
            gInfo = pictureFind.matchImg(self.screenShot, self.get, 0.9)
            nInfo = pictureFind.matchImg(self.screenShot, self.waitForNew, 0.9)
            if nInfo != None:
                return True
            if gInfo == None:
                mInfo = pictureFind.matchImg(self.screenShot, self.getMaterial)
                if mInfo == None:
                    return True
                #break
            else:
                self.adb.click(gInfo['result'][0], gInfo['result'][1])
            
            tryFlag = False
            while self.switch:
                self.adb.screenShot()
                mInfo = pictureFind.matchImg(self.screenShot, self.getMaterial)
                hInfo = pictureFind.matchImg(self.screenShot, self.home)
                if mInfo != None:
                    tryFlag = True
                    self.adb.click(mInfo['result'][0], mInfo['result'][1])
                elif hInfo != None:
                    if tryFlag:
                        tryFlag = False
                        continue
                    else:
                        self.adb.screenShot()
                        break

    def oneByOne(self):
        #self.adb.screenShot()
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
        if self.switch and (not condition0):
            toast.broadcastMsg("ArkHelper", "任务交付出错", self.icon)

        elif self.switch and (not condition1):
            toast.broadcastMsg("ArkHelper", "无需任务交付", self.icon)
            
        elif self.switch:
            self.goToMainpage()
            toast.broadcastMsg("ArkHelper", "任务交付完成", self.icon)
            
        self.switch = False

    def stop(self):
        self.switch = False