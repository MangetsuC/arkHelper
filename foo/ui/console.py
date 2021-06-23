import sys
from time import localtime, strftime, time

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QDialog, QGridLayout, QTextBrowser, QDesktopWidget


class Console(QDialog):
    def __init__(self, cwd, parent=None, flags=Qt.WindowFlags(1)):
        super().__init__(parent=parent, flags=flags)
        self.cwd = cwd
        self.setWindowIcon(QIcon(self.cwd + '/res/ico.ico'))
        self.isShow = False
        self.isExit = False
        self.setWindowTitle('控制台')
        self.resize(600,400)
        self.textBrowser = QTextBrowser(self)

        self.grid = QGridLayout()
        self.grid.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.setLayout(self.grid)

        sys.stdout = EmittingStr(sgnConsole = self.outputWritten)
        sys.stderr = EmittingStr(sgnConsole = self.outputWritten)

    def applyStyleSheet(self, theme):
        self.setStyleSheet(f'''Console{{background-color:{theme.getBgColor()};}}
                              QTextBrowser{{background-color:{theme.getFgColor()};
                                           color:{theme.getFontColor()};
                                           font-family:"Microsoft YaHei", SimHei, SimSun;
                                           font:10pt;}}''')

    def outputWritten(self, text):
        text = text.strip()
        if text != '':
            text = text + '\n'
            cursor = self.textBrowser.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            with open(self.cwd + '/arkhelper.log', 'a') as log:
                log.write(text)
            self.textBrowser.setTextCursor(cursor)

    def showOrHide(self):
        if not self.isVisible():
            self.show()
            cp = QDesktopWidget().availableGeometry().center()
            self.move(int(cp.x() - self.width()/2), int(cp.y() - self.height()/2))

class EmittingStr(QObject):
    sgnConsole = pyqtSignal(str)

    def write(self, text):
        if text != '\n':
            timeNow = strftime("%Y-%m-%d %H:%M:%S" ,localtime())
            text = '[{logTime}]{logText}'.format(logTime = timeNow, logText = str(text))
        self.sgnConsole.emit(text)
