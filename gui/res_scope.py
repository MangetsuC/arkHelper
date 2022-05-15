from ctypes import alignment
import sys
from os import getcwd, getlogin, path, system
from ast import literal_eval

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QIcon, QTextCursor, QPixmap
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
                               QPushButton, QTextBrowser, QVBoxLayout, QWidget, QScrollArea, QLabel, QTextEdit)

sys.path.append(getcwd())
from common import res_config
from common2 import adb
from image_.image_io import del_image, output_image
from foo.ui.messageBox import AMessageBox
from user_res import R
from common import theme
from image_.match import match_pic_signal

#adb.ip = '127.0.0.1:7555' #测试时选定模拟器用


class Res_scope(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('资源状态监视器')
        self.setMinimumWidth(450)
        self.setMinimumHeight(700)

        self.init_ui()

        self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}
                                QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:14pt;}}
                                QScrollArea{{background-color:{theme.getFgColor()};}}
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
        match_pic_signal.pic_send.connect(self.set_pic_checked)


    def init_ui(self):
        self.mainLayout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        #self.scroll.setMaximumHeight(800)
        #self.scroll.setMinimumWidth(450)
        self.scroll_widget = QWidget()
        self.scroll_widget.setMinimumWidth(450)
        self.scroll_widget.setMinimumHeight(700)
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.res_names = []
        self.res_states = []
        
        for i in res_config.get_res_list():
            temp = QLabel(i)
            temp_state = QLabel('暂未识别')
            self.res_names.append(i)
            self.res_states.append(temp_state)

            temp_layout = QHBoxLayout()
            temp_layout.addWidget(temp, alignment=Qt.AlignCenter)
            temp_layout.addWidget(temp_state, alignment=Qt.AlignCenter)
            
            self.scroll_layout.addLayout(temp_layout)

        self.scroll.setWidget(self.scroll_widget)
        self.mainLayout.addWidget(self.scroll)

    def set_pic_checked(self, pic_name):
        pic_index = self.res_names.index(pic_name)
        self.res_states[pic_index].setText('已识别')
        

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    res_scope = Res_scope()
    res_scope.show()
    sys.exit(app.exec())








