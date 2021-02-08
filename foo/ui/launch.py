import sys
from PyQt5.QtWidgets import QSplashScreen, QLabel, QWidget, QPushButton, QGridLayout, QTextBrowser, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from os import getcwd
from threading import Thread
from urllib import request
from configparser import ConfigParser
from  time import sleep

class Launch(QSplashScreen):
    def __init__(self):
        super(Launch, self).__init__(QPixmap(getcwd() + '/res/gui/launchWindow.png'))
        self.setWindowIcon(QIcon(getcwd() + '/res/ico.ico'))
        self.show()

class BlackBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('''BlackBoard{background:#272626}
                                QPushButton{border:0px;background:#272626;color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:12pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QPushButton:pressed{background:#606162;font:11pt;}
                                QTextBrowser{background-color:#292A2A;color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:14pt;
                                border-width:0px;border-style:outset;}
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
                                QScrollBar:add-page:horizontal,QScrollBar:sub-page:horizontal{background:rgba(0,0,0,10%);border-radius:0px;}
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

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    test = BlackBoard()
    sys.exit(app.exec_())