import sys
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget,QApplication, QPushButton,QCheckBox, QDialog,QScrollArea
from PySide6.QtCore import QMimeData,Qt
from PySide6.QtGui import QDrag,QPainter,QPixmap,QColor

class QLeftTabWidget(QWidget):
    def __init__(self, scroll_max_height = 300):
        super().__init__()

        self.top_layout = QHBoxLayout(self)

        self.scrollarea = QScrollArea()
        self.btn_widget = QWidget()
        self.btn_widget.setMinimumWidth(150)
        #self.scrollarea.setMinimumWidth(160)
        self.btn_layout = QVBoxLayout()

        self.top_layout.addWidget(self.scrollarea)
        self.btn_list = []
        self.widget_list = []

        self.setMaximumHeight(scroll_max_height)

        self.setStyleSheet(f'''
                                QScrollBar:vertical{{width:8px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:2px;padding-bottom:2px;}}
                                QScrollBar:handle:vertical{{width:8px;background:rgba(0,0,0,25%);border-radius:0px;min-height:20;}}
                                QScrollBar:handle:vertical:hover{{width:8px;background:rgba(0,0,0,50%);border-radius:0px;min-height:20;}}
                                QScrollBar:add-line:vertical{{height:0px;width:0px;subcontrol-position:bottom;}}
                                QScrollBar:sub-line:vertical{{height:0px;width:0px;subcontrol-position:top;}}
                                QScrollBar:add-page:vertical,QScrollBar:sub-page:vertical{{background:rgba(0,0,0,10%);border-radius:0px;}}
                                QScrollBar:horizontal{{height:0px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}}
                                QScrollBar:handle:horizontal{{width:0px;background:rgba(0,0,0,25%);border-radius:0px;min-height:20;}}
                                QScrollBar:handle:horizontal:hover{{width:0px;background:rgba(0,0,0,50%);border-radius:0px;min-height:20;}}
                                QScrollBar:add-line:horizontal{{height:0px;width:0px;subcontrol-position:bottom;}}
                                QScrollBar:sub-line:horizontal{{height:0px;width:0px;subcontrol-position:top;}}
                                QScrollBar:add-page:horizontal,QScrollBar:sub-page:horizontal{{background:rgba(0,0,0,10%);border-radius:0px;}}
                            ''')

    def addTab(self, widget, tab_name, btn_size = (120, 40, 6)):
        if len(tab_name) > btn_size[2]:
            new_tab_name = tab_name[0:3] + '...' + tab_name[len(tab_name)-3:len(tab_name)]
        else:
            new_tab_name = tab_name
        btn = QPushButton(new_tab_name)
        btn.setToolTip(tab_name)
        btn.setCheckable(True)
        btn.clicked.connect(self.change_tab)
        btn.setFixedSize(btn_size[0], btn_size[1])

        self.btn_layout.addWidget(btn, alignment=Qt.AlignHCenter)
        self.top_layout.addWidget(widget)

        self.btn_list.append(btn)
        self.widget_list.append(widget)

        if len(self.btn_list) == 1:
            btn.setChecked(True)
            widget.show()
        else:
            widget.hide()


    def finish_add(self):
        self.btn_widget.setLayout(self.btn_layout)
        self.scrollarea.setWidget(self.btn_widget)

    def change_tab(self):
        sender = self.sender()
        if sender.isChecked():
            index = self.btn_list.index(sender)
            for i in self.widget_list:
                i.hide()

            for i in range(len(self.widget_list)):
                if i == index:
                    self.widget_list[i].show()
                else:
                    self.btn_list[i].setChecked(False)
        else:
            sender.setChecked(True)

        



















