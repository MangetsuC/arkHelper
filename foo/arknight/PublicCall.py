from os import getcwd, listdir
from sys import path
from time import perf_counter,sleep, time
from json import loads
from cv2 import fillConvexPoly
from numpy import array
from random import choice

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
        self.regAns = None
        self.cwd = cwd
        self.tag = pictureFind.picRead([self.cwd + '/res/publicCall/' + i for i in listdir(self.cwd + '/res/publicCall')])
        self.tag.sort(key = lambda x:len(x['obj']), reverse = True)
        self.tagOnScreenList = []
        self.refresh = pictureFind.picRead(self.cwd + '/res/panel/publicCall/refresh.png')
        self.confirm = pictureFind.picRead(self.cwd + '/res/panel/other/confirm.png')
        self.pcInMark = pictureFind.picRead(self.cwd + '/res/panel/publicCall/inPcMark.png')

        self.tagConfidence = 0.75

        self.is1Need = False
        self.is5Need = False
        #self.monitorFlag = False
    
    def setStar(self, star, func, state = True):
        if func:
            if star == 1:
                self.is1Need = state
            elif star == 5:
                self.is5Need = state
        if star == 1:
            return self.is1Need
        elif star == 5:
            return self.is5Need

    def updateTag(self):
        self.isTagNeedUpdate = True
    
    def getTag(self, src, isAutoMode = False):
        self.tagOnScreenList = []
        imSrc = src

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
        self.tagConfidence = self.adb.getTagConfidence()
        for each in objList:
            if len(self.tagOnScreenList) == 5:
                break
            tInfo = pictureFind.matchImg(src, each, confidencevalue = self.tagConfidence)
            if tInfo != None:
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

    def getAns(self, tagOnScreenList):
        if tagOnScreenList == []:
            return False
        if self.isTagNeedUpdate: #判断是否从网站下载了新公招表
            with open(self.cwd + '/data.json', 'r', encoding = 'UTF-8') as f:
                temp = f.read()
            temp = loads(temp)['data']
            self.tagDict = temp[0]['normal']
            self.highTagDict = temp[0]['high']
            self.isTagNeedUpdate = False
        applyTagDict = self.tagDict.copy()
        if '高级资深干员' in tagOnScreenList:
            for eachTag in self.highTagDict.keys():
                applyTagDict[eachTag].extend(self.highTagDict[eachTag])

        ans = self.ans_set(applyTagDict, tagOnScreenList)

        return (ans, tagOnScreenList)

    def run(self):
        while True:
            tempTagList = self.getTag(self.adb.getScreen_std())
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
        src = self.adb.getScreen_std()
        tempTagList = self.getTag(src, isAutoMode=True)
        if tempTagList == []:
            return 6 #出现错误，跳过此组
        if self.is1Need: #小车
            for i in tempTagList:
                if i[0] == '支援机械':
                    return 1
        tagNameAndPos = dict(tempTagList)
        tagCombination = self.getAns(list(tagNameAndPos.keys()))[0]
        star4Combination = []
        star5Combination = []
        star6Combination = []
        for eachCombination in tagCombination.keys():
            tagCombination[eachCombination].sort(key=lambda x:x[0]%10)
            minStar = tagCombination[eachCombination][0][0] #最低星数
            tempNum = 0
            while minStar == 10:
                tempNum += 1
                if len(tagCombination[eachCombination]) == tempNum:
                    if self.is1Need:
                        return 1
                    else:
                        break
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
            if self.is5Need:
                return 6 #设定保留五星时返回6，即把这组5星tag当作6星处理，保留此组tag
            else:
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
                    sleep(1)
                    startTime = perf_counter()
                    while True:
                        if perf_counter() - startTime > 20:
                            break
                        confirmPic = pictureFind.matchImg(self.adb.getScreen_std(), self.confirm)
                        if confirmPic != None:
                            self.adb.click(confirmPic['result'][0], confirmPic['result'][1])
                            sleep(1)
                        else:
                            return 100
        return 0 #返回0代表不保留1星且未发现4，5，6星且已无法刷新
