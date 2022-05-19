import sys
from os import getcwd
from time import localtime, strftime, time

from PySide6.QtCore import QObject, Qt, Signal, SIGNAL
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import QGridLayout, QTextBrowser, QWidget

from common import theme, app_ico

class Console(QWidget):
    def __init__(self, ver):
        super().__init__()
        self.cwd = getcwd()
        self.setWindowIcon(app_ico)
        self.isShow = False
        self.isExit = False
        self.setWindowTitle('控制台')
        self.resize(600,400)
        self.textBrowser = QTextBrowser(self)

        self.grid = QGridLayout()
        self.grid.addWidget(self.textBrowser, 0, 0, 1, 1)
        self.setLayout(self.grid)
        if ver != "DEV":
            self.stream = EmittingStr()
            self.stream.sgnConsole.connect(self.outputWritten)
            sys.stdout = self.stream
            sys.stderr = self.stream
        else:
            self.textBrowser.setText('In DEV')
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            print('IN DEV')

        self.applyStyleSheet(theme)

    def applyStyleSheet(self, theme):
        self.setStyleSheet(f'''Console{{background-color:{theme.getBgColor()};}}
                              QTextBrowser{{background-color:{theme.getFgColor()};
                                           color:{theme.getFontColor()};
                                           font-family:"Microsoft YaHei", SimHei, SimSun;
                                           font:10pt;}}
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

    def outputWritten(self, text):
        text = text.strip()
        if text != '':
            text = text + '\n'
            cursor = self.textBrowser.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            with open(self.cwd + '/arkhelper.log', 'a', encoding='UTF-8') as log:
                log.write(text)
            self.textBrowser.setTextCursor(cursor)

class EmittingStr(QObject):
    sgnConsole = Signal(str)

    def write(self, text):
        if text != '\n':
            timeNow = strftime("%Y-%m-%d %H:%M:%S" ,localtime())
            text = '[{logTime}]{logText}'.format(logTime = timeNow, logText = str(text))
        self.sgnConsole.emit(text)
