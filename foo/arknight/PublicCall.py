from os import getcwd, listdir
from sys import path
from time import perf_counter,sleep
from aircv import imread
from threading import Thread, Lock

path.append(getcwd())
from foo.pictureR import pictureFind

class PublicCall:
    def __init__(self, adb, cwd):
        self.tagDict = {'先锋干员':[[2,'夜刀'],[3,'芬'],[3,'翎羽'],[3,'香草'],[4,'红豆'],[4,'清道夫'],[5,'德克萨斯'],[5,'凛冬']],
        '近卫干员':[[10,'Castle-3'],[3,'玫兰莎'],[3,'泡普卡'],[3,'月见夜'],[4,'艾丝黛尔'],[4,'缠丸'],[4,'杜宾'],[4,'猎蜂'],[4,'慕斯'],[4,'霜叶'],[5,'诗怀雅'],[5,'因陀罗'],[5,'幽灵鲨']],
        '狙击干员':[[2,'巡林者'],[3,'安德切尔'],[3,'克洛丝'],[3,'空爆'],[4,'白雪'],[4,'杰西卡'],[4,'流星'],[5,'白金'],[5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'陨星']],
        '重装干员':[[2,'黑角'],[3,'斑点'],[3,'米格鲁'],[4,'古米'],[4,'角峰'],[4,'蛇屠箱'],[5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光']],
        '医疗干员':[[10,'Lancet-2'],[3,'安赛尔'],[3,'芙蓉'],[4,'调香师'],[4,'末药'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳']],
        '辅助干员':[[3,'梓兰'],[4,'地灵'],[5,'初雪'],[5,'梅尔'],[5,'真理']],
        '术师干员':[[2,'12F'],[2,'杜林'],[3,'史都华德'],[3,'炎熔'],[4,'格雷伊'],[4,'夜烟'],[4,'远山'],[5,'夜魔']],
        '特种干员':[[10,'THRM-EX'],[4,'阿消'],[4,'暗索'],[4,'砾'],[5,'红'],[5,'狮蝎'],[5,'食铁兽'],[5,'崖心']],
        '近战位':[[10,'Castle-3'],[10,'THRM-EX'],[2,'夜刀'],[2,'黑角'],[3,'芬'],[3,'翎羽'],[3,'香草'],[3,'玫兰莎'],[3,'泡普卡'],[3,'月见夜'],[3,'斑点'],
                [3,'米格鲁'],[4,'红豆'],[4,'清道夫'],[4,'艾丝黛尔'],[4,'缠丸'],[4,'杜宾'],[4,'猎蜂'],[4,'慕斯'],[4,'霜叶'],[4,'古米'],[4,'角峰'],[4,'蛇屠箱'],
                [4,'阿消'],[4,'暗索'],[4,'砾'],[5,'德克萨斯'],[5,'凛冬'],[5,'诗怀雅'],[5,'因陀罗'],[5,'幽灵鲨'],[5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光'],
                [5,'红'],[5,'狮蝎'],[5,'食铁兽'],[5,'崖心']],
        '远程位':[[10,'Lancet-2'],[2,'巡林者'],[2,'12F'],[2,'杜林'],[3,'安德切尔'],[3,'克洛丝'],[3,'空爆'],[3,'安赛尔'],[3,'芙蓉'],[3,'梓兰'],
                [3,'史都华德'],[3,'炎熔'],[4,'白雪'],[4,'杰西卡'],[4,'流星'],[4,'调香师'],[4,'末药'],[4,'地灵'],[4,'格雷伊'],[4,'夜烟'],[4,'远山'],[5,'白金'],
                [5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'陨星'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[5,'初雪'],[5,'梅尔'],[5,'真理'],[5,'夜魔']],
        '新手':[[2,'夜刀'],[2,'巡林者'],[2,'黑角'],[2,'12F'],[2,'杜林']],
        '资深干员':[[5,'德克萨斯'],[5,'凛冬'],[5,'诗怀雅'],[5,'因陀罗'],[5,'幽灵鲨'],[5,'白金'],[5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'陨星'],
                [5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[5,'初雪'],[5,'梅尔'],[5,'真理'],[5,'夜魔'],[5,'红'],[5,'狮蝎'],[5,'食铁兽'],[5,'崖心']],
        '高级资深干员':[[6,'推进之王'],[6,'陈'],[6,'斯卡蒂'],[6,'银灰'],[6,'能天使'],[6,'塞雷娅'],[6,'星熊'],[6,'闪灵'],[6,'夜莺'],[6,'伊芙利特']],
        '治疗':[[10,'Lancet-2'],[3,'斑点'],[3,'安赛尔'],[3,'芙蓉'],[4,'古米'],[4,'调香师'],[4,'末药'],[5,'临光'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[5,'夜魔']],
        '支援':[[10,'Castle-3'],[4,'杜宾'],[5,'凛冬'],[5,'诗怀雅'],[5,'白面鸮'],[5,'华法琳']],
        '输出':[[3,'翎羽'],[3,'玫兰莎'],[3,'月见夜'],[3,'安德切尔'],[3,'克洛丝'],[3,'史都华德'],[4,'红豆'],[4,'清道夫'],[4,'缠丸'],[4,'杜宾'],[4,'猎蜂'],
                [4,'慕斯'],[4,'霜叶'],[4,'杰西卡'],[4,'流星'],[4,'夜烟'],[5,'诗怀雅'],[5,'因陀罗'],[5,'白金'],[5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'火神'],
                [5,'雷蛇'],[5,'真理'],[5,'夜魔'],[5,'狮蝎'],[5,'崖心']],
        '群攻':[[3,'泡普卡'],[3,'空爆'],[3,'炎熔'],[4,'艾丝黛尔'],[4,'白雪'],[4,'格雷伊'],[4,'远山'],[5,'幽灵鲨'],[5,'陨星']],
        '减速':[[3,'梓兰'],[4,'霜叶'],[4,'白雪'],[4,'地灵'],[4,'格雷伊'],[5,'真理'],[5,'夜魔'],[5,'食铁兽']],
        '生存':[[3,'玫兰莎'],[3,'泡普卡'],[4,'艾丝黛尔'],[4,'缠丸'],[4,'杰西卡'],[5,'因陀罗'],[5,'幽灵鲨'],[5,'火神'],[5,'狮蝎']],
        '防护':[[3,'斑点'],[3,'米格鲁'],[4,'古米'],[4,'角峰'],[4,'蛇屠箱'],[4,'砾'],[5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光']],
        '削弱':[[4,'流星'],[4,'夜烟'],[5,'陨星'],[5,'初雪']],
        '位移':[[4,'阿消'],[4,'暗索'],[5,'可颂'],[5,'食铁兽'],[5,'崖心']],
        '控场':[[5,'德克萨斯'],[5,'梅尔'],[5,'红']],
        '爆发':[[10,'THRM-EX'],[5,'守林人']],
        '召唤':[[5,'梅尔']],
        '快速复活':[[4,'砾'],[5,'红']],
        '费用回复':[[3,'芬'],[3,'翎羽'],[3,'香草'],[4,'红豆'],[4,'清道夫'],[5,'德克萨斯'],[5,'凛冬']],
        '支援机械':[[10,'Castle-3'],[10,'Lancet-2'],[10,'THRM-EX']]}

        self.highTagDict = {'先锋干员':[[2,'夜刀'],[3,'芬'],[3,'翎羽'],[3,'香草'],[4,'红豆'],[4,'清道夫'],[5,'德克萨斯'],[5,'凛冬'],[6,'推进之王']],
        '近卫干员':[[10,'Castle-3'],[3,'玫兰莎'],[3,'泡普卡'],[3,'月见夜'],[4,'艾丝黛尔'],[4,'缠丸'],[4,'杜宾'],[4,'猎蜂'],[4,'慕斯'],[4,'霜叶'],[5,'诗怀雅'],[5,'因陀罗'],[5,'幽灵鲨'],
                [6,'陈'],[6,'斯卡蒂'],[6,'银灰']],
        '狙击干员':[[2,'巡林者'],[3,'安德切尔'],[3,'克洛丝'],[3,'空爆'],[4,'白雪'],[4,'杰西卡'],[4,'流星'],[5,'白金'],[5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'陨星'],[6,'能天使']],
        '重装干员':[[2,'黑角'],[3,'斑点'],[3,'米格鲁'],[4,'古米'],[4,'角峰'],[4,'蛇屠箱'],[5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光'],[6,'塞雷娅'],[6,'星熊']],
        '医疗干员':[[10,'Lancet-2'],[3,'安赛尔'],[3,'芙蓉'],[4,'调香师'],[4,'末药'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[6,'闪灵'],[6,'夜莺']],
        '辅助干员':[[3,'梓兰'],[4,'地灵'],[5,'初雪'],[5,'梅尔'],[5,'真理']],
        '术师干员':[[2,'12F'],[2,'杜林'],[3,'史都华德'],[3,'炎熔'],[4,'格雷伊'],[4,'夜烟'],[4,'远山'],[5,'夜魔'],[6,'伊芙利特']],
        '特种干员':[[10,'THRM-EX'],[4,'阿消'],[4,'暗索'],[4,'砾'],[5,'红'],[5,'狮蝎'],[5,'食铁兽'],[5,'崖心']],
        '近战位':[[10,'Castle-3'],[10,'THRM-EX'],[2,'夜刀'],[2,'黑角'],[3,'芬'],[3,'翎羽'],[3,'香草'],[3,'玫兰莎'],[3,'泡普卡'],[3,'月见夜'],[3,'斑点'],
                [3,'米格鲁'],[4,'红豆'],[4,'清道夫'],[4,'艾丝黛尔'],[4,'缠丸'],[4,'杜宾'],[4,'猎蜂'],[4,'慕斯'],[4,'霜叶'],[4,'古米'],[4,'角峰'],[4,'蛇屠箱'],
                [4,'阿消'],[4,'暗索'],[4,'砾'],[5,'德克萨斯'],[5,'凛冬'],[5,'诗怀雅'],[5,'因陀罗'],[5,'幽灵鲨'],[5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光'],
                [5,'红'],[5,'狮蝎'],[5,'食铁兽'],[5,'崖心'],[6,'推进之王'],[6,'陈'],[6,'斯卡蒂'],[6,'银灰'],[6,'塞雷娅'],[6,'星熊']],
        '远程位':[[10,'Lancet-2'],[2,'巡林者'],[2,'12F'],[2,'杜林'],[3,'安德切尔'],[3,'克洛丝'],[3,'空爆'],[3,'安赛尔'],[3,'芙蓉'],[3,'梓兰'],
                [3,'史都华德'],[3,'炎熔'],[4,'白雪'],[4,'杰西卡'],[4,'流星'],[4,'调香师'],[4,'末药'],[4,'地灵'],[4,'格雷伊'],[4,'夜烟'],[4,'远山'],[5,'白金'],
                [5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'陨星'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[5,'初雪'],[5,'梅尔'],[5,'真理'],[5,'夜魔'],[6,'能天使'],
                [6,'闪灵'],[6,'夜莺'],[6,'伊芙利特']],
        '新手':[[2,'夜刀'],[2,'巡林者'],[2,'黑角'],[2,'12F'],[2,'杜林']],
        '资深干员':[[5,'德克萨斯'],[5,'凛冬'],[5,'诗怀雅'],[5,'因陀罗'],[5,'幽灵鲨'],[5,'白金'],[5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'陨星'],
                [5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[5,'初雪'],[5,'梅尔'],[5,'真理'],[5,'夜魔'],[5,'红'],[5,'狮蝎'],[5,'食铁兽'],[5,'崖心']],
        '高级资深干员':[[6,'推进之王'],[6,'陈'],[6,'斯卡蒂'],[6,'银灰'],[6,'能天使'],[6,'塞雷娅'],[6,'星熊'],[6,'闪灵'],[6,'夜莺'],[6,'伊芙利特']],
        '治疗':[[10,'Lancet-2'],[3,'斑点'],[3,'安赛尔'],[3,'芙蓉'],[4,'古米'],[4,'调香师'],[4,'末药'],[5,'临光'],[5,'白面鸮'],[5,'赫默'],[5,'华法琳'],[5,'夜魔'],[6,'塞雷娅'],
                [6,'闪灵'],[6,'夜莺']],
        '支援':[[10,'Castle-3'],[4,'杜宾'],[5,'凛冬'],[5,'诗怀雅'],[5,'白面鸮'],[5,'华法琳'],[6,'银灰'],[6,'塞雷娅'],[6,'闪灵'],[6,'夜莺']],
        '输出':[[3,'翎羽'],[3,'玫兰莎'],[3,'月见夜'],[3,'安德切尔'],[3,'克洛丝'],[3,'史都华德'],[4,'红豆'],[4,'清道夫'],[4,'缠丸'],[4,'杜宾'],[4,'猎蜂'],
                [4,'慕斯'],[4,'霜叶'],[4,'杰西卡'],[4,'流星'],[4,'夜烟'],[5,'诗怀雅'],[5,'因陀罗'],[5,'白金'],[5,'蓝毒'],[5,'普罗旺斯'],[5,'守林人'],[5,'火神'],
                [5,'雷蛇'],[5,'真理'],[5,'夜魔'],[5,'狮蝎'],[5,'崖心'],[6,'推进之王'],[6,'陈'],[6,'斯卡蒂'],[6,'银灰'],[6,'能天使'],[6,'星熊']],
        '群攻':[[3,'泡普卡'],[3,'空爆'],[3,'炎熔'],[4,'艾丝黛尔'],[4,'白雪'],[4,'格雷伊'],[4,'远山'],[5,'幽灵鲨'],[5,'陨星'],[6,'伊芙利特']],
        '减速':[[3,'梓兰'],[4,'霜叶'],[4,'白雪'],[4,'地灵'],[4,'格雷伊'],[5,'真理'],[5,'夜魔'],[5,'食铁兽']],
        '生存':[[3,'玫兰莎'],[3,'泡普卡'],[4,'艾丝黛尔'],[4,'缠丸'],[4,'杰西卡'],[5,'因陀罗'],[5,'幽灵鲨'],[5,'火神'],[5,'狮蝎'],[6,'斯卡蒂']],
        '防护':[[3,'斑点'],[3,'米格鲁'],[4,'古米'],[4,'角峰'],[4,'蛇屠箱'],[4,'砾'],[5,'火神'],[5,'可颂'],[5,'雷蛇'],[5,'临光'],[6,'塞雷娅'],[6,'星熊']],
        '削弱':[[4,'流星'],[4,'夜烟'],[5,'陨星'],[5,'初雪'],[6,'伊芙利特']],
        '位移':[[4,'阿消'],[4,'暗索'],[5,'可颂'],[5,'食铁兽'],[5,'崖心']],
        '控场':[[5,'德克萨斯'],[5,'梅尔'],[5,'红']],
        '爆发':[[10,'THRM-EX'],[5,'守林人'],[6,'陈']],
        '召唤':[[5,'梅尔']],
        '快速复活':[[4,'砾'],[5,'红']],
        '费用回复':[[3,'芬'],[3,'翎羽'],[3,'香草'],[4,'红豆'],[4,'清道夫'],[5,'德克萨斯'],[5,'凛冬'],[6,'推进之王']],
        '支援机械':[[10,'Castle-3'],[10,'Lancet-2'],[10,'THRM-EX']]}

        self.adb = adb
        #self.srcBefore = None
        self.regAns = None
        #self.battle = battle
        self.cwd = cwd
        self.screenShot = self.cwd + '/bin/adb/PCScreenshot.png'
        self.tag = pictureFind.picRead([self.cwd + '/res/publicCall/' + i for i in listdir(self.cwd + '/res/publicCall')])
        self.mark = pictureFind.picRead(self.cwd + '/res/panel/other/publicMark.png')
        self.lock = Lock()
        self.tagOnScreenList = []
        #self.monitorFlag = False
    
    def getTag(self, src):
        #tempT = perf_counter()
        self.tagOnScreenList = []
        imSrc = src
        trytime = 0
        tInfo = pictureFind.matchImg(imSrc, self.mark, 0.8)
        if tInfo == None:
            return []
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

        #print('识别'+str(perf_counter() - tempT))
        #print(self.tagOnScreenList)
        tZS = None
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
                self.lock.acquire()
                #self.tagOnScreenList.append(self.trans(tInfo['obj']))
                self.tagOnScreenList.append((tInfo['obj'][:-4], tInfo['result']))
                self.lock.release()

    
    def getAns(self, tagOnScreenList):
        #tempT = perf_counter()
        if tagOnScreenList == []:
            #print('匹配'+str(perf_counter() - tempT))
            return False
        #tagOnScreenList.sort()
        if '高级资深干员' in tagOnScreenList:
            applyTagDict = self.highTagDict
        else:
            applyTagDict = self.tagDict
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
    src = imread('E:/workSpace/CodeRelease/arknightHelper/source/tag/test.png')
    print(test.getTag(src))
