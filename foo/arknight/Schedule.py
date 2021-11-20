from json import loads
from os import getcwd, listdir
from sys import path
from time import sleep, time

from common import schedule_data
from common2 import adb
from foo.ocr.ocr import findTextPos, getText, findTextPos_all
from foo.pictureR import bootyCount, pictureFind
from foo.pictureR.squreDetect import find_squares
from foo.pictureR.spoils import spoilsCheck
from foo.win import toast
from PyQt5.QtCore import QObject, pyqtSignal


class BattleSchedule(QObject):
    errorSignal = pyqtSignal(str)
    def __init__(self, cwd, ico):
        super(BattleSchedule, self).__init__()
        self.cwd = cwd
        self.ico = ico
        self.switch = False
        self.switchB = False
        self.autoRecMed = False
        self.autoRecStone = False

        self.isWaitingUser = False
        self.isRecovered = False

        self.stoneMaxNum = 0
        self.BootyDetect = bootyCount.Booty(self.cwd)
        self.imgInit()

    def recChange(self, num, inputData):
        if num == 0:
            self.autoRecMed = inputData
        elif num == 1:
            self.autoRecStone = inputData
        elif num == 2:
            self.stoneMaxNum = inputData

    def imgInit(self):
        self.resTrans = {'A':'固若金汤', 'B':'摧枯拉朽',\
                        'C':'势不可挡', 'D':'身先士卒',\
                        'AP':'粉碎防御', 'CA':'空中威胁',\
                        'CE':'货物运送', 'SK':'资源保障',\
                        'LS':'战术演习'}

    def enter(self):
        '进入终端界面'
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['采购中心'], [])
            if ans != None:
                ans = findTextPos(ocrResult, ['理智'], [])
                for i in range(5):
                    adb.click(ans[0][0], ans[0][1])
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['终端'], [])
                    if temp != None:
                        return 

            adb.clickHome()
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['终端'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
            
            for i in range(5):
                temp = findTextPos(getText(adb.getScreen_std(True)), ['终端'], [])
                if temp != None:
                    return 

    def enter2(self, part):
        '进入主线、资源或剿灭的二级界面'
        class Enter2Error(Exception):
            def __init__(self, info) -> None:
                self.info = info
            def __str__(self) -> str:
                return self.info

        img = adb.getScreen_std()
        if part == 'MAIN':
            ans = pictureFind.matchImg(img, './res/panel/level/mainIcon.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                for i in range(5):
                    adb.click(ans['result'][0], ans['result'][1])
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['主题曲'], [])
                    if temp != None:
                        break 
            else:
                raise Enter2Error('无法找到主题曲Icon')
        elif part == 'EX':
            ans = pictureFind.matchImg(img, './res/panel/level/exIcon.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                for i in range(5):
                    adb.click(ans['result'][0], ans['result'][1])
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['每周部署'], [])
                    if temp != None:
                        break 
            else:
                raise Enter2Error('无法找到每周部署Icon')
        elif part == 'RS' or part == 'PR':
            ans = pictureFind.matchImg(img, './res/panel/level/resIcon.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                for i in range(5):
                    adb.click(ans['result'][0], ans['result'][1])
                    temp = findTextPos(getText(adb.getScreen_std(True)), ['资源收集'], [])
                    if temp != None:
                        break 
            else:
                raise Enter2Error('无法找到资源收集Icon')
        else:
            raise Enter2Error('part信息错误')

    def enter4(self, objLevel):
        '前往关卡'
        class Enter4Error(Exception):
            def __init__(self, info) -> None:
                self.info = info
            def __str__(self) -> str:
                return self.info

        if objLevel[0] == 'e':
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            if objLevel == 'e01':
                ans = findTextPos(ocrResult, ['切尔诺伯格'], [])
            elif objLevel == 'e02':
                ans = findTextPos(ocrResult, ['龙门外环'], [])
            elif objLevel == 'e03':
                ans = findTextPos(ocrResult, ['龙门市区'], [])
            else:
                ans = findTextPos(ocrResult, ['委托'], ['期'])
            
            if ans != None:
                adb.click(ans[0][0], ans[0][1])
                return 
            else:
                raise Enter4Error('未发现剿灭关卡')

        else:
            adb.speedToLeft()
            for i in range(25):
                if not self.switch:
                    break

                img = adb.getScreen_std(True)
                ocrResult = getText(img)
                ans = []
                temp = findTextPos_all(ocrResult, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], [])
                for i in temp:
                    if '-' in i[2]:
                        ans.append(i)
                
                if ans == []:
                    raise Enter4Error('未发现任何关卡')

                levelOnScreen = dict()
                for i in ans:
                    levelOnScreen[i[2]] = i[0]

                if objLevel in levelOnScreen.keys():
                    adb.click(levelOnScreen[objLevel][0],levelOnScreen[objLevel][1])
                    img = adb.getScreen_std(True)
                    ocrResult = getText(img)
                    ans = findTextPos(ocrResult, ['开始行动'], [])
                    if ans != None:
                        return True
                else:
                    adb.onePageRight()
            else:
                raise Enter4Error('未发现指定关卡，可能是关卡输入错误')


    def goLevel(self, level):
        part = level['part']
        chap = level['chap']
        objLevel = level['objLevel']

        #前往终端界面/一级菜单
        self.enter()

        #二级菜单的选择
        self.enter2(part)

        sleep(1)
        #三级菜单的选择
        #主线MIAN，物资RS，芯片PR
        if not self.chooseChap(chap):
            return False

        #关卡选择
        self.enter4(objLevel)
        return True

    def backToOneLayer(self, layerMark):
        '回到某一层'
        startTime = time()
        while pictureFind.matchImg(adb.getScreen_std(), layerMark, confidencevalue = 0.7) is None:
            if not self.switch:
                break
            adb.click(100, 50)
            if time() - startTime > 30:
                return -1
        return 0

    def chooseChap(self,chap):
        '进入到关卡页面'
        if chap == 'external' or chap == 'tempE':
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            ans = findTextPos(ocrResult, ['当期委托'], [])
            if ans != None:
                adb.click(ans[0][0], ans[0][1])

            for i in range(5):
                temp = findTextPos(getText(adb.getScreen_std(True)), ['开始行动'], [])
                if temp != None:
                    break 
            adb.clickBack()
            for i in range(5):
                temp = findTextPos(getText(adb.getScreen_std(True)), ['开始行动'], [])
                if temp == None:
                    break 
            adb.clickDownRight()
            for i in range(5):
                temp = findTextPos(getText(adb.getScreen_std(True)), ['当期委托'], [])
                if temp != None:
                    return True  #确认来到剿灭选单界面


        elif chap.isdigit():
            #主线
            nowChap = -1
            if int(chap) <= 3:
                ans = findTextPos(getText(adb.getScreen_std(True)), ['幻灭', 'SHATTEROFAVISION'], [])
                if ans != None:
                    adb.click(ans[0][0], ans[0][1]) 
                ans = findTextPos(getText(adb.getScreen_std(True)), ['觉醒'], [])
                if ans != None:
                    adb.click(ans[0][0], ans[0][1]) 
            elif int(chap) <= 8:
                ans = findTextPos(getText(adb.getScreen_std(True)), ['幻灭', 'SHATTEROFAVISION'], [])
                if ans != None:
                    adb.click(ans[0][0], ans[0][1]) 
            elif int(chap) > 8:
                ans = findTextPos(getText(adb.getScreen_std(True)), ['幻灭', 'SHATTEROFAVISION'], [])
                if ans != None:
                    adb.click(ans[0][0], ans[0][1]) 
                ans = findTextPos(getText(adb.getScreen_std(True)), ['残阳'], [])
                if ans != None:
                    adb.click(ans[0][0], ans[0][1]) 
            
            ans = find_squares(adb.getScreen_std())
            if ans != []:
                adb.click(ans[0][0][0], ans[0][0][1])

            while True:
                img = adb.getScreen_std(True)
                ocrResult = getText(img)

                center = findTextPos(ocrResult, ['当前进度'], [])
                if center == None:
                    continue

                ans = []
                temp = findTextPos_all(ocrResult, ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], [])
                for i in temp:
                    if i[2].isdigit():
                        ans.append(i)
                ans.sort(key = lambda x:int(x[2]))

                thisLevel = None
                xDistance = adb.screenX
                for i in range(len(ans)):
                    if abs(ans[i][0][0] - center[0][0]) < xDistance:
                        xDistance = abs(ans[i][0][0] - center[0][0])
                        thisLevel = i
                
                if int(chap) == int(ans[thisLevel][2]):
                    return True
                elif int(chap) > int(ans[thisLevel][2]):
                    adb.click(ans[thisLevel + 1][0][0], ans[thisLevel + 1][0][1])
                else:
                    adb.click(ans[thisLevel - 1][0][0], ans[thisLevel - 1][0][1])

            
        else:
            #各类资源
            adb.swipe(1050, 400, 1440, 400, 200) #左滑，避免关卡全开的情况
            for i in range(20):
                if not self.switch:
                    break
                img = adb.getScreen_std(True)
                ocrResult = getText(img)

                ans = findTextPos(ocrResult, [self.resTrans[chap]], [])
                if not self.switch:
                    break
                elif ans == None:
                    adb.onePageRight()
                else:
                    adb.click(ans[0][0],ans[0][1])
                    return True
        return False

    def runTimes(self, times = 1):
        spoilName = 'NULL'
        if isinstance(times, dict):
            spoilName = times['bootyName']
            restSpoilNum = int(times['bootyNum'])
            restLoopTime = -100
        else:
            restSpoilNum = -100
            restLoopTime = int(times)

        isAutoMode = 0 #是否代理指挥标志位
        stepFinishOneLevel = 0
        restStoneNum = self.stoneMaxNum
        while self.switch:
            img = adb.getScreen_std(True)
            ocrResult = getText(img)

            if isAutoMode < 3:
                ans = findTextPos(ocrResult, ['配置不可更改'], [])
                if ans != None:
                    #检测到处于代理状态
                    isAutoMode = 3
                    continue

            if isAutoMode == 1:
                ans = findTextPos(ocrResult, ['代理指挥'], [])
                if ans != None:
                    #点击代理指挥
                    adb.click(ans[0][0], ans[0][1])
                    isAutoMode = 2
                    continue

            ans = findTextPos(ocrResult, ['开始行动'], [])
            if ans != None:
                #检测到第一个开始行动
                if stepFinishOneLevel == 1:
                    stepFinishOneLevel = 2
                
                if stepFinishOneLevel == 2:
                    restLoopTime -= 1
                    stepFinishOneLevel = 0

                if (restLoopTime <= 0 and (not restLoopTime <= -100)):
                    break

                adb.click(ans[0][0], ans[0][1])
                continue

            ans = findTextPos(ocrResult, ['开始'], ['行动'])
            if ans != None:
                #检测到第二个开始行动
                if isAutoMode == 3:
                    adb.click(ans[0][0], ans[0][1])
                else:
                    #不处于代理指挥状态
                    isAutoMode = 1
                    #应当点击返回
                    adb.clickBack()
                continue

            ans = findTextPos(ocrResult, ['攻入敌方数', '理智恢复'], [])
            if ans != None:
                #检测到升级或剿灭
                adb.click(ans[0][0], ans[0][1])
                continue
            
            ans = findTextPos(ocrResult, ['行动结束'], [])
            if ans != None:
                #检测到正常关卡结束
                if restSpoilNum != -100:
                    #掉落物模式
                    #等待掉落物显示完
                    for i in range(5):
                        if findTextPos(getText(adb.getScreen_std(True)), ['额外物资'], []) != None:
                            break
                    else:
                        for i in range(5):
                            if findTextPos(getText(adb.getScreen_std(True)), ['常规掉落'], []) != None:
                                break
                    spoils = spoilsCheck()
                    if spoils != dict():
                        print(f'本次行动共获得:{spoils}')

                    if spoilName in spoils.keys():
                        restSpoilNum -= int(spoils[spoilName])
                        print(f'距离{spoilName}的目标个数还有:{restSpoilNum}个')

                    if restSpoilNum <= 0:
                        restLoopTime = 0 #使其跳出

                adb.click(ans[0][0], ans[0][1])
                if stepFinishOneLevel == 0:
                    stepFinishOneLevel = 1
                continue

            ans = findTextPos(ocrResult, ['是否花费'], [])
            if ans != None:
                #检测到使用源石或理智药剂
                #获取确认按钮的位置
                confirmPos = pictureFind.matchImg(adb.getScreen_std(), './res/panel/recovery/confirm.png', confidencevalue=0.3, targetSize=(0,0))
                if confirmPos == None:
                    continue
                confirmPos = confirmPos['result']
                cancelPos = [ans[1][0][0], confirmPos[1]]
                if (not self.autoRecMed) and (not self.autoRecStone):
                    adb.click(cancelPos[0], cancelPos[1]) #取消按钮的位置
                    break
                if self.autoRecMed:
                    #使用药剂
                    if '源石' in ans[3]:
                        #已经没有药剂剩余
                        pass
                    else:
                        #使用药剂
                        adb.click(confirmPos[0], confirmPos[1])
                        continue
                if self.autoRecStone:
                    #使用源石
                    if restStoneNum > 0:
                        #在允许范围内
                        ans = findTextPos(ocrResult, ['使用至纯源石恢复'], [])
                        adb.click(ans[0][0], ans[0][1])
                        adb.click(confirmPos[0], confirmPos[1])
                        continue
                    else:
                        adb.click(cancelPos[0], cancelPos[1])
                else:
                    adb.click(cancelPos[0], cancelPos[1])
                break

            ans = findTextPos(ocrResult, ['源石不足'], [])
            if ans != None:
                #检测到源石也没有了
                adb.click(ans[0][0], ans[0][1])
                break
                
    def readJson(self):
        with open(self.json,'r', encoding='UTF-8') as s:
            data = s.read()
        data = loads(data)
        return data

    def run(self, switchI):
        self.switch = switchI
        self.restStone = self.stoneMaxNum
        '''print('正在获取用户配置的计划')
        self.levelSchedule = self.readJson()
        print('用户配置读取成功')
        levelList = self.levelSchedule['main'][0]['sel']'''
        levelList = schedule_data.get('main')[0]['sel']
        for eachLevel in levelList:
            if not self.switch:
                break
            if eachLevel['part'] == 'THIS':
                self.switchB = True
            else:
                targetLevel = eachLevel['objLevel']
                if targetLevel[0] == 'S':
                    targetLevel = 'L' + targetLevel
                print(f'正在前往指定关卡{targetLevel}')
                self.switchB = self.goLevel(eachLevel)
            if self.switchB and self.switch:
                levelCondition = self.runTimes(times=eachLevel['times'])
                if not levelCondition:
                    self.stop()
                    break

    def stop(self):
        self.switch = False
        self.switchB = False
