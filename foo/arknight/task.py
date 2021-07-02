from os import getcwd, listdir
from sys import path

from foo.pictureR import pictureFind
from foo.win import toast

class Task:
    def __init__(self, adb, cwd, ico, listGoTo):
        self.adb = adb
        self.cwd = cwd
        self.switch = False
        self.icon = ico
        #self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.task = pictureFind.picRead(self.cwd + "/res/panel/other/task.png")
        self.get = pictureFind.picRead(self.cwd + "/res/panel/other/get.png")
        self.daySel = pictureFind.picRead(self.cwd + "/res/panel/other/dailyTaskSelect.png")
        self.actSel = pictureFind.picRead(self.cwd + "/res/panel/other/actSelect.png")
        self.weekUnSel = pictureFind.picRead(self.cwd + "/res/panel/other/weeklyTaskUnSelect.png")
        self.weekSel = pictureFind.picRead(self.cwd + "/res/panel/other/weeklyTaskSelect.png")
        self.back = pictureFind.picRead(self.cwd + '/res/panel/other/back.png')
        self.rewardFinish = pictureFind.picRead(self.cwd + '/res/panel/other/rewardFinish.png')
        self.collectAll = pictureFind.picRead(self.cwd + '/res/panel/other/collectAll.png')

        self.listGoTo = listGoTo
        self.mainpage = self.listGoTo[0]
        self.home = self.listGoTo[1]
        self.mainpageMark = self.listGoTo[2]

    def goToMainpage(self):
        listGoToTemp = self.listGoTo.copy()
        tryCount = 0
        while self.switch:
            screenshot = self.adb.getScreen_std()
            for eachStep in listGoToTemp:
                bInfo = pictureFind.matchImg(screenshot, eachStep)
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


    def checkTask(self):
        tryCount = 0
        cInfo = pictureFind.matchImg(self.adb.getScreen_std(), self.task)
        if cInfo == None:
            print('无法检测到任务交付入口，中断任务交付后续')
            return False
        else:
            while self.switch:
                self.adb.click(cInfo['result'][0], cInfo['result'][1])
                
                screenshot = self.adb.getScreen_std()
                if pictureFind.matchImg(screenshot, self.daySel) != None:
                    return True
                elif pictureFind.matchImg(screenshot, self.actSel) != None:
                    return True
                else:
                    tryCount += 1
                    if tryCount > 5:
                        return False

    def submitTask(self):
        #交付当前栏的任务
        endCount = 0
        while self.switch:
            screenshot = self.adb.getScreen_std()
            #gInfo = pictureFind.matchImg(screenshot, self.get, 0.9)
            collectAllInfo = pictureFind.matchImg(screenshot, self.collectAll, 0.8)
            backInfo = pictureFind.matchImg(screenshot, self.back, 0.9)
            #rewardFinishInfo = pictureFind.matchMultiImg(screenshot, self.rewardFinish, 
            #                                            confidencevalue = self.adb.getTagConfidence())[0]
            #if rewardFinishInfo != None:
            #    rewardFinishInfo.sort(key = lambda x:x[1])
            #    if rewardFinishInfo[0][1] < 250:#该栏任务交付全部完成
            #        return True
            if collectAllInfo != None: #有任务待交付
                endCount = 0
                self.adb.click(collectAllInfo['result'][0], collectAllInfo['result'][1])
                continue
            elif backInfo != None: #没有任务待交付
                endCount += 1
                if endCount > 3:
                    return True
                else:
                    continue
            else: #获取了奖励
                endCount = 0
                self.adb.click(720, 120)
                continue

    def oneByOne(self):
        #self.adb.screenShot()
        tryCount = 0
        self.submitTask()
        while self.switch:
            #切换到每周任务
            wInfo = pictureFind.matchImg(self.adb.getScreen_std(), self.weekUnSel)
            self.adb.click(wInfo['result'][0], wInfo['result'][1])
            wInfo = pictureFind.matchImg(self.adb.getScreen_std(), self.weekSel)
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