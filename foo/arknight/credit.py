from os import getcwd, listdir
from sys import path

from foo.pictureR import pictureFind
from foo.pictureR.colorDetect import findColorBlock
from common2 import adb

from foo.ocr.ocr import getText, findTextPos

class Credit:
    def __init__(self, cwd, listGoTo):
        self.cwd = cwd
        self.switch = False
        self.icon = self.cwd + "/res/ico.ico"
        
        

    def enter(self):
        '进入好友页面'
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                ans = findTextPos(ocrResult, ['好反', '好屁'], []) #试了几次 就这两个结果 总之是出不了好友
                for i in range(5):
                    if not self.switch: return 
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
                if not self.switch: return 
                temp = findTextPos(getText(adb.getScreen_std(True)), ['好友列表'], [])
                if temp != None:
                    adb.click(temp[0][0], temp[0][1])
                    if findTextPos(getText(adb.getScreen_std(True)), ['访问基建'], []) != None:
                        return 

    def visit(self):
        '访问基建'
        img = adb.getScreen_std(True)
        ocrResult = getText(img)
        ans = findTextPos(ocrResult, ['访问基建'], [])
        if ans != None:
            for i in range(5):
                if not self.switch: return 
                adb.click(ans[0][0], ans[0][1])
                if findTextPos(getText(adb.getScreen_std(True)), ['访问下位'], []) != None:
                    break

        lastAns = ''
        while self.switch:
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

    def run(self, switch):
        self.switch = switch
        self.enter()
        if not self.switch: return 
        self.visit()

        self.switch = False
    
    def stop(self):
        self.switch = False