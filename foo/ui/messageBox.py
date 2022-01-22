from os import getcwd, path, getlogin
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDialog,
                             QHBoxLayout,
                             QLabel,
                             QPushButton, QVBoxLayout, QLineEdit)

from common import theme

class AMessageBox(QDialog):
    def __init__(self, parent):
        super(AMessageBox, self).__init__(parent)
        self.setWindowIcon(QIcon(getcwd() + '/res/ico.ico'))

        self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}
                            QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
                            QPushButton{{border:0px;background:{theme.getFgColor()};
                            color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                            QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                            QPushButton:pressed{{background:{theme.getPressedColor()};font:9pt;}}
                            QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()}}}
                            QLineEdit{{color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                       border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                        ''')

        self.setMinimumWidth(400)

        self.isBtnClicked = False

        self.btnOK = QPushButton('确定')
        self.btnOK.setMinimumSize(70, 30)
        self.btnOK.clicked.connect(self.btnClicked)
        self.btnCancel = QPushButton('取消')
        self.btnCancel.setMinimumSize(70, 30)
        self.btnCancel.clicked.connect(self.btnClicked)

        self.input = QLineEdit()
        self.input.setMinimumSize(150, 30)
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

        self.ans = ['', False]
        #self.show()

    def btnClicked(self):
        if self.sender() == self.btnOK:
            self.ans[1] = True
        
        self.close()

    def closeEvent(self, event):
        if self.input.isVisible():
            self.ans[0] = self.input.text()
        event.accept()

    def warningInit(self, title, warningMsg):
        self.setWindowTitle(title)
        self.notice.setText(warningMsg)
        self.notice.show()
        self.input.hide()
        self.btnOK.show()
        self.btnCancel.hide()

    def questionInit(self, title, questionMsg):
        self.setWindowTitle(title)
        self.notice.setText(questionMsg)
        self.notice.show()
        self.input.hide()
        self.btnOK.show()
        self.btnCancel.show()

    def inputInit(self, title, reminderText):
        self.setWindowTitle(title)
        self.notice.setText(reminderText)
        self.notice.show()
        self.input.show()
        self.input.setText('')
        self.btnOK.show()
        self.btnCancel.show()

    @classmethod
    def warning(cls, parent, title, msg):
        warningDialog = cls(parent)
        warningDialog.warningInit(title, msg)
        warningDialog.exec_()
        return warningDialog.ans[1]

    @classmethod
    def question(cls, parent, title, msg):
        questionDialog = cls(parent)
        questionDialog.questionInit(title, msg)
        questionDialog.exec_()
        return questionDialog.ans[1]

    @classmethod
    def input(cls, parent, title, msg):
        inputDialog = cls(parent)
        inputDialog.inputInit(title, msg)
        inputDialog.exec_()
        return inputDialog.ans
