from os import getcwd
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMenu, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget, QLineEdit)

class AMessageBox(QWidget):
    ans = pyqtSignal(tuple)
    def __init__(self, theme = None):
        super(AMessageBox, self).__init__()
        self.setWindowIcon(QIcon(getcwd() + '/res/ico.ico'))

        if theme != None:
            self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}
                                QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
                                QPushButton{{border:0px;background:{theme.getFgColor()};
                                color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                QPushButton:pressed{{background:{theme.getPressedColor()};font:9pt;}}
                                QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()}}}
                                QLineEdit{{color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:12pt;}}
                            ''')

        self.setMinimumWidth(400)

        self.isBtnClicked = False

        self.btnOK = QPushButton('确定')
        self.btnOK.setMinimumSize(75, 40)
        self.btnOK.clicked.connect(self.btnClicked)
        self.btnCancel = QPushButton('取消')
        self.btnCancel.setMinimumSize(75, 40)
        self.btnCancel.clicked.connect(self.btnClicked)

        self.input = QLineEdit()
        self.input.setMinimumSize(150, 40)
        self.notice = QLabel('测试文本')

        topVLayout = QVBoxLayout()
        highVLayout = QVBoxLayout()
        lowHLayout = QHBoxLayout()

        topVLayout.addLayout(highVLayout)
        topVLayout.addLayout(lowHLayout)

        highVLayout.addWidget(self.notice)
        highVLayout.addWidget(self.input)

        lowHLayout.addStretch(1)
        lowHLayout.addWidget(self.btnOK)
        lowHLayout.addWidget(self.btnCancel)

        self.setLayout(topVLayout)
        #self.show()

    def btnClicked(self):
        self.isBtnClicked = True
        source = self.sender()
        if self.input.isVisible():
            txt = self.input.text()
        else:
            txt = ''
        
        if source == self.btnOK:
            self.ans.emit((txt, True))
        elif source == self.btnCancel:
            self.ans.emit((txt, False))
        
        self.close()

    def closeEvent(self, event):
        if not self.isBtnClicked:
            if self.input.isVisible():
                txt = self.input.text()
            else:
                txt = ''
            self.ans.emit((txt, False))
        self.isBtnClicked = False
        event.accept()

    def warning(self, title, warningMsg):
        self.setWindowTitle(title)
        self.notice.setText(warningMsg)
        self.notice.show()
        self.input.hide()
        self.btnOK.show()
        self.btnCancel.hide()
        self.show()

    def inputDialog(self, title, reminderText):
        self.setWindowTitle(title)
        self.notice.setText(reminderText)
        self.notice.show()
        self.input.show()
        self.input.setText('')
        self.btnOK.show()
        self.btnCancel.show()
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    messagebox = AMessageBox()
    sys.exit(app.exec_())