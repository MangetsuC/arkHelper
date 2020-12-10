from os import getcwd
from sys import path
from threading import Thread, Lock
from time import sleep, perf_counter
path.append(getcwd())
from foo.arknight.PublicCall import PublicCall

from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QLabel, QWidget, QScrollArea
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

class UIPublicCall(QDialog):
    def __init__(self, adb, battle, cwd, btnCheck, normal, high, parent=None, flags=Qt.WindowFlags(1)):
        super().__init__(parent=parent, flags=flags)
        self.initVar(adb, battle, cwd, btnCheck, normal, high)
        self.initUI()
        #self.myTimer()
        
    def initVar(self, adb, battle, cwd, btnCheck, normal, high):
        self.cwd = cwd
        self.battle = battle
        self.btnCheck = btnCheck
        
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
    
    def initUI(self):
        self.setWindowTitle('公开招募计算器')
        self.setWindowIcon(QIcon(self.cwd + '/res/ico.ico'))
        self.grid = QGridLayout()

        self.combFiller = QWidget()
        self.combGrid = QGridLayout()
        self.combGrid.setAlignment(Qt.AlignTop)
        self.combFiller.setLayout(self.combGrid)
        self.combFiller.setMinimumSize(400, 2000)#######设置滚动条的尺寸
        self.scroll = QScrollArea()
        self.scroll.viewport().setStyleSheet("background-color:#4d4d4d;")
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
            eachLabel.setStyleSheet('''QLabel {border-style: solid;border-left-width: 5px;border-right-width: 5px;border-top-width: 2px;border-bottom-width: 2px;
            border-color: #4d4d4d;border-radius: 0px;background-color: #4d4d4d;}''')
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
        
        self.setStyleSheet('''UIPublicCall{background-color:#272626;}
        QPushButton{border:0px;background:#4d4d4d;color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QPushButton:pressed{background:#606162;font:9pt;}
                                QPushButton:checked{background:#70bbe4;}
        QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}
        QScrollArea{background-color:#4d4d4d;}
        QScrollBar:vertical{width:8px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:2px;padding-bottom:2px;}
        QScrollBar:handle:vertical{width:8px;background:rgba(0,0,0,25%);border-radius:0px;min-height:20;}
        QScrollBar:handle:vertical:hover{width:8px;background:rgba(0,0,0,50%);border-radius:0px;min-height:20;}
        QScrollBar:add-line:vertical{height:0px;width:0px;subcontrol-position:bottom;}
        QScrollBar:sub-line:vertical{height:0px;width:0px;subcontrol-position:top;}
        QScrollBar:add-page:vertical,QScrollBar:sub-page:vertical{background:rgba(0,0,0,10%);border-radius:0px;}
        QScrollBar:horizontal{height:8px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}
        QScrollBar:handle:horizontal{width:8px;background:rgba(0,0,0,25%);border-radius:0px;min-height:20;}
        QScrollBar:handle:horizontal:hover{width:8px;background:rgba(0,0,0,50%);border-radius:0px;min-height:20;}
        QScrollBar:add-line:horizontal{height:0px;width:0px;subcontrol-position:bottom;}
        QScrollBar:sub-line:horizontal{height:0px;width:0px;subcontrol-position:top;}
        QScrollBar:add-page:horizontal,QScrollBar:sub-page:horizontal{background:rgba(0,0,0,10%);border-radius:0px;}''')

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
    
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
                        tempTagLabel.setStyleSheet('''QLabel {border-style: solid;border-left-width: 5px;border-right-width: 5px;border-top-width: 2px;border-bottom-width: 2px;
                                            border-color: #808080;border-radius: 8px;background-color: #808080;}''')
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
        self.myTimer()
        self.totalFlag = True
        self.updateUI()
        self.show()

    def turnOff(self):
        self.btnCheck.setChecked(False)
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