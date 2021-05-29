from os import getcwd, listdir
from sys import path
from time import sleep

from foo.adb import adbCtrl
from foo.pictureR import pictureFind

class Room:
    def __init__(self, positionXY, adb, screenPosition = 'left'):
        self.positionXY = []
        if isinstance(positionXY, tuple):
            self.positionXY.extend(positionXY)
        else:
            self.positionXY = None

        if screenPosition == 'left':
            self.initSwipe = ((500,500), (800,500))
        else:
            self.initSwipe = ((800,500), (500,500))

        self.isRun = True
        self.cwd = getcwd().replace('\\', '/')
        self.adb = adb
        self.imgSrc = self.cwd + '/bin/adb/arktemp.png'
        self.ensure = self.cwd + '/res/construction/ensure.png'
        self.back = [self.cwd + '/res/construction/back.png', self.cwd + '/res/construction/stopBack.png']

    def stop(self):
        self.isRun = False
    
    '''
    def get(self):
        #不知道有什么用
        return self.positionXY

    def insert(self, newPosition):
        #暂时也没什么用
        self.positionXY.append(newPosition)
    '''

    def initialize(self):
        '恢复到当前房间所处的基建首页位置（左侧/右侧）'
        self.adb.swipe(self.initSwipe[0], self.initSwipe[1])
        sleep(1)

    def click(self, info):
        if isinstance(info, dict):
            self.adb.click(info['result'][0], info['result'][1])
        elif isinstance(info, tuple):
            self.adb.click(info[0], info[1])
        else:
            pass
    
    def backToConstruction(self):
        '回到基建首页'
        while True:
            print('正在返回基建首页')
            self.adb.screenShot()
            backInfoP = pictureFind.matchImg(self.cwd + '/bin/adb/arktemp.png', self.back[0], 0.9)
            stopBackInfoP = pictureFind.matchImg(self.cwd + '/bin/adb/arktemp.png', self.back[1], 0.9)
            if stopBackInfoP == None:
                self.click(backInfoP)
                sleep(0.5)
            else:
                break
        sleep(0.5)
        self.initialize()

    def change(self, waitPeoImg, talentList):
        '人员换班'
        self.adb.screenShot()
        picInfo = pictureFind.matchImg(self.imgSrc, waitPeoImg, 0.9)
        if picInfo != None:
            self.click(picInfo)
            sleep(1)
            self.adb.screenShot()
            for eachTalent in talentList:
                picInfo = pictureFind.matchForWork(self.cwd + '/bin/adb/arktemp.png', eachTalent, self.cwd + '/bin/adb')
                print(picInfo)
                if picInfo != None:
                    break
            self.click(picInfo)
            picInfo = pictureFind.matchImg(self.imgSrc, self.ensure, 0.9)
            print('确定', picInfo)  #!!
            self.click(picInfo)
            sleep(1)
    
    def start(self):
        '请在子类中重写'
        pass

    def run(self, enterEensureImg):
        self.isRun = True

        self.backToConstruction()

        for eachRoom in self.positionXY:
            if self.isRun == False:
                break

            count = 0
            while count < 20:
                self.click(eachRoom) #进入房间
                sleep(0.5)
                count += 1
                self.adb.screenShot()
                picInfo = pictureFind.matchImg(self.imgSrc, enterEensureImg, 0.9)
                if picInfo != None:
                    break
            else:
                self.isRun = False
                print('进入失败')

            while self.isRun:
                runningState = self.start()
                if runningState == False:
                    break

            self.backToConstruction()


class Trade(Room):
    def __init__(self, positionXY, adb, isRun=True, screenPosition='left'):
        super().__init__(positionXY, adb, screenPosition=screenPosition)
        self.dirWaitPeo = self.cwd + '/res/construction/waitPeo.png'
        self.talentTrade = [self.cwd + '/res/construction/talentTrade/' + each for each in \
            listdir(self.cwd + '/res/construction/talentTrade')]
        self.tradeImgObj = [self.cwd + '/res/construction/trade/' + each for each in \
            listdir(self.cwd + '/res/construction/trade')]

    def start(self):
        '贸易站内部操作执行一次'
        #贸易站操作过于简单
        #我不喜欢卖源石碎片

        self.adb.screenShot()
        picOrderInfo = pictureFind.matchImg(self.imgSrc, self.tradeImgObj[0], 0.9)
        picSupplyInfo = pictureFind.matchImg(self.imgSrc, self.tradeImgObj[1], 0.9)
        picWaitPeoInfo = pictureFind.matchImg(self.imgSrc, self.dirWaitPeo, 0.9)
        if picWaitPeoInfo != None:
                self.change(self.dirWaitPeo, self.talentTrade)
                return True
        else:
            if picOrderInfo != None or picSupplyInfo != None:
                self.click(picOrderInfo if picOrderInfo != None else picSupplyInfo)
                sleep(0.5)
                return True

            else:
                return False

    def run(self):
        super().run(self.tradeImgObj[0])


class Production(Room):
    def __init__(self, positionXY, adb, screenPosition='left'):
        super().__init__(positionXY, adb, screenPosition=screenPosition)
        self.dirWaitPeo = self.cwd + '/res/construction/waitPeo.png'
        self.talentProduction = [self.cwd + '/res/construction/talentProduction/' + each for each in \
            listdir(self.cwd + '/res/construction/talentProduction')]
        self.productionImgObj = [self.cwd + '/res/construction/production/' + each for each in \
            listdir(self.cwd + '/res/construction/production')]

    def start(self):
        self.adb.screenShot()
        picExpInfo = pictureFind.matchImg(self.imgSrc, self.productionImgObj[4], 0.9) #判断这个制造站是否在生产作战记录
        if picExpInfo == None:
            tempTalent = self.talentProduction[0:len(self.talentProduction)] #未生产作战记录不选择作战记录技能干员，并有限选择赤金技能干员
        else:
            #制造站在生产作战记录的话，则不选择赤金技能干员，优先选择作战记录技能干员
            tempTalent = self.talentProduction[1:]
            tempTalent[0], tempTalent[len(tempTalent) - 1] = tempTalent[len(tempTalent) - 1], tempTalent[0]



        self.adb.screenShot()
        picProductCtrlInfo = pictureFind.matchImg(self.imgSrc, self.productionImgObj[2], 0.9)
        if picProductCtrlInfo != None:
            self.click(picProductCtrlInfo) #进入制造站二级界面
        else:
            picWaitPeoInfo = pictureFind.matchImg(self.imgSrc, self.dirWaitPeo, 0.9) #换班判断
            if picWaitPeoInfo != None:    
                self.change(self.dirWaitPeo, tempTalent)
                return True

            #补充任务至99
            picMaxInfo = pictureFind.matchImg(self.imgSrc, self.productionImgObj[1], 0.9)
            picConfirmInfo = pictureFind.matchImg(self.imgSrc, self.productionImgObj[0], 0.9)
            pic99Info = pictureFind.matchImg(self.imgSrc, self.productionImgObj[3], 0.9)
            if pic99Info == None and picConfirmInfo == None:
                self.click(picMaxInfo)
                return True
            elif pic99Info != None and picConfirmInfo != None:
                self.click(picConfirmInfo)
                return True
            else:
                return False

    def run(self):
        super().run(self.productionImgObj[2])



class Dormitory(Room):
    def __init__(self, positionXY, adb, screenPosition='left'):
        super().__init__(positionXY, adb, screenPosition=screenPosition)
        self.dormObj = [self.cwd + '/res/construction/dorm/' + each for each \
            in listdir(self.cwd + '/res/construction/dorm')]
        self.getInXY = None
        self.alreadyIsClear =  False
        self.noMoreTiredP = False

    def restart(self):
        '用于重置状态'
        self.alreadyIsClear = True

    def getGetInXY(self):
        #为中枢提供进驻按钮坐标，但是那边已经用了默认值了，所以暂时用不上
        return (self.getInXY['result'],) if self.getInXY != None else None

    def start(self):
        self.adb.screenShot()
        picLiveMsgClosedInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[2], 0.8)
        picLiveMsgOpenInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[3], 0.9)
        if picLiveMsgOpenInfo != None:
            pass
        elif picLiveMsgClosedInfo != None:
            self.click(picLiveMsgClosedInfo)
            sleep(0.5)
            return True
        
        count = 0
        while count < 5: #清空宿舍
            if not self.alreadyIsClear:
                self.adb.screenShot()
                picClearInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[1], 0.9)
                self.click(picClearInfo)
                count += 1

                self.adb.screenShot()
                pic0PeoInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[0], 0.8)
                if pic0PeoInfo != None:
                    self.alreadyIsClear = True
                    break
            else:
                break
        else:
            return False
        
        if self.getInXY == None:
            picGetInInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[4], 0.9)
            if picGetInInfo != None:
                self.getInXY = picGetInInfo

        picFullInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[7], 0.9)
        if picFullInfo == None:
            self.click(self.getInXY) #打开干员界面
            sleep(1)
            self.adb.screenShot()
            picDistractedInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[5], 0.8)
            if picDistractedInfo == None:
                self.noMoreTiredP = True #已经没有还需要休息的干员了，避免进入下个宿舍，节约时间
                return False
            else:
                self.click(picDistractedInfo)

            picEnsureInfo = pictureFind.matchImg(self.imgSrc, self.ensure, 0.9)
            self.click(picEnsureInfo) #确认
            sleep(0.5)
            return True
        else:
            return False

    def run(self):
        #self.isFinish = False
        self.isRun = True

        self.backToConstruction()

        if self.positionXY == None:
            self.isRun = False
        else:
            for eachRoom in self.positionXY:
                if self.isRun == False:
                    break
                if self.noMoreTiredP:
                    break

                count = 0
                while count < 5:
                    self.click(eachRoom)
                    sleep(0.5)
                    self.adb.screenShot()
                    picInfo = pictureFind.matchImg(self.imgSrc, self.dormObj[6], 0.9)
                    if picInfo != None:
                        break
                else:
                    self.isRun = False

                self.alreadyIsClear = False #每个宿舍的清空状态需要重置

                while self.isRun:
                    runningState = self.start()
                    if runningState == False:
                        break

                self.backToConstruction()
            self.backToConstruction()
            self.restart()


class Center(Room):
    def __init__(self, positionXY, adb, getInPosition = (1200, 200), screenPosition='left'):
        super().__init__(positionXY, adb, screenPosition=screenPosition)
        self.getInXY = getInPosition
        self.centerObj = [self.cwd + '/res/construction/center/' + each for each \
            in listdir(self.cwd + '/res/construction/center')]
        self.centerTalent = [self.cwd + '/res/construction/talentCenter/' + each for each \
            in listdir(self.cwd + '/res/construction/talentCenter')]
        self.noneTalent = [self.cwd + '/res/construction/talentNone/' + each for each \
            in listdir(self.cwd + '/res/construction/talentNone')]

    def start(self):
        self.adb.screenShot() #判断是否打开了进驻信息面板
        picLiveMsgClosedInfo = pictureFind.matchImg(self.imgSrc, self.centerObj[2], 0.8) #关闭状态
        picLiveMsgOpenInfo = pictureFind.matchImg(self.imgSrc, self.centerObj[3], 0.9) #打开状态
        if picLiveMsgOpenInfo != None:
            pass
        elif picLiveMsgClosedInfo != None:
            self.click(picLiveMsgClosedInfo)
            sleep(0.5)
            return True

        self.adb.screenShot()
        picFullCenterInfo = pictureFind.matchImg(self.imgSrc, self.centerObj[1], 0.9) #判断中枢是否已经满员
        if picFullCenterInfo != None:
            return False
        else:
            self.click(self.getInXY) #进入选择干员界面，这里用了默认值（1440*810下）做坐标，也可以将宿舍界面得到的进驻按钮坐标输入
            sleep(0.5)
            self.adb.screenShot()
            for eachTalent in self.centerTalent: #选择有中枢相关能力的干员
                picTalentInfo = pictureFind.matchForWork(self.imgSrc, eachTalent, self.cwd + '/bin/adb')
                if picTalentInfo != None:
                    self.click(picTalentInfo)
                    break
            else:
                for eachPeople in self.noneTalent: #没有相关干员的时候随便用一些人来凑数 为防止部分干员能力浪费应当跳过这部分
                    picTalentInfo = pictureFind.matchImg(self.imgSrc, eachPeople, 0.9)
                    if picTalentInfo != None:
                        self.click(picTalentInfo)
                        break
            
            picEnsureInfo = pictureFind.matchImg(self.imgSrc,self.ensure, 0.9) #确定干员选中
            if picEnsureInfo != None:
                self.click(picEnsureInfo)
                return True
            else:
                return False
            

    def run(self):
        super().run(self.centerObj[0])



class Reception(Room):
    def __init__(self, positionXY, adb, screenPosition='right'):
        super().__init__(positionXY, adb, screenPosition=screenPosition)
        self.clueNo = 0
        self.checkClueFinish = False
        self.collectClueFinish = False
        self.dailyClueFinish = False
        self.clueXYList = list()
        self.isClueSendAllow = True

        self.talentClue = [self.cwd + '/res/construction/talentClue/' + each for each in \
            listdir(self.cwd + '/res/construction/talentClue')]
        self.receptionObj = [self.cwd + '/res/construction/reception/' + each for each in \
            listdir(self.cwd + '/res/construction/reception')]
        self.clueObj = [self.cwd + '/res/construction/clue/' + each for each in \
            listdir(self.cwd + '/res/construction/clue')]
        self.clueCheckObj = [self.cwd + '/res/construction/clueCheck/' + each for each in \
            listdir(self.cwd + '/res/construction/clueCheck')]

    def sendClue(self):
        '线索赠送'
        self.adb.screenShot()
        picSendInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[9], 0.9)
        self.click(picSendInfo)
        sleep(1)   
        for tryCount in range(5):
            #共5次，尝试进入线索赠送界面
            self.adb.screenShot()
            picSendInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[9], 0.9)
            picCheckInfo = pictureFind.matchImg(self.imgSrc, self.clueCheckObj[0], 0.9)
            if picSendInfo == None and picCheckInfo != None:
                #如果已经进入就不再尝试
                self.isInSendClueOneTime = True
                break
            elif picSendInfo != None and picCheckInfo == None:
                #还未进入，尝试进入
                self.click(picSendInfo)
                sleep(0.5)
            else:
                #既不在二级界面也不在线索赠送界面，可能在加载，再来一次
                sleep(0.5)

        for clueNum in range(1,8):
            #获取线索1-7按钮的位置
            picClueXY = pictureFind.matchImg(self.imgSrc, self.clueCheckObj[clueNum], 0.9)
            self.clueXYList.append(picClueXY['result'])

        for eachClueColumnNo in range(7):
            if not self.isRun:
                break
            self.click(self.clueXYList[eachClueColumnNo])
            sleep(0.5)
            self.adb.screenShot()
            clueXYList = pictureFind.matchMultiImg(self.imgSrc, self.clueObj[7+eachClueColumnNo], self.cwd + '/bin/adb')
            if clueXYList != None:
                while len(clueXYList) >= 2 and self.isRun:
                    picSendButtonInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[7], 0.9)
                    self.click(clueXYList[0])
                    sleep(0.5)
                    self.click(picSendButtonInfo)
                    sleep(0.5)
                    self.adb.screenShot()
                    clueXYList = pictureFind.matchMultiImg(self.imgSrc, self.clueObj[7+eachClueColumnNo], self.cwd + '/bin/adb')

        while self.isRun:
            #尝试退出
            picExitInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[11], 0.9)
            self.click(picExitInfo)
            self.adb.screenShot()
            #会客室二级菜单有三种状态，你可知道有哪三种（划掉）
            #一个一个判断，第一个出现的概率应该远大于第二第三个，所以先判断，企图省下一些微不足道的时间
            picClueCtrlInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[2], 0.9)
            if picClueCtrlInfo != None:
                break
            else:
                picClueCtrlInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[10], 0.9)
                if picClueCtrlInfo != None:
                    break
                else:
                    picClueCtrlInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[13], 0.9)
                    if picCheckInfo != None:
                        break
        
        self.checkClueFinish = True
        return True


    def collectClue(self):
        '收取线索'
        picNewClueNeedCollectInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[4], 0.9)
        if picNewClueNeedCollectInfo != None:
            self.click(picNewClueNeedCollectInfo)
            sleep(1)
            self.adb.screenShot()
            picGetAllInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[5], 0.9)
            self.click(picGetAllInfo)

        self.collectClueFinish = True
        return True


    def getDailyClue(self):
        '收取每日刷新的一个线索'
        picDailyClueInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[3], 0.9)
        if picDailyClueInfo != None:
            self.click(picDailyClueInfo)
            sleep(0.5)
            self.adb.screenShot()
            picGetDailyInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[6], 0.9)
            picExitInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[12], 0.9)
            self.click(picGetDailyInfo)
            self.adb.screenShot()
            self.click(picExitInfo)


        self.dailyClueFinish = True

    def unlockClue(self):
        '解锁线索'
        picUnlockInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[8], 0.9)
        self.click(picUnlockInfo)


    def start(self):
        self.adb.screenShot()
        picEnterInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[0], 0.9)
        if picEnterInfo != None:
            self.click(picEnterInfo) #进入会客室二级界面
            return True
        else:
            #下面三行都是判断是否已经处于会客室二级界面（线索界面）
            picClueCtrlInfo1 = pictureFind.matchImg(self.imgSrc, self.receptionObj[2], 0.9)
            picClueCtrlInfo2 = pictureFind.matchImg(self.imgSrc, self.receptionObj[10], 0.9)
            picClueCtrlInfo3 = pictureFind.matchImg(self.imgSrc, self.receptionObj[13], 0.9)
            if picClueCtrlInfo1 == None and picClueCtrlInfo2 == None and picClueCtrlInfo3 == None:
                print('出错') #没能成功进入会客室二级界面，跳过会客室部分
                return False
            else:
                picWaitPeoInfo = pictureFind.matchImg(self.imgSrc, self.receptionObj[1], 0.9) #判断是否缺人
                if picWaitPeoInfo != None:
                    print('正在换人') #写了gui之后可能会变为修改一个变量，通过类的方法获取当前执行状态展示在gui界面上
                    self.change(self.receptionObj[1], self.talentClue)
                    return True

                if not self.dailyClueFinish: 
                    self.getDailyClue()
                    return True

                self.adb.screenShot()
                if (not self.checkClueFinish) and self.isClueSendAllow: 
                    self.sendClue()
                    return True

                self.adb.screenShot()
                if not self.collectClueFinish:
                    self.collectClue()
                    return True

                self.adb.screenShot()

                #下面是查找有无线索缺失，缺失的线索有无装载
                picClueLackInfo = pictureFind.matchImg(self.imgSrc, self.clueObj[self.clueNo], 0.85)
                print(self.clueNo)
                if self.clueNo >6: #如果7个线索都查看过一次了，就尝试解锁线索
                    self.unlockClue()
                    return False

                #实际运行的时候下面这部分效率有些低，但是因为我不过专业所以完全想不到为什么
                elif picClueLackInfo != None:
                    print(picClueLackInfo)
                    self.click(picClueLackInfo)
                    sleep(0.5)
                    self.adb.screenShot()
                    picNoClueInfo = pictureFind.matchImg(self.imgSrc, self.clueObj[7 + self.clueNo], 0.85)
                    print(picNoClueInfo)

                    self.clueNo += 1
                    self.click(picNoClueInfo)
                    sleep(0.5)
                    return True

                else:
                    self.clueNo += 1
                    return True
                

    def run(self):
        super().run(self.receptionObj[0])
        self.restart()

    def restart(self):
        '重置'
        self.clueNo = 0
        self.dailyClueFinish = False
        self.collectClueFinish = False
        self.checkClueFinish = False
        self.ClueXYList = list()

    def switchSendClue(self):
        #赠送线索的开关，写成这样应该方便gui调用一些
        #但是我又想我好像把会客室的实例写到一个大类里了，这个东西显得就不是很有必要
        self.isClueSendAllow = False if self.isClueSendAllow else True

class Office(Room):
    def __init__(self, positionXY, adb, screenPosition='right'):
        super().__init__(positionXY, adb, screenPosition=screenPosition)
        self.officeObj = [self.cwd + '/res/construction/office/' + each for each in \
            listdir(self.cwd + '/res/construction/office')]
        self.talentOffice = [self.cwd + '/res/construction/talentOffice/' + each for each in \
            listdir(self.cwd + '/res/construction/talentOffice')]

    def start(self):
        print('办公室')
        self.change(self.officeObj[0], self.talentOffice)

        self.adb.screenShot()
        picLackPeoInfo = pictureFind.matchImg(self.imgSrc, self.officeObj[0], 0.9)
        if picLackPeoInfo == None:
            return False
        else:
            print('本次更换人员失败') 
            #这里好像可能会进入一个死循环，但这个基本不会出错，我相信它。反正再不济stop方法都能让它停下来 --2019.11.23.21：11
            return True

    def run(self):
        super().run(self.officeObj[1])


class ConstructionPanel:
    def __init__(self):
        self._cwd = getcwd().replace('\\','/')
        self._src = self._cwd + '/bin/adb/arktemp.png'
        self._listObj = []
        self._isRun = False
        self._step = ''
        self._caution = self._cwd + '/res/construction/caution.png'
        self._trust = self._cwd + '/res/construction/trust/trust.png'
        
        
    def preInitialize(self, direction = 0):
        if direction == 0:
            self._adb.swipe((500,500), (800,500))
            sleep(1)
        else:
            self._adb.swipe((800,500), (500,500))
            sleep(1)


    def initialize(self):
        self._adb = adbCtrl.adb(self._cwd + '/bin/adb', self._cwd + '/config.ini')
        self._adb.connect()

        
        #获得左半平面的房间的坐标
        self.preInitialize()
        sleep(0.5)
        self._adb.screenShot()
        self._dormXY = pictureFind.matchMultiImg(self._src, self._cwd + '/res/construction/vacantRomm.png', self._cwd + '/bin/adb')
        self._productXY = pictureFind.matchMultiImg(self._src, self._cwd + '/res/construction/productStation.png', self._cwd + '/bin/adb')
        self._tradeXY = pictureFind.matchMultiImg(self._src, self._cwd + '/res/construction/tradeStation.png', self._cwd + '/bin/adb')
        self._centerXY = pictureFind.matchMultiImg(self._src, self._cwd + '/res/construction/center.png', self._cwd + '/bin/adb')

        #获得右半平面的房间的坐标
        self.preInitialize(1)
        sleep(0.5)
        self._adb.screenShot()
        self._receptionXY = pictureFind.matchMultiImg(self._src, self._cwd + '/res/construction/receptionRoom.png', self._cwd + '/bin/adb')
        self._officeXY = pictureFind.matchMultiImg(self._src, self._cwd + '/res/construction/officeRoom.png', self._cwd + '/bin/adb')

        self._listObj = self.create()

    def create(self):
        self._dorm = Dormitory(self._dormXY, self._adb)
        self._trade = Trade(self._tradeXY, self._adb)
        self._product = Production(self._productXY, self._adb)
        self._center = Center(self._centerXY, self._adb)
        self._reception = Reception(self._receptionXY, self._adb)
        self._office = Office(self._officeXY, self._adb)
        
        return [self._dorm, self._trade, self._product, self._reception, self._office, self._center, self._reception] #会客室可能要来三回

    def click(self, info):
        if isinstance(info, dict):
            self._adb.click(info['result'][0], info['result'][1])
        else:
            pass

    def run(self):
        self._isRun = True
        step = 0
        for eachObj in self._listObj:
            eachObj.run()
            if not self._isRun:
                break
            print(step)
            step += 1
        #self._reception.run()
        #上面这行是我用来测试会客室的时候用的 作为最复杂的一个房间 很有纪念意义就不删了

        self.getTrust() #在最后进行信赖触摸 方法内部已经判断了是否终止，所以这里就不用了
        self._isRun = False

    def stop(self):
        self._isRun = False
        for eachObj in self._listObj:
            eachObj.stop()

    def getTrust(self):
        while self._isRun:
            self._adb.screenShot()
            picCautionInfo = pictureFind.matchImg(self._src, self._caution, 0.9)
            if picCautionInfo == None:
                break

            self.click(picCautionInfo)
            sleep(0.5)
            self._adb.screenShot()
            picTrustInfo = pictureFind.matchImg(self._src, self._trust, 0.9)
            if picTrustInfo != None:
                self.click(picTrustInfo)
                self._isRun = False
                break
    









if __name__ == "__main__":
    
    #下面都是测试用部分

    con = ConstructionPanel()
    con.initialize()
    def test():
        con.run()
        #con._reception.run()

    def stop():
        con.stop()

    from _thread import start_new_thread
    start_new_thread(test,())
    print('!')
    input()
    stop()
    input()