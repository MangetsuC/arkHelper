from os import getcwd
from sys import path
from threading import Thread, Lock
from time import sleep, perf_counter

path.append(getcwd())
from foo.arknight.PublicCall import PublicCall

from PyQt5.QtWidgets import QDialog, QGridLayout, QTextBrowser, QPushButton
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
        
        self.text = '正在监测公开招募'
        self.beforeText = 'init'
        self.isShowAll = False
        self.monitorFlag = False
        self.lock  = Lock()
        self.isExit = False
    
    def initUI(self):
        self.setWindowTitle('公开招募计算器')
        self.setWindowIcon(QIcon(self.cwd + '/res/ico.ico'))
        self.grid = QGridLayout()
        
        self.textBrowser = QTextBrowser(self)
        
        self.btnShowAll = QPushButton('显示全部干员', self)
        self.btnShowAll.setCheckable(True)
        self.btnShowAll.clicked[bool].connect(self.showAllChange)
        self.btnShowAll.setFixedHeight(40)
        
        self.grid.addWidget(self.textBrowser, 0, 0, 6, 1)
        self.grid.addWidget(self.btnShowAll, 6, 0, 1, 1)
        
        self.setLayout(self.grid)
        self.resize(350,700)
        self.setFixedWidth(350)
        
        self.setStyleSheet('''UIPublicCall{background-color:#272626;}
        QTextBrowser{background-color:#4d4d4d;color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:14pt;}
        QPushButton{border:0px;background:#4d4d4d;color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QPushButton:pressed{background:#606162;font:9pt;}
                                QPushButton:checked{background:#70bbe4;}''')
    
    def showAllChange(self, ischecked):
        self.isShowAll = ischecked
    
    def getTextBrowser(self):
        #tempT = perf_counter()
        self.monitorFlag = self.battle.connect()
        while self.monitorFlag:
            text = ''
            ans = self.publicCall.run()
            if not ans:
                text = '未发现公开招募标签'
            else:
                keyValueList = ans.items()
                keyValueList = list(keyValueList)
                keyValueList.sort(key = lambda x:len(x[0]), reverse = True)
                for eachKeyValue in keyValueList:
                    eachKeyValue[1].sort()

                    tempStr = ''
                    for eachValue in eachKeyValue[1]:
                        if eachValue[0] >= 4:
                            tempStr = tempStr + f'{str(eachValue[0])[0]}星：' + eachValue[1] + '；\n'
                        elif self.isShowAll:
                            tempStr = tempStr + f'{eachValue[0]}星：' + eachValue[1] + '；\n'
                        else:
                            text = '无稳定高星组合'
                            break
                    else:
                        text = text + eachKeyValue[0] + '\n' + tempStr
            self.lock.acquire()
            self.text = text
            #print(self.text)
            self.lock.release()
            #print('总'+str(perf_counter() - tempT))

    def updateBrowser(self):
        if self.text != self.beforeText:
            self.beforeText = self.text
            self.textBrowser.setText(self.text)

    def myTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBrowser)
        self.timer.start(100)
        

    def updateUI(self):
        self.thSetText = Thread(target=self.getTextBrowser)
        self.thSetText.setDaemon(True)
        self.thSetText.start()

    def turnOn(self):
        self.updateUI()
        self.show()

    def turnOff(self):
        self.monitorFlag = False
        #self.timer.stop()
        self.hide()
        #self.thSetText.join()

    def closeEvent(self, event):
        if not self.isExit:
            event.ignore()
            self.btnCheck.setChecked(False)
            self.turnOff()
        else:
            event.accept()

    def exit(self):
        self.isExit = True
        self.close()

