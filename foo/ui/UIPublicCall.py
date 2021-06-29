from sys import path
from threading import Thread, Lock
from time import sleep, perf_counter
from foo.arknight.PublicCall import PublicCall
from foo.pictureR import pictureFind

from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QLabel, QWidget, QScrollArea
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

class UIPublicCall(QDialog):
    def __init__(self, adb, battle, cwd, listGoTo, normal, high, theme = None, parent=None, flags=Qt.WindowFlags(1)):
        super().__init__(parent=parent, flags=flags)
        self.initVar(adb, battle, cwd, normal, high)
        self.initAuto(listGoTo)
        self.initUI(theme)
        self.theme = theme
        #self.myTimer()
        
    def updateTag(self):
        self.publicCall.updateTag()
    
    def initVar(self, adb, battle, cwd, normal, high):
        self.cwd = cwd
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.battle = battle
        #self.btnCheck = btnCheck
        self.adb = adb
        
        self.publicCall = PublicCall(adb, self.cwd, normal, high)

        self.isThTagExit = False
        self.isTimerExit = False
        
        self.tags = []
        self.text = '正在连接'
        self.beforeText = []
        self.allTempLabel = []
        self.isShowAll = False
        self.monitorFlag = False
        self.totalFlag = True
        self.lock  = Lock()
        self.isExit = False

        self.autoSwitch = False #自动公招
    
    def initAuto(self, listGoTo):
        self.pcFinish = pictureFind.picRead(self.cwd + '/res/panel/publicCall/finish.png')
        self.pcInMark = pictureFind.picRead(self.cwd + '/res/panel/publicCall/inPcMark.png')
        self.pc9 = pictureFind.picRead(self.cwd + '/res/panel/publicCall/pc9.png')
        self.pcCancel = pictureFind.picRead(self.cwd + '/res/panel/publicCall/pcCancel.png')
        self.pcConfirm = pictureFind.picRead(self.cwd + '/res/panel/publicCall/pcConfirm.png')
        self.pcMark = pictureFind.picRead(self.cwd + '/res/panel/publicCall/pcMark.png')
        self.pcNew = pictureFind.picRead(self.cwd + '/res/panel/publicCall/pcNew.png')
        self.pcAddTime = pictureFind.picRead(self.cwd + '/res/panel/publicCall/addTime.png')
        self.pcDecreaseTime = pictureFind.picRead(self.cwd + '/res/panel/publicCall/decreaseTime.png')
        self.pcEnter = pictureFind.picRead(self.cwd + '/res/panel/publicCall/enter.png')

        self.listGoTo = listGoTo
        self.mainpage = self.listGoTo[0]
        self.home = self.listGoTo[1]
        self.mainpageMark = self.listGoTo[2]

        self.employFlag = True
        self.searchFlag = True
        self.advCredOnly = True
    
    def initUI(self, theme):
        self.setWindowTitle('公开招募计算器')
        self.setWindowIcon(QIcon(self.cwd + '/res/ico.ico'))
        self.grid = QGridLayout()

        self.combFiller = QWidget()
        self.combGrid = QGridLayout()
        self.combGrid.setAlignment(Qt.AlignTop)
        self.combFiller.setLayout(self.combGrid)
        self.combFiller.setMinimumSize(400, 2000)#######设置滚动条的尺寸
        self.scroll = QScrollArea()
        if theme != None:
            self.scroll.viewport().setStyleSheet(f"background-color:{theme.getFgColor()};")
        self.scroll.setWidget(self.combFiller)
        
        self.lbText = QLabel('现有标签', self)
        self.lbText.setAlignment(Qt.AlignCenter)
        self.tag0 = QLabel('', self)
        self.tag1 = QLabel('', self)
        self.tag2 = QLabel('', self)
        self.tag3 = QLabel('', self)
        self.tag4 = QLabel('', self)
        self.tagsLabelList = [self.tag0, self.tag1, self.tag2, self.tag3, self.tag4]
        for eachLabel in self.tagsLabelList:
            if theme != None:
                eachLabel.setStyleSheet(f'''QLabel {{border-style: solid;
                                border-left-width: 5px;border-right-width: 5px;border-top-width: 2px;border-bottom-width: 2px;
                                border-color: {theme.getFgColor()};border-radius: 0px;background-color: {theme.getFgColor()};}}''')
            eachLabel.setFixedHeight(35)
            eachLabel.setAlignment(Qt.AlignCenter)

        self.btnShowAll = QPushButton('显示全部干员', self)
        self.btnShowAll.setCheckable(True)
        self.btnShowAll.clicked[bool].connect(self.showAllChange)
        self.btnShowAll.setFixedHeight(40)
        
        self.grid.addWidget(self.lbText, 0, 0, 2, 1)


        self.grid.addWidget(self.tag0, 0, 1, 1, 1)
        self.grid.addWidget(self.tag1, 0, 2, 1, 1)
        self.grid.addWidget(self.tag2, 0, 3, 1, 1)
        self.grid.addWidget(self.tag3, 1, 1, 1, 1)
        self.grid.addWidget(self.tag4, 1, 2, 1, 1)


        self.grid.addWidget(self.scroll, 3, 0, 1, 4)
        self.grid.addWidget(self.btnShowAll, 2, 0, 1, 4)
        
        self.setLayout(self.grid)
        self.resize(445,800)
        #self.setFixedWidth(430)
        if theme != None:
            self.setStyleSheet(f'''UIPublicCall{{background-color:{theme.getBgColor()};}}
            QPushButton{{border:0px;background:{theme.getFgColor()};color:{theme.getFontColor()};
                        font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                        QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                        QPushButton:pressed{{background:{theme.getPressedColor()};font:9pt;}}
                        QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()};}}
            QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
            QScrollArea{{background-color:{theme.getFgColor()};}}
            QScrollBar:vertical{{width:8px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:2px;padding-bottom:2px;}}
            QScrollBar:handle:vertical{{width:8px;background:rgba(0,0,0,25%);border-radius:0px;min-height:20;}}
            QScrollBar:handle:vertical:hover{{width:8px;background:rgba(0,0,0,50%);border-radius:0px;min-height:20;}}
            QScrollBar:add-line:vertical{{height:0px;width:0px;subcontrol-position:bottom;}}
            QScrollBar:sub-line:vertical{{height:0px;width:0px;subcontrol-position:top;}}
            QScrollBar:add-page:vertical,QScrollBar:sub-page:vertical{{background:rgba(0,0,0,10%);border-radius:0px;}}
            QScrollBar:horizontal{{height:8px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}}
            QScrollBar:handle:horizontal{{width:8px;background:rgba(0,0,0,25%);border-radius:0px;min-height:20;}}
            QScrollBar:handle:horizontal:hover{{width:8px;background:rgba(0,0,0,50%);border-radius:0px;min-height:20;}}
            QScrollBar:add-line:horizontal{{height:0px;width:0px;subcontrol-position:bottom;}}
            QScrollBar:sub-line:horizontal{{height:0px;width:0px;subcontrol-position:top;}}
            QScrollBar:add-page:horizontal,QScrollBar:sub-page:horizontal{{background:rgba(0,0,0,10%);border-radius:0px;}}''')

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
    
    def setStar(self, star, func, state = True):
        return self.publicCall.setStar(star, func, state)
    
    def showAllChange(self, ischecked):
        self.isShowAll = ischecked
    
    def getTextBrowser(self):
        #tempT = perf_counter()
        self.monitorFlag = self.battle.connect()
        while self.monitorFlag and self.totalFlag:
            ans = self.publicCall.run()
            if not ans:
                self.tags = [] #改为列表
                keyValueList = []
            else:
                tags = ans[1]
                ans = ans[0]
                self.tags = tags #改为列表
                keyValueList = ans.items()
                keyValueList = list(keyValueList)
                keyValueList.sort(key = lambda x:len(x[0]), reverse = True)
            if not (self.monitorFlag and self.totalFlag):
                break
            self.lock.acquire()
            self.text = keyValueList
            #print(self.text)
            self.lock.release()
            #print('总'+str(perf_counter() - tempT))

    def updateBrowser(self):
        if self.tags == []:
            for each in self.tagsLabelList:
                each.setText('')
            for each in self.allTempLabel:
                if isinstance(each, QLabel):
                    each.deleteLater()
            self.allTempLabel = []
            self.allTempLabel.append(QLabel('未发现公开招募标签或正在刷新'))
            self.combGrid.addWidget(self.allTempLabel[0], 3, 0)
            #self.tagsBrowser.setText('')
        else:
            for i in range(5):
                self.tagsLabelList[i].setText(self.tags[i])
        
        if self.text != self.beforeText:
            self.beforeText = self.text
            for each in self.allTempLabel:
                if isinstance(each, QLabel):
                    each.deleteLater()
            self.allTempLabel = []

            if not isinstance(self.text, str):
                for eachCombination in self.text:
                    eachCombination[1].sort(key = lambda x:x[0])
                    if eachCombination[1][0][0] < 4 and not self.isShowAll:
                        continue
                    tempTagsComb = eachCombination[0].split('+')
                    for eachTag in tempTagsComb:
                        tempTagLabel = QLabel(eachTag)
                        tempTagLabel.setStyleSheet(f'''QLabel {{border-style: solid;
                                            border-left-width: 5px;border-right-width: 5px;border-top-width: 2px;border-bottom-width: 2px;
                                            border-color: {self.theme.getThemeColor()};border-radius: 8px;
                                            background-color: {self.theme.getThemeColor()};color:{self.theme.getCheckedFontColor()}}}''')
                        tempTagLabel.setFixedHeight(35)
                        tempTagLabel.setAlignment(Qt.AlignCenter)
                        self.allTempLabel.append(tempTagLabel)
                    self.allTempLabel.append('END')
                    for eachPeo in eachCombination[1]:
                        tempPeoLabel = QLabel(eachPeo[1])
                        tempPeoLabel.setFixedHeight(35)
                        tempPeoLabel.setAlignment(Qt.AlignCenter)
                        tempPeoLabel.setStyleSheet('''QLabel {border-style: solid;border-left-width: 5px;border-right-width: 5px;border-top-width: 2px;border-bottom-width: 2px;
                                            border-color: #D8B3D8;border-radius: 0px;background-color: #D8B3D8;}''')
                        if eachPeo[0] == 5:
                            tempPeoLabel.setStyleSheet('''QLabel {border-color: #FFC90E;background-color: #FFC90E;}''')
                        elif eachPeo[0] == 6:
                            tempPeoLabel.setStyleSheet('''QLabel {border-color: #FF7F27;background-color: #FF7F27;}''')
                        elif eachPeo[0] == 10:
                            tempPeoLabel.setStyleSheet('''QLabel {border-color: #808080;background-color: #808080;}''')
                        elif eachPeo[0] == 3:
                            tempPeoLabel.setStyleSheet('''QLabel {border-color: #09B3F7;background-color: #09B3F7;}''')
                        elif eachPeo[0] == 2:
                            tempPeoLabel.setStyleSheet('''QLabel {border-color: #D3DB2E;background-color: #D3DB2E;}''')
                        self.allTempLabel.append(tempPeoLabel)
                    self.allTempLabel.append('END')
                count = 0
                nowLine = 0
                for eachLabel in self.allTempLabel:
                    if eachLabel == 'END' or count == 4:
                        count = 0
                        nowLine += 1
                    else:
                        self.combGrid.addWidget(eachLabel, nowLine, count, 1, 1)
                        eachLabel.show()
                        count += 1


    def myTimer(self):
        self.isTimerExit = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBrowser)
        self.timer.start(10)
        
    def updateUI(self):
        self.isThTagExit = True
        self.thSetText = Thread(target=self.getTextBrowser)
        self.thSetText.setDaemon(True)
        self.thSetText.start()


    def turnOn(self):
        if not self.isVisible():
            self.myTimer()
            self.totalFlag = True
            self.updateUI()
            self.show()

    def turnOff(self):
        #self.btnCheck.setChecked(False)
        if self.isTimerExit:
            self.timer.stop()
        self.totalFlag = False
        self.battle.stop()
        #self.timer.stop()
        self.hide()
        if self.isThTagExit:
            self.thSetText.join()

    def closeEvent(self, event):
        self.turnOff()
        event.accept()

    def goToMainpage(self):
        print('正在返回首页')
        listGoToTemp = self.listGoTo.copy()
        tryCount = 0
        while self.autoSwitch:
            self.adb.screenShot()
            for eachStep in listGoToTemp:
                bInfo = pictureFind.matchImg(self.screenShot, eachStep)
                if bInfo != None:
                    listGoToTemp.remove(eachStep)
                    break
            else:
                listGoToTemp = self.listGoTo.copy()
                tryCount += 1
                if tryCount > 10:
                    return False

            if bInfo != None:
                if bInfo['obj'] == 'act.png': #self.mainpageMark
                    print('已返回首页')
                    return True
                else:
                    self.adb.click(bInfo['result'][0], bInfo['result'][1])
    
    def chooseTag(self):
        tagState = self.publicCall.chooseTag()
        while tagState == 100:
            tagState = self.publicCall.chooseTag()
        if tagState == 6 or tagState == 1:
            for i in range(5):
                self.adb.screenShot()
                picInfo = pictureFind.matchImg(self.screenShot, self.pcCancel)
                if picInfo != None:
                    picInfo = picInfo['result']
                    self.adb.click(picInfo[0], picInfo[1])
                    break
        else:
            if self.advCredOnly and tagState < 4:
                self.adb.screenShot()
                cancelBtn = pictureFind.matchImg(self.screenShot, self.pcCancel)
                if cancelBtn != None:
                    cancelBtn = cancelBtn["result"]
                    self.adb.click(cancelBtn[0],cancelBtn[1])
                return False
            for i in range(5):
                self.adb.screenShot()
                addBtn = pictureFind.matchMultiImg(self.screenShot, self.pcDecreaseTime)[0]
                if addBtn != None:
                    addBtn.sort(key=lambda x:x[0])
                    addBtn = addBtn[0]
                    break
            else:
                return False
            picInfo = pictureFind.matchImg(self.screenShot, self.pc9, confidencevalue=0.9)
            while picInfo == None:
                if not self.autoSwitch:
                    return False
                self.adb.click(addBtn[0], addBtn[1])
                self.adb.screenShot()
                picInfo = pictureFind.matchImg(self.screenShot, self.pc9, confidencevalue=0.9)
            for i in range(5):
                #confirmBtn = pictureFind.matchImg(self.screenShot, self.pcCancel)
                confirmBtn = pictureFind.matchImg(self.screenShot, self.pcConfirm)
                if confirmBtn != None:
                    confirmBtn = confirmBtn['result']
                    self.adb.click(confirmBtn[0], confirmBtn[1])
                    return True
            return False

    def enterPC(self):
        print('正在进入公开招募界面...')
        for i in range(5):
            if not self.autoSwitch:
                return False
            self.adb.screenShot()
            picInfo = pictureFind.matchImg(self.screenShot, self.pcEnter)
            if picInfo != None:
                self.adb.click(picInfo['result'][0], picInfo['result'][1])
                while pictureFind.matchImg(self.screenShot, self.pcMark) == None:
                    sleep(1)
                    self.adb.screenShot()
                print('已经进入公开招募界面')
                return True
        else:
            print('无法进入公开招募界面，后续操作中断')
            return False
    
    def employ(self):
        for i in range(2):
            picInfo = pictureFind.matchMultiImg(self.screenShot, self.pcFinish)[0]
            if picInfo != None:
                if not self.autoSwitch:
                    break
                for eachPos in picInfo:
                    self.adb.click(eachPos[0], eachPos[1])
                    self.adb.screenShot()
                    while pictureFind.matchImg(self.screenShot, self.pcMark) == None:
                        for i in range(5):
                            self.adb.click(1400, 40)
                        sleep(1)
                        self.adb.screenShot()
            else:
                break
        return True

    def search(self):
        lastPicInfo = None
        for i in range(5):
            #多次搜索，确保找到所有可招募的位置
            self.adb.screenShot()
            picInfo = pictureFind.matchMultiImg(self.screenShot, self.pcNew)[0] #找到所有空的招募位
            if picInfo != None and len(picInfo) == 4:
                #已达到最多空闲位数，直接跳出
                break
            elif lastPicInfo == None:
                lastPicInfo = picInfo
            elif len(picInfo) > len(lastPicInfo):
                lastPicInfo = picInfo
        if lastPicInfo != None:
            picInfo = lastPicInfo
        if picInfo != None:
            for eachPos in picInfo:
                for i in range(3):
                    if not self.autoSwitch:
                        return False
                    self.adb.click(eachPos[0], eachPos[1])
                    sleep(0.5)
                    self.adb.screenShot()
                    inMarkInfo = pictureFind.matchImg(self.screenShot, self.pcInMark)
                    if inMarkInfo != None:
                        self.chooseTag()
                        break

    
    def autoPCRun(self, switch):
        self.autoSwitch = switch
        #self.adb.connect()
        self.goToMainpage()
        if self.enterPC():
            if self.employFlag:
                print('开始聘用干员')
                self.employ()
            if self.searchFlag:
                print('开始招募干员')
                self.search()
        self.goToMainpage()

    def autoPCStop(self):
        self.autoSwitch = False

    def tagTest(self):
        tempTh = Thread(target=self.autoPCRun)
        tempTh.start()