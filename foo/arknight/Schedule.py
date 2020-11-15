from os import getcwd, listdir
from sys import path
from time import sleep
from threading import Thread
from json import loads,dumps
from cv2 import imread

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.pictureR import bootyCount
from foo.win import toast

class BattleSchedule:
    def __init__(self, adb, cwd, ico):
        self.cwd = cwd
        self.adb = adb
        self.ico = ico
        self.json = self.cwd + '/schedule.json'
        self.levelSchedule = self.readJson()
        self.switch = False
        self.switchB = False
        self.autoRecMed = False
        self.autoRecStone = False
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
        self.recMed = pictureFind.picRead(self.cwd + "/res/panel/recovery/medicament.png")
        self.recStone = pictureFind.picRead(self.cwd + "/res/panel/recovery/stone.png")
        self.confirm = pictureFind.picRead(self.cwd + "/res/panel/recovery/confirm.png")

        #self.exPos = {'ex1':(220,280),'ex2':(845,580),'ex3':(1230,340)}
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.act = self.cwd + "/res/panel/other/act.png"
        self.battle = self.cwd + "/res/panel/other/battle.png"
        self.home = self.cwd + "/res/panel/other/home.png"
        self.visitNext = self.cwd + "/res/panel/other/visitNext.png"
        self.listBattleImg = pictureFind.picRead([self.cwd + "/res/battle/" + i for i in listdir(self.cwd + "/res/battle")])
        self.startA = pictureFind.picRead(self.cwd + "/res/battle/startApart.png")
        self.autoOff = pictureFind.picRead(self.cwd + "/res/panel/other/autoOff.png")
        self.autoOn = pictureFind.picRead(self.cwd + "/res/panel/other/autoOn.png")
        self.II = {'MAIN':self.cwd + "/res/panel/level/I/main.png", 'EX':self.cwd + "/res/panel/level/I/exterminate.png",\
            'RS':self.cwd + "/res/panel/level/I/resource.png", 'PR':self.cwd + "/res/panel/level/I/chip.png"}
        self.III = {'A':self.cwd + "/res/panel/level/II/A.png", 'B':self.cwd + "/res/panel/level/II/B.png",\
                'C':self.cwd + "/res/panel/level/II/C.png", 'D':self.cwd + "/res/panel/level/II/D.png",\
                'AP':self.cwd + "/res/panel/level/II/AP.png", 'CA':self.cwd + "/res/panel/level/II/CA.png",\
                'CE':self.cwd + "/res/panel/level/II/CE.png", 'SK':self.cwd + "/res/panel/level/II/SK.png",\
                'LS':self.cwd + "/res/panel/level/II/LS.png", \
                'externalE1':self.cwd + "/res/panel/level/II/enternalE01.png",'externalE2':self.cwd + "/res/panel/level/II/enternalE02.png",\
                'tempE':self.cwd + "/res/panel/level/II/tempE.png",\
                '0':self.cwd + "/res/panel/level/II/ep0.png", '1':self.cwd + "/res/panel/level/II/ep1.png",\
                '2':self.cwd + "/res/panel/level/II/ep2.png", '3':self.cwd + "/res/panel/level/II/ep3.png",\
                '4':self.cwd + "/res/panel/level/II/ep4.png", '5':self.cwd + "/res/panel/level/II/ep5.png",\
                '6':self.cwd + "/res/panel/level/II/ep6.png", '7':self.cwd + "/res/panel/level/II/ep7.png",\
                '8':self.cwd + "/res/panel/level/II/ep8.png"}
        self.exIV = {'ex1':self.cwd + "/res/panel/level/III/e01.png",'ex2':self.cwd + "/res/panel/level/III/e02.png", 'ex3':self.cwd + "/res/panel/level/III/e03.png",\
                    'ex4':self.cwd + "/res/panel/level/III/e04.png"}
        self.exSymbol = self.cwd + "/res/panel/other/exSymbol.png"

    def goLevel(self, level):
        part = level['part']
        chap = level['chap']
        objLevel = level['objLevel']

        #前往一级菜单
        while self.switch:
            if self.adb.screenShot():
                picTh = pictureFind.matchImg(self.screenShot, self.II['MAIN'])
                if picTh != None:
                    break
            else:
                print('Fail to get screenshot')
                return False
            if self.adb.screenShot():
                picAct = pictureFind.matchImg(self.screenShot, self.act)
                if picAct != None:
                    posAct = picAct['result']
                    self.adb.click(posAct[0], posAct[1])
                else:
                    picHome = pictureFind.matchImg(self.screenShot, self.home)
                    if picHome != None:
                        posHome = picHome['result']
                        self.adb.click(posHome[0], posHome[1])
                        if self.adb.screenShot():
                            picBattle = pictureFind.matchImg(self.screenShot, self.battle)
                            if picBattle != None:
                                posBattle = picBattle['result']
                                self.adb.click(posBattle[0], posBattle[1])
                            else:
                                continue
                        else:
                            print('Fail to get screenshot')
                            return False
                    else:
                        print('unable to init')
                        return False
                
            else:
                print('Fail to get screenshot')
                return False

        #二级菜单的选择
        if self.adb.screenShot():
            picColumn = pictureFind.matchImg(self.screenShot, self.II[part])
            if picColumn != None:
                posColumn = picColumn['result']
                self.adb.click(posColumn[0], posColumn[1])
            else:
                print('Column Choice Wrong')
                return False
        else:
            print('Fail to get screenshot')
            return False

        sleep(1)
        #三级菜单的选择
        if part == 'EX':
            #剿灭
            for i in range(5):
                self.adb.screenShot()
                '''picLevelOn = pictureFind.matchImg(self.screenShot,self.startA) #2020.11.15 不知道为什么要判断有没有选中的关
                if picLevelOn != None:
                    return True'''
                picEx = pictureFind.matchImg(self.screenShot, self.exSymbol)
                if picEx != None:
                    break
            else:
                return False
            for i in range(5):
                self.adb.screenShot()
                picExChap = pictureFind.matchImg(self.screenShot, self.III[chap])
                if picExChap != None:
                    self.adb.click(picExChap['result'][0], picExChap['result'][1])
                    break
                else:
                    self.adb.onePageRight()
            else:
                return False
            for i in range(5):
                self.adb.screenShot()
                picLevelOn = pictureFind.matchImg(self.screenShot,self.startA)
                if picLevelOn != None:
                    return True
                picExObj = pictureFind.matchImg(self.screenShot, self.exIV[objLevel])
                if picExObj != None:
                    self.adb.click(picExObj['result'][0], picExObj['result'][1])
            else:
                return False
            
        else:
            #主线MIAN，物资RS，芯片PR
            self.adb.speedToLeft()
            if not self.chooseChap(chap):
                return False

        #关卡选择
            self.adb.speedToLeft()
            for i in range(25):
                if not self.switch:
                    break
                self.adb.screenShot()
                levelOnScreen = pictureFind.levelOcr(self.screenShot)
                if levelOnScreen != None:
                    if objLevel in levelOnScreen:
                        self.adb.click(levelOnScreen[objLevel][0],levelOnScreen[objLevel][1])
                        picLevelOn = pictureFind.matchImg(self.screenShot,self.startA)
                        if picLevelOn != None:
                            return True
                    else:
                        self.adb.onePageRight()
                else:
                    print(f'skip {objLevel}')
                    return False
            else:
                return False


    def chooseChap(self,chap):
        for i in range(20):
            if not self.switch:
                break
            self.adb.screenShot()
            picChap = pictureFind.matchImg(self.screenShot, self.III[chap])
            if not self.switch:
                break
            elif picChap == None:
                self.adb.onePageRight()
            else:
                self.adb.click(picChap['result'][0],picChap['result'][1])
                return True
        return False

    def runTimes(self, times = 1):
        bootyName = None
        if isinstance(times, dict):
            bootyMode = True
            bootyName = times['bootyName']
            times = int(times['bootyNum'])
        else:
            bootyMode = False
            times = int(times)

        #isFirstTurn = True
        countStep = 0
        totalCount = 0
        bootyTotalCount = 0
        twiceTry = 0
        while self.switch and self.switchB:
            
            self.adb.screenShot()
            #判断代理指挥是否勾选
            '''if isFirstTurn:
                isFirstTurn = False'''
            picStartA = pictureFind.matchImg(self.screenShot, self.startA, confidencevalue= 0.9)
            if picStartA != None and self.switch and self.switchB:
                print('> auto mode check <')
                picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                if picAutoOn == None and self.switch and self.switchB:
                    picAutoOff = pictureFind.matchImg(self.screenShot, self.autoOff)
                    if picAutoOff != None and self.switch and self.switchB:
                        posAutoOff = picAutoOff['result']
                        self.adb.click(posAutoOff[0], posAutoOff[1])

                isDelayExit = False #加载延迟是否出现，即检查到开始行动A但实际上是正在进入关卡前的状态
                for i in range(5):
                    if self.switch and self.switchB:
                        break
                    isSSSuccess = self.adb.screenShot()
                    if not isSSSuccess:
                        print('unable to get screenshot')
                        self.switchB = False
                        return False
                    for eachObj in self.listBattleImg:
                        if self.switch and self.switchB:
                            break
                        picInfo = pictureFind.matchImg(self.screenShot, eachObj, 0.8)
                        if picInfo != None:
                            if eachObj['obj'] != "startApart.png":
                                isDelayExit  = True
                                break

                    picAutoOn = pictureFind.matchImg(self.screenShot, self.autoOn)
                    if picAutoOn != None or isDelayExit:
                        if isDelayExit:
                            print("start delay exit")
                        break
                else:
                    print('auto mode still off')
                    self.switchB = False
                    return True #返回True用来跳过此关

            isInBattle = False
            #sleep(1)
            for eachObj in self.listBattleImg:
                if self.switch and self.switchB:
                    if eachObj['obj'] == "end.png":
                        confidence = 0.8
                    else:
                        confidence = 0.9
                    #print(self.screenShot + ' ' + self.cwd + '/res/battle/' + eachObj)
                    picInfo = pictureFind.matchImg(self.screenShot, eachObj, confidence)
                    #print(eachObj+ '：', picInfo)
                    if picInfo != None:
                        if eachObj['obj'] == "startBpart.png":
                            isInBattle = True
                        else:
                            isInBattle = False

                        picPos = picInfo['result']
                        if countStep == 0:
                            if eachObj['obj'] == 'startBpart.png':
                                countStep += 1
                        elif countStep == 1:
                            if eachObj['obj'] == 'endNormal.png':
                                countStep += 1
                                if bootyMode:
                                    for i in range(10):
                                        temp = imread(self.screenShot)
                                        self.adb.screenShot()
                                        if pictureFind.matchImg(temp, self.screenShot, confidencevalue=0.99) != None:
                                            break
                                        sleep(1)
                                    bootyTotalCount += self.BootyDetect.bootyCheck(bootyName, self.screenShot)
                                    print(f'{bootyName} 应获得：{times} 实获得：{bootyTotalCount}')
                                    
                        elif countStep == 2:
                            if eachObj['obj'] == 'startApart.png':
                                countStep += 1
                        if countStep == 3:
                            countStep =0
                            totalCount += 1
                        if (totalCount == times) and (not bootyMode):
                            self.switchB = False
                            return True
                        if (bootyTotalCount >= times) and bootyMode:
                            self.adb.click(picPos[0], picPos[1], isSleep = True)
                            self.switchB = False
                            return True
                        '''self.adb.click(picPos[0], picPos[1], isSleep = True)
                        if eachObj['obj'] == "cancel.png":
                            self.switch = False
                            self.switchB = False
                            toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                            return False
                        break'''
                        if eachObj['obj'] == "cancel.png":
                            if self.autoRecMed or self.autoRecStone:
                                medInfo = pictureFind.matchImg(self.screenShot, self.recMed)
                                stoneInfo = pictureFind.matchImg(self.screenShot, self.recStone)
                                confirmInfo = pictureFind.matchImg(self.screenShot, self.confirm)
                                if (not self.autoRecMed) and (self.autoRecStone):
                                    if medInfo != None and stoneInfo == None:
                                        self.adb.click(medInfo['result'][0]+350, medInfo['result'][1], isSleep= True)
                                        self.adb.screenShot()
                                        medInfo = pictureFind.matchImg(self.screenShot, self.recMed)
                                        stoneInfo = pictureFind.matchImg(self.screenShot, self.recStone)
                                        if medInfo == None and stoneInfo != None:
                                            if self.restStone >0:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                self.restStone -= 1
                                                break
                                    elif medInfo == None and stoneInfo != None:
                                        if self.restStone >0:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                self.restStone -= 1
                                                break
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    self.switch = False
                                    self.switchB = False
                                    toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                    return False
                                else:
                                    if self.autoRecMed:
                                        if medInfo != None:
                                            self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                            break
                                    if self.autoRecStone:
                                        if stoneInfo != None:
                                            if self.restStone >0:
                                                self.adb.click(confirmInfo['result'][0], confirmInfo['result'][1], isSleep= True)
                                                self.restStone -= 1
                                                break
                                    self.adb.click(picPos[0], picPos[1], isSleep = True)
                                    self.switch = False
                                    self.switchB = False
                                    toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                    return False
                            else:
                                self.adb.click(picPos[0], picPos[1], isSleep = True)
                                self.switch = False
                                self.switchB = False
                                toast.broadcastMsg("ArkHelper", "理智耗尽", self.ico)
                                return False
                        else:
                            self.adb.click(picPos[0], picPos[1], isSleep = True)
                        break
            if isInBattle:
                sleep(1)
                
    def readJson(self):
        with open(self.json,'r', encoding='UTF-8') as s:
            data = s.read()
        data = loads(data)
        return data

    def run(self, switchI):
        self.switch = switchI
        self.restStone = self.stoneMaxNum
        self.levelSchedule = self.readJson()
        levelList = self.levelSchedule['main'][0]['sel']
        for eachLevel in levelList:
            if not self.switch:
                break
            self.switchB = self.goLevel(eachLevel)
            if self.switchB and self.switch:
                levelCondition = self.runTimes(times=eachLevel['times'])
                if not levelCondition:
                    self.stop()
                    break

    def stop(self):
        self.switch = False
        self.switchB = False