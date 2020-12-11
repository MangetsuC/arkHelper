from os import getcwd, listdir
from sys import path
from time import perf_counter,sleep
from threading import Thread, Lock
from json import loads
from cv2 import fillConvexPoly, imshow, waitKey
from numpy import array

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
        self.mark = pictureFind.picRead(self.cwd + '/res/panel/other/publicMark.png')
        self.lock = Lock()
        self.tagOnScreenList = []
        #self.monitorFlag = False
    
    def updateTag(self):
        self.isTagNeedUpdate = True
    
    def getTag(self, src):
        #tempT = perf_counter()
        self.tagOnScreenList = []
        imSrc = src
        trytime = 0
        #tInfo = pictureFind.matchImg(imSrc, self.mark, 0.8)
        #if tInfo == None:
        #    return []
        '''
        th0 = Thread(target=self.matchTag, args=(imSrc, self.tag[0:4]))
        th1 = Thread(target=self.matchTag, args=(imSrc, self.tag[4:8]))
        th2 = Thread(target=self.matchTag, args=(imSrc, self.tag[8:12]))
        th3 = Thread(target=self.matchTag, args=(imSrc, self.tag[12:16]))
        th4 = Thread(target=self.matchTag, args=(imSrc, self.tag[16:20]))
        th5 = Thread(target=self.matchTag, args=(imSrc, self.tag[20:24]))
        th6 = Thread(target=self.matchTag, args=(imSrc, self.tag[24:28]))
        thList = [th0, th1, th2, th3, th4, th5, th6]
        for eachth in thList:
            eachth.start()
        for eachth in thList:
            eachth.join()
        '''
        self.matchTag(imSrc, self.tag)

        #print('识别'+str(perf_counter() - tempT))
        #print(self.tagOnScreenList)
        '''
        tZS = None #意为tags资深 下面同理
        tZY = None
        tGZ = None
        tJX = None
        if not(self.tagOnScreenList == [] or len(self.tagOnScreenList) == 5):
            for each in range(len(self.tagOnScreenList)):
                if '资深干员' == self.tagOnScreenList[each][0]:
                    tZS = self.tagOnScreenList[each]
                if '高级资深干员' == self.tagOnScreenList[each][0]:
                    tGZ = self.tagOnScreenList[each]
                if '支援' == self.tagOnScreenList[each][0]:
                    tZY = self.tagOnScreenList[each]
                if '支援机械' == self.tagOnScreenList[each][0]:
                    tJX = self.tagOnScreenList[each]
            if tZS != None and tGZ != None:
                if abs(tZS[1][0] - tGZ[1][0]) < 50 and abs(tZS[1][1] - tGZ[1][1]) < 5:
                    self.tagOnScreenList.remove(tZS)
            if tZY != None and tJX != None:
                if abs(tZY[1][0] - tJX[1][0]) < 50 and abs(tZY[1][1] - tJX[1][1]) < 5:
                    self.tagOnScreenList.remove(tZY)
        '''
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
        if self.isTagNeedUpdate:
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


if __name__ == "__main__":
    test = PublicCall(None, r'E:\workSpace\CodeRelease\arknightHelper\arkHelper')
    src = pictureFind.imreadCH('E:/workSpace/CodeRelease/arknightHelper/source/tag/test2.png')
    print(test.getTag(src))
