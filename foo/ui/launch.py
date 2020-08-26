import sys
from PyQt5.QtWidgets import QSplashScreen, QLabel, QWidget, QPushButton, QGridLayout, QTextBrowser, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from os import getcwd

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
        self.boardNotice.setText('这会没有公告')

        self.grid = QGridLayout()
        self.grid.addWidget(self.boardNotice,0,0,1,4)
        self.grid.addWidget(self.btnKnow,1,3,1,1)

        self.setLayout(self.grid)
        self.grid.setVerticalSpacing(5)
        
    def showNotice(self,text):
        self.boardNotice.setText(text)
        self.show()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    test = BlackBoard()
    sys.exit(app.exec_())