from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMenu, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget, QLineEdit, QColorDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor
from common import user_data, theme

class ThemeEditor(QWidget):
    def __init__(self, app, ico = ''):
        super(ThemeEditor, self).__init__()

        self.app = app

        self.colorSelector = QColorDialog()
        self.colorSelector.colorSelected.connect(self.colorOK)

        self.source = None

        if theme != None:
            self.setStyleSheet(f'''
                                ThemeEditor{{background:{theme.getBgColor()}}}
                                QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                                QPushButton{{border:0px;background:{theme.getFgColor()};
                                color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                QPushButton:pressed{{background:{theme.getPressedColor()};font:9pt;}}
                                QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()}}}
                                QLineEdit{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};
                                           border-style:solid;border-width:0px;
                                           font-family:"Microsoft YaHei", SimHei, SimSun;font:10pt;}}
            ''')


        self.setWindowTitle('重启后生效')
        self.setWindowIcon(QIcon(ico))
        self.labelThemeColor = QLabel('打开的开关的颜色')
        self.labelFontColor = QLabel('字体颜色')
        self.labelCheckedFontColor = QLabel('打开的开关的字体颜色')
        self.labelBorderColor = QLabel('按钮悬停时边框颜色')
        self.labelFgColor = QLabel('前景色')
        self.labelBgColor = QLabel('背景色')
        self.labelPressedColor = QLabel('按下按钮时的颜色')
        self.labelSelectedColor = QLabel('√的颜色')

        self.setAutoThemeColor = QPushButton('自动')
        self.setAutoFontColor = QPushButton('自动')
        self.setAutoCheckedFontColor = QPushButton('自动')
        self.setAutoBorderColor = QPushButton('自动')
        self.setAutoFgColor = QPushButton('自动')
        self.setAutoBgColor = QPushButton('自动')
        self.setAutoPressedColor = QPushButton('自动')
        self.setAutoThemeColor.clicked.connect(self.setAuto)
        self.setAutoFontColor.clicked.connect(self.setAuto)
        self.setAutoCheckedFontColor.clicked.connect(self.setAuto)
        self.setAutoBorderColor.clicked.connect(self.setAuto)
        self.setAutoFgColor.clicked.connect(self.setAuto)
        self.setAutoBgColor.clicked.connect(self.setAuto)
        self.setAutoPressedColor.clicked.connect(self.setAuto)

        self.editorThemeColor = QPushButton()
        self.setColorBtnState(self.editorThemeColor, user_data.get('theme.themecolor'))
        self.editorThemeColor.clicked.connect(self.chooseColor)
        self.editorFontColor = QPushButton()
        self.setColorBtnState(self.editorFontColor, user_data.get('theme.fontcolor'))
        self.editorFontColor.clicked.connect(self.chooseColor)
        self.editorCheckedFontColor = QPushButton()
        self.setColorBtnState(self.editorCheckedFontColor, user_data.get('theme.checkedfontcolor'))
        self.editorCheckedFontColor.clicked.connect(self.chooseColor)
        self.editorBorderColor = QPushButton()
        self.setColorBtnState(self.editorBorderColor, user_data.get('theme.bordercolor'))
        self.editorBorderColor.clicked.connect(self.chooseColor)
        self.editorFgColor = QPushButton()
        self.setColorBtnState(self.editorFgColor, user_data.get('theme.fgcolor'))
        self.editorFgColor.clicked.connect(self.chooseColor)
        self.editorBgColor = QPushButton()
        self.setColorBtnState(self.editorBgColor, user_data.get('theme.bgcolor'))
        self.editorBgColor.clicked.connect(self.chooseColor)
        self.editorPressedColor = QPushButton()
        self.setColorBtnState(self.editorPressedColor, user_data.get('theme.pressedcolor'))
        self.editorPressedColor.clicked.connect(self.chooseColor)
        
        self.darkSelectedIcon = QPushButton('深色')
        self.darkSelectedIcon.setCheckable(True)
        self.darkSelectedIcon.clicked.connect(self.selectedIconSet)
        self.lightSelectedIcon = QPushButton('浅色')
        self.lightSelectedIcon.setCheckable(True)
        self.lightSelectedIcon.clicked.connect(self.selectedIconSet)
        self.autoSelectedIcon = QPushButton('自动')
        self.autoSelectedIcon.setCheckable(True)
        self.autoSelectedIcon.clicked.connect(self.selectedIconSet)
        selectedColor = user_data.get('theme.selectedcolor')
        if selectedColor == 'dark':
            self.darkSelectedIcon.setChecked(True)
        elif selectedColor == 'light':
            self.lightSelectedIcon.setChecked(True)
        else:
            self.autoSelectedIcon.setChecked(True)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.labelThemeColor, 0, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelCheckedFontColor, 1, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelFgColor, 2, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelBgColor, 3, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelFontColor, 4, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelBorderColor, 5, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelPressedColor, 6, 0, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.labelSelectedColor, 7, 0, 1, 1, alignment=Qt.AlignRight)

        self.grid.addWidget(self.editorThemeColor, 0, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.editorCheckedFontColor, 1, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.editorFgColor, 2, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.editorBgColor, 3, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.editorFontColor, 4, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.editorBorderColor, 5, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.editorPressedColor, 6, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoThemeColor, 0, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoCheckedFontColor, 1, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoFgColor, 2, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoBgColor, 3, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoFontColor, 4, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoBorderColor, 5, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.setAutoPressedColor, 6, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.darkSelectedIcon, 7, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.lightSelectedIcon, 7, 2, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.autoSelectedIcon, 7, 3, 1, 1, alignment=Qt.AlignCenter)

        self.resizeUI()

    def setColorBtnState(self, btn, colorText):
        btn.setText(colorText)
        if colorText != 'auto':
            btn.setStyleSheet(f'''
                                QPushButton{{background:{colorText};}}
                                QPushButton:pressed{{background:{colorText};font:9pt;}}
                                ''')

    def resizeUI(self):
        rate = self.app.screens()[QDesktopWidget().screenNumber(self)].logicalDotsPerInch()/96
        if rate < 1.1:
            rate = 1.0
        elif rate < 1.4:
            rate = 1.5
        elif rate < 1.8:
            rate = 1.75
        else:
            rate = 2
        x0 = int(rate * 150)
        x1 = int(rate * 70)
        y = int(rate * 40)
        self.editorThemeColor.setMinimumSize(x0, y)
        self.editorBorderColor.setMinimumSize(x0, y)
        self.editorPressedColor.setMinimumSize(x0, y)
        self.editorFgColor.setMinimumSize(x0, y)
        self.editorBgColor.setMinimumSize(x0, y)
        self.editorCheckedFontColor.setMinimumSize(x0, y)
        self.editorFontColor.setMinimumSize(x0, y)
        self.setAutoThemeColor.setMinimumSize(x1, y)
        self.setAutoBorderColor.setMinimumSize(x1, y)
        self.setAutoPressedColor.setMinimumSize(x1, y)
        self.setAutoFgColor.setMinimumSize(x1, y)
        self.setAutoBgColor.setMinimumSize(x1, y)
        self.setAutoCheckedFontColor.setMinimumSize(x1, y)
        self.setAutoFontColor.setMinimumSize(x1, y)
        self.darkSelectedIcon.setMinimumSize(x1, y)
        self.lightSelectedIcon.setMinimumSize(x1, y)
        self.autoSelectedIcon.setMinimumSize(x1, y)

    def selectedIconSet(self):
        #设定√符号的素材
        source = self.sender()
        if source == self.darkSelectedIcon:
            if self.darkSelectedIcon.isChecked():
                self.lightSelectedIcon.setChecked(False)
                self.autoSelectedIcon.setChecked(False)
                user_data.change('theme.selectedcolor', 'dark')
            else:
                self.darkSelectedIcon.setChecked(True)
        elif source == self.lightSelectedIcon:
            if self.lightSelectedIcon.isChecked():
                self.darkSelectedIcon.setChecked(False)
                self.autoSelectedIcon.setChecked(False)
                user_data.change('theme.selectedcolor', 'light')
            else:
                self.lightSelectedIcon.setChecked(True)
        else:
            if self.autoSelectedIcon.isChecked():
                self.lightSelectedIcon.setChecked(False)
                self.darkSelectedIcon.setChecked(False)
                user_data.change('theme.selectedcolor', 'auto')
            else:
                self.autoSelectedIcon.setChecked(True)
        #self.configUpdate.emit()

    def test(self):
        self.colorSelector.show()

    def chooseColor(self):
        #点下颜色设置按钮后保存来源并打开颜色选择器
        self.source = self.sender()
        if self.source.text() != 'auto':
            currentColor = QColor(self.source.text())
            self.colorSelector.setCurrentColor(currentColor)
            self.colorSelector.show()
        else:
            self.colorSelector.show()

    def setAuto(self):
        #设为自动
        source = self.sender()
        if source == self.setAutoFontColor:
            target = self.editorFontColor
            key = 'fontcolor'
        elif source == self.setAutoFgColor:
            target = self.editorFgColor
            key = 'fgcolor'
        elif source == self.setAutoBgColor:
            target = self.editorBgColor
            key = 'bgcolor'
        elif source == self.setAutoThemeColor:
            target = self.editorThemeColor
            key = 'themecolor'
        elif source == self.setAutoBorderColor:
            target = self.editorBorderColor
            key = 'bordercolor'
        elif source == self.setAutoCheckedFontColor:
            target = self.editorCheckedFontColor
            key = 'checkedfontcolor'
        elif source == self.setAutoPressedColor:
            target = self.editorPressedColor
            key = 'pressedcolor'
        target.setText('auto')
        target.setStyleSheet(f'''
                                QPushButton{{border:0px;background:{theme.getFgColor()};}}
                                QPushButton:pressed{{background:{theme.getPressedColor()};}}
                                ''')
        user_data.change(f'theme.{key}', 'auto')
        #self.configUpdate.emit()

    def colorOK(self):
        #点下确认后进行颜色处理
        color = self.colorSelector.currentColor().name(0)
        self.source.setText(color)
        if self.source == self.editorFontColor:
            key = 'fontcolor'
        elif self.source == self.editorFgColor:
            key = 'fgcolor'
        elif self.source == self.editorBgColor:
            key = 'bgcolor'
        elif self.source == self.editorThemeColor:
            key = 'themecolor'
        elif self.source == self.editorBorderColor:
            key = 'bordercolor'
        elif self.source == self.editorCheckedFontColor:
            key = 'checkedfontcolor'
        elif self.source == self.editorPressedColor:
            key = 'pressedcolor'
        self.source.setStyleSheet(f'''
                                QPushButton{{border:0px;background:{color};}}
                                QPushButton:pressed{{background:{color};}}
                                ''')
        user_data.change(f'theme.{key}', color)

