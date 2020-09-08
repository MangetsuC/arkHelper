from os import getcwd
from sys import path
from threading import Thread, Lock
from time import sleep, perf_counter

path.append(getcwd())
from foo.arknight.PublicCall import PublicCall

from PyQt5.QtWidgets import QDialog, QGridLayout, QTextBrowser, QPushButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer

class UIPublicCall(QDialog):
    def __init__(self, adb, battle, cwd, btnCheck, parent=None, flags=Qt.WindowFlags(1)):
        super().__init__(parent=parent, flags=flags)
        self.initVar(adb, battle, cwd, btnCheck)
        self.initUI()
        self.myTimer()
        
    def initVar(self, adb, battle, cwd, btnCheck):
        self.cwd = cwd
        self.battle = battle
        self.btnCheck = btnCheck
        
        self.publicCall = PublicCall(adb, self.cwd)
        
        self.tags = []
        self.text = '正在连接'
        self.beforeText = 'init'
        self.isShowAll = False
        self.monitorFlag = False
        self.totalFlag = True
        self.lock  = Lock()
        self.isExit = False
    
    def initUI(self):
        self.setWindowTitle('公开招募计算器')
        self.setWindowIcon(QIcon(self.cwd + '/res/ico.ico'))
        self.grid = QGridLayout()
        
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

        self.tagsBrowser = QTextBrowser(self)
        self.tagsBrowser.setFixedHeight(80)

        self.textBrowser = QTextBrowser(self)
        
        self.btnShowAll = QPushButton('显示全部干员', self)
        self.btnShowAll.setCheckable(True)
        self.btnShowAll.clicked[bool].connect(self.showAllChange)
        self.btnShowAll.setFixedHeight(40)
        
        self.grid.addWidget(self.lbText, 0, 0, 2, 1)
        #self.grid.addWidget(self.tagsBrowser, 0, 1, 2, 3)
        self.tagsBrowser.hide()

        self.grid.addWidget(self.tag0, 0, 1, 1, 1)
        self.grid.addWidget(self.tag1, 0, 2, 1, 1)
        self.grid.addWidget(self.tag2, 0, 3, 1, 1)
        self.grid.addWidget(self.tag3, 1, 1, 1, 1)
        self.grid.addWidget(self.tag4, 1, 2, 1, 1)

        self.grid.addWidget(self.textBrowser, 2, 0, 6, 4)
        self.grid.addWidget(self.btnShowAll, 8, 0, 1, 4)
        
        self.setLayout(self.grid)
        self.resize(350,800)
        self.setFixedWidth(430)
        
        self.setStyleSheet('''UIPublicCall{background-color:#272626;}
        QTextBrowser{background-color:#4d4d4d;color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:14pt;}
        QPushButton{border:0px;background:#4d4d4d;color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QPushButton:pressed{background:#606162;font:9pt;}
                                QPushButton:checked{background:#70bbe4;}
        QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}''')

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
    
    def showAllChange(self, ischecked):
        self.isShowAll = ischecked
    
    def getTextBrowser(self):
        #tempT = perf_counter()
        self.monitorFlag = self.battle.connect()
        while self.monitorFlag and self.totalFlag:
            text = ''
            ans = self.publicCall.run()
            if not ans:
                text = '未发现公开招募标签'
                self.tags = [] #改为列表
            else:
                tags = ans[1]
                ans = ans[0]
                self.tags = tags #改为列表
                keyValueList = ans.items()
                keyValueList = list(keyValueList)
                keyValueList.sort(key = lambda x:len(x[0]), reverse = True)
                for eachKeyValue in keyValueList:
                    if not (self.monitorFlag and self.totalFlag):
                        break
                    eachKeyValue[1].sort()

                    tempStr = ''
                    for eachValue in eachKeyValue[1]:
                        if not (self.monitorFlag and self.totalFlag):
                            break
                        if eachValue[0] >= 4:
                            tempStr = tempStr + f'{str(eachValue[0])[0]}星：' + eachValue[1] + '；\n'
                        elif self.isShowAll:
                            tempStr = tempStr + f'{eachValue[0]}星：' + eachValue[1] + '；\n'
                        else:
                            if text == '':
                                text = '无稳定高星组合'
                            break
                    else:
                        if text == '无稳定高星组合':
                            text = ''
                        text = text + eachKeyValue[0] + '\n' + tempStr
            if not (self.monitorFlag and self.totalFlag):
                break
            self.lock.acquire()
            self.text = text
            #print(self.text)
            self.lock.release()
            #print('总'+str(perf_counter() - tempT))

    def updateBrowser(self):
        if self.tags == []:
            for each in self.tagsLabelList:
                each.setText('')
            #self.tagsBrowser.setText('')
        else:
            for i in range(5):
                self.tagsLabelList[i].setText(self.tags[i])
            #self.tagsBrowser.setText('|'.join(self.tags)) #临时调整
        
        if self.text != self.beforeText:
            self.beforeText = self.text
            self.textBrowser.setText(self.text)

    def myTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBrowser)
        self.timer.start(10)
        

    def updateUI(self):
        self.thSetText = Thread(target=self.getTextBrowser)
        self.thSetText.setDaemon(True)
        self.thSetText.start()

    def turnOn(self):
        self.monitorFlag = True
        self.updateUI()
        self.show()

    def turnOff(self):
        self.monitorFlag = False
        #self.timer.stop()
        self.hide()
        self.thSetText.join()

    def closeEvent(self, event):
        if not self.isExit:
            event.ignore()
            self.btnCheck.setChecked(False)
            self.turnOff()
        else:
            if self.monitorFlag:
                self.thSetText.join()
            event.accept()

    def exit(self):
        self.isExit = True
        self.totalFlag = False
        self.timer.stop()
        self.close()

