from os import getcwd, listdir, remove
from _thread import start_new_thread, exit_thread
from time import sleep

from foo.adb import adbCtrl
from foo.pictureR import pictureFind


def battle():
    print('start')
    while isRun:
        adb.screenShot()
        for eachPic in listBattleImgObj:
            if eachPic == 'end.png': #降低置信系数，避免有些特别花的干员背景干扰判断
                minConfidence = 0.8
            else:
                minConfidence = 0.9
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', cwd + '/res/battle/' + eachPic, minConfidence)
            print( eachPic+ '：', picInfo)
            if picInfo != None:
                adb.click(picInfo['result'][0], picInfo['result'][1])
                if eachPic == 'cancel.png':
                    print('程序已结束！')
                    exit_thread()
                break
        sleep(1)
    print('程序已结束！')

def construction():
    switchRest = True
    while isUnattended:
        adb.screenShot()
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listPeoplepanel[0], 0.9)
        if picInfo != None and switchRest:
            click(picInfo)
            adb.screenShot()
            getOff()

        if switchRest:
            adb.screenShot()
            autoRest()
            switchRest = False
        
        adb.screenShot()
        sleep(0.5)
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listPanelImgObj[0], 0.9)
        print(listPanelImgObj[0], '：', picInfo)
        if picInfo != None:  #贸易站判断
            adb.click(picInfo['result'][0], picInfo['result'][1])
            sleep(0.5)
            trade()
        else:
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listPanelImgObj[1], 0.9)  #制造站判断
            entranceCtrl = 'production'
            print(listPanelImgObj[1], '：', picInfo)
            if picInfo == None:  #信赖判断
                picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[3], 0.9)
                entranceCtrl = 'trust'
                print(listBackImgObj[3], '：', picInfo)
                if picInfo == None:
                    entranceCtrl = 'finish'

            if entranceCtrl == 'production':
                emergencyInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[2], 0.9)
                cautionInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[3], 0.9)
                if emergencyInfo != None or cautionInfo != None:  #制造站入口
                    adb.click(picInfo['result'][0], picInfo['result'][1])
                    sleep(1)
                    adb.click(picInfo['result'][0], picInfo['result'][1])
                    sleep(0.5)
                    production()
            elif entranceCtrl == 'trust':  #信赖入口
                adb.click(picInfo['result'][0], picInfo['result'][1])
                sleep(1)
                adb.screenShot()
                picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listTrustImgObj[0], 0.9)
                print(listTrustImgObj[0], '：', picInfo)
                if picInfo != None:
                    click(picInfo)
                    sleep(0.5)
            elif entranceCtrl == 'finish':
                print('\r程序结束！')
                break



def trade():
    switchT =True
    while switchT:
        if not isUnattended:
            break

        adb.screenShot()
        sleep(0.5)
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listPeoplepanel[1], 0.9)
        if picInfo != None:
            click(picInfo)
            sleep(1)
            adb.screenShot()
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listTradeImgObj[2], 0.9)
            click(picInfo)
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/ensure.png', 0.9)
            print('确定', picInfo)
            click(picInfo)
            sleep(1)

        adb.screenShot()
        picOrderInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listTradeImgObj[0], 0.9)
        picSupplyInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listTradeImgObj[1], 0.9)
        if picOrderInfo != None or picSupplyInfo != None:
            click(picOrderInfo if picOrderInfo != None else picSupplyInfo)
            sleep(0.5)
        else:
            switchT = False
            break

    while 1:
        if not isUnattended:
            break

        adb.screenShot()
        backInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[0], 0.9)
        stopBackInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[1], 0.9)
        if stopBackInfoP == None:
            click(backInfoP)
            sleep(0.5)
        else:
            break

def production():
    countP = True
    while countP:
        if not isUnattended:
            break

        adb.screenShot()
        sleep(0.5)
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listPeoplepanel[1], 0.9)
        if picInfo != None:
            click(picInfo)
            sleep(1)
            adb.screenShot()
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listProductionImgObj[4], 0.9)
            click(picInfo)
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/ensure.png', 0.9)
            print('确定', picInfo)
            click(picInfo)
            sleep(1)

        adb.screenShot()
        for each in range(4):
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listProductionImgObj[each], 0.9)
            print(listProductionImgObj[each], '：', picInfo)
            if picInfo != None:
                if '99' in listProductionImgObj[each]:
                    picConfInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listProductionImgObj[0], 0.9)
                    print('exit：', picConfInfo)
                    if picConfInfo == None:
                        countP =False
                        break
                else:
                    click(picInfo)
                    sleep(0.5)
                    adb.screenShot()


    while 1:
        if not isUnattended:
            break

        adb.screenShot()
        backInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[0], 0.9)
        stopBackInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[1], 0.9)
        if stopBackInfoP == None:
            click(backInfoP)
            sleep(0.5)
        else:
            break

def getOff():
    '撤下疲劳的干员，用于进驻总览页面'
    adb.screenShot()
    sleep(0.5)
    totalTry = 0
    totalPeoNeedRest = 0

    while 1:
        sleep(0.5)
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/getOffWorkButton.png', 0.9)
        print('撤下',picInfo)
        click(picInfo)
        adb.screenShot()
        sleep(0.5)
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/getOffWorkButtonOn.png', 0.9)
        totalTry += 1
        if totalTry >= 10:
            print('出现错误')
            exit_thread()
        elif picInfo != None:
            break


    while 1:
        while 1:
            if isStop:
                exit_thread()
            adb.screenShot()
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/distractedE.png', 0.8)
            if picInfo != None:
                adb.click(picInfo['result'][0], picInfo['result'][1])
                totalPeoNeedRest += 1
                print(picInfo)
                print('!!!')
                sleep(0.5)
            else:
                break

        print('下面将滑动')
        adb.swipeD()
        sleep(1)
        adb.screenShot('swipeAfter')
        compare = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', cwd + '/bin/adb/swipeAfter.png', 0.98) #判断是否到达底端
        print(compare)
        if  compare != None:
            print('全部撤下')
            break

    while 1:
        if isStop:
            exit_thread()
        adb.screenShot()
        backInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[0], 0.9)
        stopBackInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[1], 0.9)
        if stopBackInfoP == None:
            click(backInfoP)
            sleep(0.5)
        else:
            break
    return totalPeoNeedRest

def autoRest():
    continuePutIn = True
    while continuePutIn:
        if isStop:
            exit_thread()
        adb.screenShot()
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/vacantRomm.png', 0.8)
        if picInfo != None:
            adb.click(picInfo['result'][0], picInfo['result'][1])
        else:
            break
        sleep(1)
        while 1:
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/liveMsg.png', 0.8)
            click(picInfo)
            adb.screenShot()
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/liveMsgOpen.png', 0.8)
            if picInfo != None:
                break
        sleep(1)
        adb.screenShot()
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/clear.png', 0.9)
        click(picInfo)
        sleep(1)
        adb.screenShot()
        picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/getIn.png', 0.8)
        enterButtonP = picInfo['result']
        putInNum = 0
        while putInNum < 5:
            adb.click(enterButtonP[0], enterButtonP[1])
            sleep(1)
            adb.screenShot()
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/distracted.png', 0.8)
            print('疲惫', picInfo)
            if picInfo == None:
                continuePutIn = False
                break
            click(picInfo)
            sleep(1)
            adb.screenShot()
            picInfo = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', 'E:/Code/arkHelper/res_bak/test/dorm/ensure.png', 0.9)
            print('确定', picInfo)
            click(picInfo)
            putInNum += 1
            sleep(1.5)
    
    while 1:
        if isStop:
            exit_thread()
        adb.screenShot()
        backInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[0], 0.9)
        stopBackInfoP = pictureFind.matchImg(cwd + '/bin/adb/arktemp.png', listBackImgObj[1], 0.9)
        if stopBackInfoP == None:
            click(backInfoP)
            sleep(0.5)
        else:
            break

def click(info):
    if info != None:
        adb.click(info['result'][0], info['result'][1])

def connect():
    adb.connect()

#这部分可能应该用pickle存一下
cwd = getcwd().replace('\\', '/')
listBattleImgObj = listdir(cwd + '/res/battle')
listProductionImgObj = [cwd + '/res/construction/production/' + each for each in listdir(cwd + '/res/construction/production')]
listTradeImgObj = [cwd + '/res/construction/trade/' + each for each in listdir(cwd + '/res/construction/trade')]
listTrustImgObj = [cwd + '/res/construction/trust/' + each for each in listdir(cwd + '/res/construction/trust')]
listPanelImgObj = [cwd + '/res/construction/panel/' + each for each in listdir(cwd + '/res/construction/panel')]
listBackImgObj = [cwd + '/res/construction/back.png', cwd + '/res/construction/stopBack.png', cwd + '/res/construction/emergency.png',\
    cwd + '/res/construction/caution.png']
listPeoplepanel = [cwd + '/res/construction/allpeople.png', cwd + '/res/construction/waitPeo.png']

adb = adbCtrl.adb(cwd + '/bin/adb')
isRun = True
isUnattended = True
isStop = False
mode = input('输入1进入战斗模式，输入2进入基建模式')
connect()
if mode == '1':
    start_new_thread(battle, ())
elif mode == '2':
    start_new_thread(construction, ())
else:
    print('输错了，重新开程序')
input()
isRun = False
isUnattended =False
isStop = True
print('正在终止程序')
sleep(1)
test = input('按下回车退出')
