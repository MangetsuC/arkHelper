from os import getcwd, listdir
from sys import path

from foo.pictureR import pictureFind
from common2 import adb
from foo.ocr.ocr import getText, findTextPos, findTextPos_withConficende

class Task:
    def __init__(self, cwd, ico, listGoTo):
        self.switch = False

    def enter(self):
        '进入任务交付页面'
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                ans = findTextPos(ocrResult, ['任务'], [])
                for i in range(5):
                    adb.click(ans[0][0], ans[0][1])
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['日'], [])
                    if temp != None:
                        adb.click(temp[0][0], temp[0][1])
                        return 
            
            adb.clickHome()
            img = adb.getScreen_std()
            ans = pictureFind.matchImg(img, './res/panel/other/taskIcon.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                adb.click(ans['result'][0], ans['result'][1])
            
            for i in range(5):
                temp = findTextPos(getText(adb.getScreen_std(True)), ['日'], [])
                if temp != None:
                    adb.click(temp[0][0], temp[0][1])
                    return 
            return 


    def submitTask(self):
        #交付当前栏的任务
        count = 0
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['收集全部', '获得物资'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
            else:
                count += 1
                if count > 3:
                    break

    def run(self, switch):
        self.switch = switch

        self.enter()
        if not self.switch: return 

        self.submitTask()
        if not self.switch: return 

        img = adb.getScreen_std(True)
        ocrResult = getText(img)

        ans = findTextPos(ocrResult, ['周常任务'], [])
        if ans != None:
            adb.click(ans[0][0], ans[0][1])
        if not self.switch: return 

        self.submitTask()


    def stop(self):
        self.switch = False