from os import getcwd, listdir
from sys import path
from time import perf_counter,sleep
from threading import Thread, Lock
from json import loads
from cv2 import fillConvexPoly, imshow, waitKey
from numpy import array
from random import choice

path.append(getcwd())
from foo.pictureR import pictureFind

class PublicCall:
    def __init__(self, adb, cwd, normal = None, high = None):
        if normal == None and high == None:
            self.updateTag()
        else:
            self.tagDict = normal
            self.highTagDict = high

        self.isTagNeedUpdate = False

        self.adb = adb
        #self.srcBefore = None
        self.regAns = None
        #self.battle = battle
        self.cwd = cwd
        self.screenShot = self.cwd + '/bin/adb/PCScreenshot.png'
        self.tag = pictureFind.picRead([self.cwd + '/res/publicCall/' + i for i in listdir(self.cwd + '/res/publicCall')])
        self.tag.sort(key = lambda x:len(x['obj']), reverse = True)
        #self.mark = pictureFind.picRead(self.cwd + '/res/panel/other/publicMark.png')
        self.lock = Lock()
        self.tagOnScreenList = []
        self.refresh = pictureFind.picRead(self.cwd + '/res/panel/publicCall/refresh.png')
        self.confirm = pictureFind.picRead(self.cwd + '/res/panel/other/confirm.png')
        self.pcInMark = pictureFind.picRead(self.cwd + '/res/panel/publicCall/inPcMark.png')
        #self.monitorFlag = False
    
    def updateTag(self):
        self.isTagNeedUpdate = True
    
    def getTag(self, src, isAutoMode = False):
        self.tagOnScreenList = []
        imSrc = src
        trytime = 0

        self.matchTag(imSrc, self.tag)

        if isAutoMode:
            if len(self.tagOnScreenList) == 5:
                return self.tagOnScreenList
            else:
                return []
        else:
            if len(self.tagOnScreenList) == 5:
                self.tagOnScreenList.sort(key = lambda x:x[1][1])
                tagOnScreenBefore3 = self.tagOnScreenList[0:3]
                tagOnScreenlast2 = self.tagOnScreenList[3:5]
                tagOnScreenBefore3.sort(key = lambda x:x[1][0])
                tagOnScreenlast2.sort(key = lambda x:x[1][0])
                tagsInTurn = []
                for eachTag in tagOnScreenBefore3:
                    tagsInTurn.append(eachTag[0])
                for eachTag in tagOnScreenlast2:
                    tagsInTurn.append(eachTag[0])
                return tagsInTurn
            else:
                return []

    def matchTag(self, src, objList):
        for each in objList:
            if len(self.tagOnScreenList) == 5:
                break
            #tInfo = pictureFind.matchImg(src, self.cwd + '/res/publicCall/' + each)
            tInfo = pictureFind.matchImg(src, each)
            if tInfo != None:
                #self.lock.acquire()
                #self.tagOnScreenList.append(self.trans(tInfo['obj']))
                self.tagOnScreenList.append((tInfo['obj'][:-4], tInfo['result']))
                tInfo['rectangle'] = list(tInfo['rectangle'])
                for i in range(4):
                    tInfo['rectangle'][i] = list(tInfo['rectangle'][i])
                    tInfo['rectangle'][i][0] = int(tInfo['rectangle'][i][0]/1440*src.shape[1] + 0.5)
                    tInfo['rectangle'][i][1] = int(tInfo['rectangle'][i][1]/810*src.shape[0] + 0.5)
                rect = array([tInfo['rectangle'][0],tInfo['rectangle'][1],tInfo['rectangle'][3],tInfo['rectangle'][2]])
                fillConvexPoly(src,rect,0)
                #imshow('img', src)
                #waitKey(0)
                #self.lock.release()

    
    def getAns(self, tagOnScreenList):
        #tempT = perf_counter()
        if tagOnScreenList == []:
            #print('匹配'+str(perf_counter() - tempT))
            return False
        #tagOnScreenList.sort()
        if self.isTagNeedUpdate: #判断是否从网站下载了新公招表
            with open(self.cwd + '/data.json', 'r') as f:
                temp = f.read()
            temp = loads(temp)['data']
            self.tagDict = temp[0]['normal']
            self.highTagDict = temp[0]['high']
            self.isTagNeedUpdate = False
        applyTagDict = self.tagDict.copy()
        if '高级资深干员' in tagOnScreenList:
            for eachTag in self.highTagDict.keys():
                applyTagDict[eachTag].extend(self.highTagDict[eachTag])
        tag0 = applyTagDict[tagOnScreenList[0]]
        tag1 = applyTagDict[tagOnScreenList[1]]
        tag2 = applyTagDict[tagOnScreenList[2]]
        tag3 = applyTagDict[tagOnScreenList[3]]
        tag4 = applyTagDict[tagOnScreenList[4]]

        tagall = tag0 + tag1 + tag2 + tag3 + tag4
        tagnew = []
        for i in tagall:
            if i not in tagnew:
                tagnew.append(i)

        ans = dict()
        for each in tagnew:
            if each in tag0:
                temp = ans.get(tagOnScreenList[0], [])
                temp.append(each)
                ans[tagOnScreenList[0]] = temp
                if each in tag1:
                    temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[1], [])
                    temp.append(each)
                    ans[tagOnScreenList[0] + '+' + tagOnScreenList[1]] = temp
                    if each in tag2:
                        temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[1] + '+' + tagOnScreenList[2], [])
                        temp.append(each)
                        ans[tagOnScreenList[0] + '+' + tagOnScreenList[1] + '+' + tagOnScreenList[2]] = temp
                        if each in tag3:
                            temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3], [])
                            temp.append(each)
                            ans[tagOnScreenList[0] + '+' + tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3]] = temp
                            if each in tag4:
                                temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                                temp.append(each)
                                ans[tagOnScreenList[0] + '+' + tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
                if each in tag2:
                    temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[2], [])
                    temp.append(each)
                    ans[tagOnScreenList[0] + '+' + tagOnScreenList[2]] = temp
                    if each in tag3:
                        temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3], [])
                        temp.append(each)
                        ans[tagOnScreenList[0] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3]] = temp
                        if each in tag4:
                            temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                            temp.append(each)
                            ans[tagOnScreenList[0] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
                if each in tag3:
                    temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[3], [])
                    temp.append(each)
                    ans[tagOnScreenList[0] + '+' + tagOnScreenList[3]] = temp
                    if each in tag4:
                        temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                        temp.append(each)
                        ans[tagOnScreenList[0] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
                if each in tag4:
                    temp = ans.get(tagOnScreenList[0] + '+' + tagOnScreenList[4], [])
                    temp.append(each)
                    ans[tagOnScreenList[0] + '+' + tagOnScreenList[4]] = temp
            if each in tag1:
                temp = ans.get(tagOnScreenList[1], [])
                temp.append(each)
                ans[tagOnScreenList[1]] = temp
                if each in tag2:
                    temp = ans.get(tagOnScreenList[1] + '+' + tagOnScreenList[2], [])
                    temp.append(each)
                    ans[tagOnScreenList[1] + '+' + tagOnScreenList[2]] = temp
                    if each in tag3:
                        temp = ans.get(tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3], [])
                        temp.append(each)
                        ans[tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3]] = temp
                        if each in tag4:
                            temp = ans.get(tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                            temp.append(each)
                            ans[tagOnScreenList[1] + '+' + tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
                if each in tag3:
                    temp = ans.get(tagOnScreenList[1] + '+' + tagOnScreenList[3], [])
                    temp.append(each)
                    ans[tagOnScreenList[1] + '+' + tagOnScreenList[3]] = temp
                    if each in tag4:
                        temp = ans.get(tagOnScreenList[1] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                        temp.append(each)
                        ans[tagOnScreenList[1] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
                if each in tag4:
                    temp = ans.get(tagOnScreenList[1] + '+' + tagOnScreenList[4], [])
                    temp.append(each)
                    ans[tagOnScreenList[1] + '+' + tagOnScreenList[4]] = temp
            if each in tag2:
                temp = ans.get(tagOnScreenList[2], [])
                temp.append(each)
                ans[tagOnScreenList[2]] = temp
                if each in tag3:
                    temp = ans.get(tagOnScreenList[2] + '+' + tagOnScreenList[3], [])
                    temp.append(each)
                    ans[tagOnScreenList[2] + '+' + tagOnScreenList[3]] = temp
                    if each in tag4:
                        temp = ans.get(tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                        temp.append(each)
                        ans[tagOnScreenList[2] + '+' + tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
                if each in tag4:
                    temp = ans.get(tagOnScreenList[2] + '+' + tagOnScreenList[4], [])
                    temp.append(each)
                    ans[tagOnScreenList[2] + '+' + tagOnScreenList[4]] = temp
            if each in tag3:
                temp = ans.get(tagOnScreenList[3], [])
                temp.append(each)
                ans[tagOnScreenList[3]] = temp
                if each in tag4:
                    temp = ans.get(tagOnScreenList[3] + '+' + tagOnScreenList[4], [])
                    temp.append(each)
                    ans[tagOnScreenList[3] + '+' + tagOnScreenList[4]] = temp
            if each in tag4:
                temp = ans.get(tagOnScreenList[4], [])
                temp.append(each)
                ans[tagOnScreenList[4]] = temp

        #print('匹配'+str(perf_counter() - tempT))
        #print(ans)
        return (ans, tagOnScreenList)

    def run(self):
        #self.srcBefore = {'pic':src,'obj':'tags'}
        while True:
            self.adb.screenShot(pngName='PCScreenshot')
            src = pictureFind.imreadCH(self.screenShot)
            tempTagList = self.getTag(src)
            if tempTagList == [] or len(tempTagList) == 5:
                break
            elif '资深干员' in tempTagList and '高级资深干员' in tempTagList:
                tempTagList.remove('资深干员')
                break
            elif '支援' in tempTagList and '支援机械' in tempTagList:
                tempTagList.remove('支援')
                break
            sleep(0.5)

        self.regAns = self.getAns(tempTagList)
        return self.regAns

    def chooseTag(self):
        is1Need = False #一星干员
        #self.adb.connect()
        self.adb.screenShot(pngName='autoPC')
        src = pictureFind.imreadCH(self.cwd + '/bin/adb/autoPC.png')
        tempTagList = self.getTag(src, isAutoMode=True)
        tagNameAndPos = dict(tempTagList)
        tagCombination = self.getAns(list(tagNameAndPos.keys()))[0]
        star4Combination = []
        star5Combination = []
        star6Combination = []
        for eachCombination in tagCombination.keys():
            if is1Need:
                pass
            else:
                tagCombination[eachCombination].sort(key=lambda x:x[0]%10)
                minStar = tagCombination[eachCombination][0][0] #最低星数
                tempNum = 0
                while minStar == 10:
                    tempNum += 1
                    minStar = tagCombination[eachCombination][tempNum][0]
                if minStar == 4:
                    star4Combination.append(eachCombination)
                elif minStar == 5:
                    star5Combination.append(eachCombination)
                elif minStar == 6:
                    star6Combination.append(eachCombination)
        if star6Combination != []:
            return 6
        if star5Combination != []:
            tagChoice = choice(star5Combination).split('+')
            tagPos = []
            for tag in tagChoice:
                tagPos.append(tagNameAndPos[tag])
            for pos in tagPos:
                self.adb.click(pos[0], pos[1])
            return 5
        if star4Combination != []:
            tagChoice = choice(star4Combination).split('+')
            tagChoice = list(set(tagChoice))
            tagPos = []
            for tag in tagChoice:
                tagPos.append(tagNameAndPos[tag])
            for pos in tagPos:
                self.adb.click(pos[0], pos[1])
            return 4
        else:
            #刷新tag
            refreshPic = pictureFind.matchImg(src, self.refresh)
            if refreshPic != None:
                for i in range(3):
                    self.adb.click(refreshPic['result'][0], refreshPic['result'][1])
                    self.adb.screenShot(pngName='autoPC')
                    confirmPic = pictureFind.matchImg(self.cwd + '/bin/adb/autoPC.png', self.refresh)
                    if confirmPic != None:
                        while pictureFind.matchImg(self.cwd + '/bin/adb/autoPC.png', self.pcInMark) == None:
                            self.adb.click(confirmPic['result'][0], confirmPic['result'][1])
                            sleep(1)
                            self.adb.screenShot(pngName='autoPC')
                        return 100
        return 0
