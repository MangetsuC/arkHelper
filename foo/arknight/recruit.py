#公开招募功能实现部分代码
#UI中应为单纯的UI部分
import json
from sys import path as syspath
from os import getcwd
syspath.append(getcwd())

from foo.ocr.ocr import getText, findTextPos
from foo.pictureR import pictureFind
from common2 import adb

class Recruit:
    def __init__(self, priority = [-6, 5, 4]):


        temp = self.readData()
        self.normal = temp[0]
        self.high = temp[1]
        self.allTags = list(self.normal.keys()) + ['高级资深干员']

        self.confirm_refresh_pos = None
        self.confirm_recruit_pos = None

        self.priority = priority
        self.switch = True

    def readData(self):
        '获取公开招募的信息'
        #未做异常处理
        with open('./data.json', 'r', encoding='UTF-8') as f:
            data = json.loads(f.read())['data'][0]
        return (data['normal'], data['high'])
    

    def getTag(self):
        '获取屏幕上的5个tag与他们的坐标'

        img = adb.getScreen_std(True)
        ocrResult = getText(img)

        tags = []
        for i in ocrResult:
            tagName = i[1].split('、')[1].strip()
            if tagName in self.allTags:
                tags.append([tagName, (int((i[0][0][0] + i[0][1][0])/2), int((i[0][0][1] + i[0][2][1])/2))])

            if len(tags) == 5:
                break

        return tags

    def refresh(self):
        '刷新标签'

        img = adb.getScreen_std(True)
        ocrResult = getText(img)

        ans = findTextPos(ocrResult, ['点击刷新标签'], [])
        if ans != None:
            #可以刷新
            adb.click(ans[0][0], ans[0][1])

            return self.confirm_refresh()
            
        #无法刷新
        return False

    def confirm_refresh(self):
        '刷新后点击确认'
        for i in range(5):
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['联络机会'], [])
            if ans != None:
                break
        if self.confirm_refresh_pos == None:
            startPos = ans[1][1]

            for i in range(1000):
                img = adb.getScreen_std(True)
                ocrResult = getText(img)

                ans = findTextPos(ocrResult, ['招募说明'], [])
                if ans != None:
                    self.confirm_refresh_pos = [startPos[0], startPos[1] + (i-1)*25]
                    return True
                adb.click(startPos[0], startPos[1] + i*25)  
        else:
            adb.click(self.confirm_refresh_pos[0], self.confirm_refresh_pos[1])
            return True
        return False

    def confirm_recruit(self):
        '确认招募'
        if self.confirm_recruit_pos == None:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            temp1 = findTextPos(ocrResult, ['点击刷新标签', '人脉资源联络中'], [])
            temp2 = findTextPos(ocrResult, ['招募预算'], [])
            self.confirm_recruit_pos =[temp1[0][0], temp2[0][1]]
        adb.click(self.confirm_recruit_pos[0], self.confirm_recruit_pos[1])

    def chooseTag(self, tagName, tags):
        '选择某个tag'
        pos = None
        for i in tags:
            if i[0] == tagName:
                pos = i[1]
                break

        if pos != None:
            adb.click(pos[0], pos[1])
        else:
            adb.clickBack()

    def addTime(self, targetTime = '09'):
        '调整到9小时'
        for i in range(5):
            img = adb.getScreen_std(True)
            ocrResult = getText(img)
            ans = findTextPos(ocrResult, ['09', '01'], [])
            if ans != None:
                temp0 = findTextPos(ocrResult, ['招募说明'], [])
                temp1 = findTextPos(ocrResult, ['招募时限'], [])
                downPos = [ans[1][0][0], temp1[0][1]*2 - temp0[0][1]]

                if targetTime in ans[2]:
                    return 
                else:
                    adb.click(downPos[0], downPos[1])
                    continue
        else:
            return 




    def ans_set(self, tagData, tagOnScreenList):
        tags = tuple(
            set(tuple(x) for x in tagData[tagOnScreenList[i]])
            for i in range(5)
        )
        ans = dict()

        def check_combination(args):
            tmp = set.intersection(*[tags[i] for i in args])
            if tmp == set(): return False
            ans["+".join([tagOnScreenList[i] for i in args])] = [list(i) for i in tmp]
            return True

        def recursive_check(history=None, parent=0):
            # 最多只有 5 个标签
            if len(history) == 5: return
            for i in range(parent, 5):
                new = history + [i]
                check_combination(new)
                recursive_check(new, i + 1)

        recursive_check([])
        return ans

    def getAns(self, tags):
        tagOnScreenList = [x[0] for x in tags]
        if tagOnScreenList == []:
            return False
        applyTagDict = self.normal.copy()
        if '高级资深干员' in tagOnScreenList:
            for eachTag in self.high.keys():
                applyTagDict[eachTag].extend(self.high[eachTag])

        ans = self.ans_set(applyTagDict, tagOnScreenList)

        return ans

    def doRecruit_once(self, priority = [-6, 5, 4]):
        '执行一次招募'
        tags = self.getTag()
        ans = list(self.getAns(tags).items())

        for i in ans:
            i[1].sort(key = lambda x:x[0])
        
        ans.sort(key = lambda x:x[1][0][0], reverse=True)#从高星级组合往低星级排序

        while self.switch:
            for i in priority:
                for j in ans:
                    if j[1][0][0] == abs(i):
                        #找到了优先级最高的星级组合
                        if i > 0:
                            targetTags = j[0].split('+')
                            for k in targetTags:
                                self.chooseTag(k, tags)
                            self.addTime()
                            self.confirm_recruit()
                            return True
                        else:
                            adb.clickBack()
                            return True
                        
            else:
                #无法找到优先级列表中有的星级组合
                #可刷新则刷新，不可刷新则直接招募
                if self.refresh():
                    continue
                else:
                    if not self.switch: return 
                    self.addTime()
                    if not self.switch: return 
                    self.confirm_recruit()
                    return True

    def employ(self):
        '聘用'
        count = 0
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['聘用候选人'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
                for i in range (20):
                    if not self.switch: return 
                    adb.clickUpRight()

                    img = adb.getScreen_std(True)
                    ocrResult = getText(img)
                    ans = findTextPos(ocrResult, ['公开招募'], [])
                    if ans != None:
                        break
            else:
                count += 1
                if count > 3:
                    return 
        

    def doRecruit(self):
        count = 0
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['开始招募'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
                self.doRecruit_once(self.priority)
            else:
                count += 1
                if count > 3:
                    return 
        
    
    def enter(self):
        '进入自动公招页面'
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                ans = findTextPos(ocrResult, ['公开招募'], [])
                for i in range(5):
                    adb.click(ans[0][0], ans[0][1])
                    if findTextPos(getText(adb.getScreen_std(True)), ['开始招募', '聘用候选人', '停止招募'], []) != None:
                        return 
            
            adb.clickHome()
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['公开招募'], [])
            adb.click(ans[1][0][0], ans[1][0][1])
            for i in range(5):
                if not self.switch: return 
                if findTextPos(getText(adb.getScreen_std(True)), ['开始招募', '聘用候选人', '停止招募'], []) != None:
                    return 
            return 


    def run(self):
        '完整执行自动公招'
        self.enter()
        self.employ()
        self.doRecruit()

    def stop(self):
        self.switch = False
