from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMenu, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget, QLineEdit, QColorDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor

class ThemeEditor(QWidget):
    configUpdate = pyqtSignal()
    def __init__(self, config, app, theme = None, ico = ''):
        super(ThemeEditor, self).__init__()

        self.config = config
        self.app = app
        self.theme = theme

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
        self.setColorBtnState(self.editorThemeColor, self.config.get('theme.themecolor'))
        self.editorThemeColor.clicked.connect(self.chooseColor)
        self.editorFontColor = QPushButton()
        self.setColorBtnState(self.editorFontColor, self.config.get('theme.fontcolor'))
        self.editorFontColor.clicked.connect(self.chooseColor)
        self.editorCheckedFontColor = QPushButton()
        self.setColorBtnState(self.editorCheckedFontColor, self.config.get('theme.checkedfontcolor'))
        self.editorCheckedFontColor.clicked.connect(self.chooseColor)
        self.editorBorderColor = QPushButton()
        self.setColorBtnState(self.editorBorderColor, self.config.get('theme.bordercolor'))
        self.editorBorderColor.clicked.connect(self.chooseColor)
        self.editorFgColor = QPushButton()
        self.setColorBtnState(self.editorFgColor, self.config.get('theme.fgcolor'))
        self.editorFgColor.clicked.connect(self.chooseColor)
        self.editorBgColor = QPushButton()
        self.setColorBtnState(self.editorBgColor, self.config.get('theme.bgcolor'))
        self.editorBgColor.clicked.connect(self.chooseColor)
        self.editorPressedColor = QPushButton()
        self.setColorBtnState(self.editorPressedColor, self.config.get('theme.pressedcolor'))
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
        selectedColor = self.config.get('theme.selectedcolor')
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
        self.editorThemeColor.setMinimumSize(rate * 150, rate * 40)
        self.editorBorderColor.setMinimumSize(rate * 150, rate * 40)
        self.editorPressedColor.setMinimumSize(rate * 150, rate * 40)
        self.editorFgColor.setMinimumSize(rate * 150, rate * 40)
        self.editorBgColor.setMinimumSize(rate * 150, rate * 40)
        self.editorCheckedFontColor.setMinimumSize(rate * 150, rate * 40)
        self.editorFontColor.setMinimumSize(rate * 150, rate * 40)
        self.setAutoThemeColor.setMinimumSize(rate * 70, rate * 40)
        self.setAutoBorderColor.setMinimumSize(rate * 70, rate * 40)
        self.setAutoPressedColor.setMinimumSize(rate * 70, rate * 40)
        self.setAutoFgColor.setMinimumSize(rate * 70, rate * 40)
        self.setAutoBgColor.setMinimumSize(rate * 70, rate * 40)
        self.setAutoCheckedFontColor.setMinimumSize(rate * 70, rate * 40)
        self.setAutoFontColor.setMinimumSize(rate * 70, rate * 40)
        self.darkSelectedIcon.setMinimumSize(rate * 70, rate * 40)
        self.lightSelectedIcon.setMinimumSize(rate * 70, rate * 40)
        self.autoSelectedIcon.setMinimumSize(rate * 70, rate * 40)

    def selectedIconSet(self):
        #设定√符号的素材
        source = self.sender()
        if source == self.darkSelectedIcon:
            if self.darkSelectedIcon.isChecked():
                self.lightSelectedIcon.setChecked(False)
                self.autoSelectedIcon.setChecked(False)
                self.config.change('theme.selectedcolor', 'dark')
            else:
                self.darkSelectedIcon.setChecked(True)
        elif source == self.lightSelectedIcon:
            if self.lightSelectedIcon.isChecked():
                self.darkSelectedIcon.setChecked(False)
                self.autoSelectedIcon.setChecked(False)
                self.config.change('theme.selectedcolor', 'light')
            else:
                self.lightSelectedIcon.setChecked(True)
        else:
            if self.autoSelectedIcon.isChecked():
                self.lightSelectedIcon.setChecked(False)
                self.darkSelectedIcon.setChecked(False)
                self.config.change('theme.selectedcolor', 'auto')
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
                                QPushButton{{border:0px;background:{self.theme.getFgColor()};}}
                                QPushButton:pressed{{background:{self.theme.getPressedColor()};}}
                                ''')
        self.config.change(f'theme.{key}', 'auto')
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
        self.config.change(f'theme.{key}', color)
        self.configUpdate.emit()

