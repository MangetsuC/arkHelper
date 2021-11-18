from os import getcwd, listdir
from sys import path

from foo.pictureR import pictureFind
from foo.pictureR.colorDetect import findColorBlock
from foo.win import toast
from common2 import adb

from foo.ocr.ocr import getText, findTextPos, findTextPos_withConficende

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
        self.visits = pictureFind.picRead(self.cwd + '/res/panel/other/visit.png')

        self.listGoTo = listGoTo
        self.mainpage = self.listGoTo[0]
        self.home = self.listGoTo[1]
        self.mainpageMark = self.listGoTo[2]
        self.listGetCredit = [self.visitNext, self.visitFinish]
        

    def enter(self):
        '进入好友页面'
        while True:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                ans = findTextPos(ocrResult, ['好反', '好屁'], []) #试了几次 就这两个结果 总之是出不了好友
                for i in range(5):
                    adb.click(ans[0][0], ans[0][1])
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['好友列表'], [])
                    if temp != None:
                        adb.click(temp[0][0], temp[0][1])
                        if findTextPos(getText(adb.getScreen_std(True)), ['访问基建'], []) != None:
                            return
            
            adb.clickHome()
            img = adb.getScreen_std()
            ans = pictureFind.matchImg(img, './res/panel/other/friendIcon.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                adb.click(ans['result'][0], ans['result'][1])
            
            for i in range(5):
                temp = findTextPos(getText(adb.getScreen_std(True)), ['好友列表'], [])
                if temp != None:
                    adb.click(temp[0][0], temp[0][1])
                    if findTextPos(getText(adb.getScreen_std(True)), ['访问基建'], []) != None:
                        return 
            return 

    def visit(self):
        '访问基建'
        img = adb.getScreen_std(True)
        ocrResult = getText(img)
        ans = findTextPos(ocrResult, ['访问基建'], [])
        if ans != None:
            for i in range(5):
                adb.click(ans[0][0], ans[0][1])
                if findTextPos(getText(adb.getScreen_std(True)), ['访问下位'], []) != None:
                    break

        lastAns = ''
        while True:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)
            ans = findTextPos(ocrResult, ['会客室'], [])
            if ans == lastAns:
                ans = None

            if ans != None:
                if findTextPos(getText(adb.getScreen_std(True)), ['访问下位'], []) != None:
                    lastAns = ans[2]
                    img = adb.getScreen_std()
                    ans = findColorBlock(img, [(200, 225), (85, 100), (5, 20)])
                    if ans != None:
                        adb.click(ans[0], ans[1])
                    else:
                        break


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
            vInfo = pictureFind.matchImg(adb.getScreen_std(), self.visits)
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

    def run(self, switch):
        self.switch = switch
        self.enter()
        self.visit()

        self.switch = False
    
    def stop(self):
        self.switch = False