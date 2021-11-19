from os import getcwd, listdir
from sys import path
from time import sleep, time
from PyQt5.QtCore import center, pyqtSignal, QObject
from foo.ocr.ocr import getText, findTextPos


from foo.pictureR import pictureFind
from foo.win import toast
from common2 import adb

class BattleLoop(QObject):
    noBootySignal = pyqtSignal()
    errorSignal = pyqtSignal(str)
    def __init__(self, cwd, ico):
        super(BattleLoop, self).__init__()
        self.cwd = cwd
        self.ico = ico
        self.switch = False
        self.connectSwitch = False
        self.autoRecMed = False
        self.autoRecStone = False
        self.stoneMaxNum = 0

        self.isWaitingUser = False
        self.isUselessContinue = False
        self.isRecovered = False

        self.battleLoopTimes = -100

        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.listBattleImg = pictureFind.picRead([self.cwd + "/res/battle/" + i for i in listdir(self.cwd + "/res/battle")])
        self.listActImg = pictureFind.picRead([self.cwd + "/res/actBattle/" + i for i in listdir(self.cwd + "/res/actBattle")])
        
        self.listImg = self.listBattleImg#self.listActImg + self.listBattleImg

        self.startA = pictureFind.picRead(self.cwd + "/res/battle/startApart.png")
        self.startB = pictureFind.picRead(self.cwd + "/res/battle/startBpart.png")
        self.autoOff = pictureFind.picRead(self.cwd + "/res/panel/other/autoOff.png")
        self.autoOn = pictureFind.picRead(self.cwd + "/res/panel/other/autoOn.png")

        self.recMed = pictureFind.picRead(self.cwd + "/res/panel/recovery/medicament.png")
        self.recStone = pictureFind.picRead(self.cwd + "/res/panel/recovery/stone.png")
        self.confirm = pictureFind.picRead(self.cwd + "/res/panel/recovery/confirm.png")

        self.uselessLevel = pictureFind.picRead(self.cwd + "/res/panel/other/uselessLevel.png")
    
    def setLoopTimes(self, times):
        if times < 0:
            times = -100
        self.battleLoopTimes = times

    def getLoopTimes(self):
        return self.battleLoopTimes

    def recChange(self, num, inputData):
        if num == 0:
            self.autoRecMed = inputData
        elif num == 1:
            self.autoRecStone = inputData
        elif num == 2:
            self.stoneMaxNum = inputData
    
    def connect(self, broadcast = True):
        self.connectSwitch = True
        for times in range(10):
            print(f'正在连接adb...第{times+1}次')
            if self.connectSwitch:
                if adb.connect():
                    return True
                else:
                    print(f'第{times+1}次连接尝试失败')
            else:
                print('收到用户指令，中断')
                return False
        
        else:
            if broadcast:
                toast.broadcastMsg("ArkHelper", "连接模拟器失败，请检查设置和模拟器", self.ico)
                print('连接adb失败')
            else:
                print("INIT:adb connect failed")
            return False


    def run(self, switchI):
        self.switch = switchI
        isAutoMode = 0 #是否代理指挥标志位
        stepFinishOneLevel = 0
        restStoneNum = self.stoneMaxNum
        restLoopTime = self.battleLoopTimes
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





    def stop(self):
        self.connectSwitch = False
        self.switch = False