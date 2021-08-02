from os import getcwd, listdir
from sys import path

from foo.pictureR import pictureFind
from foo.win import toast
from common2 import adb

class Credit:
    def __init__(self, cwd, listGoTo):
        self.cwd = cwd
        self.switch = False
        self.icon = self.cwd + "/res/ico.ico"
        #self.home = pictureFind.picRead(self.cwd + "/res/panel/other/home.png")
        #self.mainpage = pictureFind.picRead(self.cwd + "/res/panel/other/mainpage.png")
        #self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        #self.mainpageMark = pictureFind.picRead(self.cwd + "/res/panel/other/act.png")
        self.frendList = pictureFind.picRead(self.cwd + '/res/panel/other/friendList.png')
        self.visitNext = pictureFind.picRead(self.cwd + '/res/panel/other/visitNext.png')
        self.visitFinish = pictureFind.picRead(self.cwd + '/res/panel/other/visitFinish.png')
        self.friends = pictureFind.picRead(self.cwd + '/res/panel/other/friends.png')
        self.visit = pictureFind.picRead(self.cwd + '/res/panel/other/visit.png')

        self.listGoTo = listGoTo
        self.mainpage = self.listGoTo[0]
        self.home = self.listGoTo[1]
        self.mainpageMark = self.listGoTo[2]
        self.listGetCredit = [self.visitNext, self.visitFinish]
        

    def goToMainpage(self):
        listGoToTemp = self.listGoTo.copy()
        tryCount = 0
        while self.switch:
            screenshot = adb.getScreen_std()
            for eachStep in listGoToTemp:
                bInfo = pictureFind.matchImg(screenshot, eachStep)
                if bInfo != None:
                    listGoToTemp.remove(eachStep)
                    break
            else:
                listGoToTemp = self.listGoTo.copy()
                tryCount += 1
                if tryCount > 10:
                    return False

            if bInfo != None:
                if bInfo['obj'] == 'act.png': #self.mainpageMark
                    return True
                else:
                    adb.click(bInfo['result'][0], bInfo['result'][1])

    def openCard(self):
        tryTime = 0
        while self.switch:
            screenshot = adb.getScreen_std()
            fInfo = pictureFind.matchImg(screenshot, self.friends)
            if fInfo != None:
                adb.click(fInfo['result'][0], fInfo['result'][1])
            else:
                fInfo = pictureFind.matchImg(screenshot, self.frendList)
                if fInfo != None:
                    return fInfo
                elif tryTime > 10:
                    print('无法找到好友入口，中断信用获取后续操作')
                    return False
                tryTime += 1

    def openFriendList(self, fInfo):
        tryTime = 0
        while self.switch:
            adb.click(fInfo['result'][0], fInfo['result'][1])
            vInfo = pictureFind.matchImg(adb.getScreen_std(), self.visit)
            if vInfo != None:
                return vInfo
            elif tryTime > 10:
                return False
            tryTime += 1

    def enterCons(self, vInfo):
        tryTime = 0
        breakFlag = False
        while self.switch:
            adb.click(vInfo['result'][0], vInfo['result'][1])
            screenshot = adb.getScreen_std()
            for each in self.listGetCredit:
                gInfo = pictureFind.matchImg(screenshot, each, 0.95)
                if gInfo != None:
                    breakFlag = True
                    break
            if breakFlag:
                break
            if tryTime > 10:
                print("cannot visitCons")
                return False
            tryTime += 1

        while self.switch:
            tryTime = 0
            if gInfo == None:
                tryTime += 1
                if tryTime > 5:
                    print('visit next failed')
                    break
                for each in self.listGetCredit:
                    gInfo = pictureFind.matchImg(adb.getScreen_std(), each, 0.95)
                    if gInfo != None:
                        break
            elif gInfo['obj'] == 'visitFinish.png':
                break
            else:
                tryTime = 0
                adb.click(gInfo['result'][0], gInfo['result'][1])
                for each in self.listGetCredit:
                    gInfo = pictureFind.matchImg(adb.getScreen_std(), each, 0.95)
                    if gInfo != None:
                        break

    def run(self, switchI):
        self.switch = switchI
        isNormal = True
        flag = self.goToMainpage()
        if self.switch and flag:
            infoFlag = self.openCard()
            if self.switch and infoFlag != None:
                infoFlag2 = self.openFriendList(infoFlag)
                if self.switch and infoFlag2 != None:
                    self.enterCons(infoFlag2)
                else:
                    isNormal = False
            else:
                isNormal = False
        else:
            isNormal = False

        self.goToMainpage()
        if isNormal and self.switch:
            toast.broadcastMsg("ArkHelper", "获取信用点成功", self.icon)
        elif self.switch:
            toast.broadcastMsg("ArkHelper", "获取信用点出错", self.icon)

        self.switch = False
    
    def stop(self):
        self.switch = False