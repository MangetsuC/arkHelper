import sys
from PyQt5.QtWidgets import QSplashScreen, QWidget, QPushButton, QGridLayout, QTextBrowser, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from os import getcwd, path, remove, rename
from time import sleep
import requests
from json import loads, dumps
from hashlib import md5
from common import config_path, user_data, theme

class Launch(QSplashScreen):
    def __init__(self):
        super(Launch, self).__init__(QPixmap(getcwd() + '/res/gui/launchWindow.png'))
        self.setWindowIcon(QIcon(getcwd() + '/res/ico.ico'))
        self.show()

class BlackBoard(QWidget):
    def __init__(self):
        super().__init__()
        if theme != None:
            self.setStyleSheet(f'''BlackBoard{{background:{theme.getBgColor()}}}
            QPushButton{{border:0px;background:{theme.getBgColor()};color:{theme.getFontColor()};
                        font-family: "Microsoft YaHei", SimHei, SimSun;font:12pt;}}
            QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
            QPushButton:pressed{{background:{theme.getPressedColor()};font:11pt;}}
            QTextBrowser{{background-color:{theme.getBgColor()};color:{theme.getFontColor()};
                        font-family:"Microsoft YaHei", SimHei, SimSun;font:14pt;
            border-width:2px;border-style:solid;border-color:{theme.getFgColor()}}}
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
            QScrollBar:add-page:horizontal,QScrollBar:sub-page:horizontal{{background:rgba(0,0,0,10%);border-radius:0px;}}
            ''')

        self.setWindowTitle('公告栏')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon(getcwd() + '/res/ico.ico'))

        self.btnKnow = QPushButton(text = '我知道了')
        self.btnKnow.setFixedHeight(40)
        self.btnKnow.setMinimumWidth(80)
        self.btnKnow.clicked.connect(self.close)
        self.boardNotice = QTextBrowser(self)
        self.boardNotice.setMinimumSize(600,400)

        self.grid = QGridLayout()
        self.grid.addWidget(self.boardNotice,0,0,1,4)
        self.grid.addWidget(self.btnKnow,1,3,1,1)

        self.setLayout(self.grid)
        self.grid.setVerticalSpacing(5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.globalPos() - self.pos() #获取鼠标相对窗口的位置
            self.moveFlag = True
            event.accept()
            
    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.moveFlag:  
            self.move(QMouseEvent.globalPos() - self.mousePos) #更改窗口位置
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        #停止窗口移动
        self.moveFlag = False
    
    def updateText(self, newText):
        self.boardNotice.setText(newText)
        #self.show()

class AfterInit(QThread):
    boardNeedShow = pyqtSignal()
    reloadPcModule = pyqtSignal()
    logisticReady = pyqtSignal()
    widgetShow = pyqtSignal(int) #0:公告按钮 1:升级按钮
    def __init__(self, app, cwd):
        super(AfterInit, self).__init__()
        self.app = app
        self.cwd = cwd

    def run(self):
        self.getLogisticRule()
        self.checkPublicCallData()
        self.checkMessage()
        self.checkUpdate()

    def getFileMd5(self, fileName):
        m = md5()   #创建md5对象
        with open(fileName,'rb') as fobj:
            while True:
                data = fobj.read(4096)
                if not data:
                    break
                m.update(data)  #更新md5对象

        return m.hexdigest()    #返回md5对象

    def checkUpdate(self):
        updateData = requests.get('http://www.mangetsuc.top/arkhelper/update.json')
        if updateData.status_code == 200:
            updateData.encoding = 'utf-8'
            self.app._updateData = loads(updateData.text)
            updateEXE = self.app._updateData.get('updateEXE', 'update.exe')
            if updateEXE != 'update.exe' and path.exists(self.cwd + '/update.exe') and path.exists(self.cwd + '/' + updateEXE):
                remove(self.cwd + '/update.exe')
                rename(self.cwd + '/' + updateEXE, self.cwd + '/update.exe')
            newVersion =self.app._updateData['version'].split('.')
            if self.app.ver != 'DEV' and self.app.ver != 'ERR':
                tempSelfVersion = self.app.ver.split('.')
                ver0 = int(newVersion[0]) == int(tempSelfVersion[0])
                ver1 = int(newVersion[1]) == int(tempSelfVersion[1])
                ver2 = int(newVersion[2]) == int(tempSelfVersion[2])
                isNeedUpdate = False
                if ver0:
                    if ver1:
                        if not ver2:
                            if int(newVersion[2]) > int(tempSelfVersion[2]):
                                isNeedUpdate = True
                    else:
                        if int(newVersion[1]) > int(tempSelfVersion[1]):
                            isNeedUpdate = True
                else:
                    if int(newVersion[0]) > int(tempSelfVersion[0]):
                        isNeedUpdate = True
                if isNeedUpdate:
                    self.widgetShow.emit(1)

    def checkMessage(self):
        noticeData = requests.get('http://www.mangetsuc.top/arkhelper/notice.html')
        if noticeData.status_code == 200:
            noticeData.encoding = 'utf-8'
            noticeMd5 = md5()
            noticeMd5.update(noticeData.text.encode("utf8"))
            self.app.noticeMd5 = noticeMd5.hexdigest()
            self.app._notice = noticeData.text
            self.widgetShow.emit(0)
            if noticeMd5.hexdigest() != user_data.get('notice'):
                self.boardNeedShow.emit()

    def checkPublicCallData(self):
        pcData = requests.get('http://www.mangetsuc.top/arkhelper/pcData.json')
        if pcData.status_code == 200:
            pcData.encoding = 'utf-8'
            temp = loads(pcData.text)
            tempData = dict()
            tempData['data'] = temp
            if tempData != self.app._data:
                with open(self.cwd + '/data.json', 'w', encoding='UTF-8') as f:
                    f.write(dumps(tempData, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
                if self.app._data == None:
                    self.reloadPcModule.emit()
                while self.app._data == None:
                    sleep(0.1)
                self.app.publicCall.updateTag()

    def getLogisticRule(self):
        #自动下载基建规则文件
        if not path.exists(config_path + '/logisticRule.ahrule'):
            rule = requests.get('http://www.mangetsuc.top/arkhelper/logisticRule.txt')
            if rule.status_code == 200:
                rule.encoding = 'UTF-8'
                temp = rule.text.strip('\ufeff')
                with open(config_path + '/logisticRule.ahrule', 'w', encoding = 'utf-8') as f:
                    f.write('\n'.join([s for s in temp.splitlines() if s.strip()]))
                self.logisticReady.emit()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    test = BlackBoard()
    sys.exit(app.exec_())