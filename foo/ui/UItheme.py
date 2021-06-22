from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMenu, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class ThemeEditor(QWidget):
    configUpdate = pyqtSignal()
    def __init__(self, config, app, theme = None, ico = ''):
        super(ThemeEditor, self).__init__()

        self.config = config
        self.app = app
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


        self.setWindowTitle('颜色格式#rrggbb(自动:auto)')
        self.setWindowIcon(QIcon(ico))
        self.labelThemeColor = QLabel('打开的开关的颜色')
        self.labelFontColor = QLabel('字体颜色')
        self.labelCheckedFontColor = QLabel('打开的开关的字体颜色')
        self.labelBorderColor = QLabel('按钮悬停时边框颜色')
        self.labelFgColor = QLabel('前景色')
        self.labelBgColor = QLabel('背景色')
        self.labelPressedColor = QLabel('按下按钮时的颜色')
        self.labelSelectedColor = QLabel('√的颜色')

        self.saveThemeColor = QPushButton('保存')
        self.saveFontColor = QPushButton('保存')
        self.saveCheckedFontColor = QPushButton('保存')
        self.saveBorderColor = QPushButton('保存')
        self.saveFgColor = QPushButton('保存')
        self.saveBgColor = QPushButton('保存')
        self.savePressedColor = QPushButton('保存')

        self.editorThemeColor = QLineEdit()
        self.editorThemeColor.setText(self.config.get('theme', 'themecolor'))
        self.editorThemeColor.setAlignment(Qt.AlignHCenter)
        self.editorFontColor = QLineEdit()
        self.editorFontColor.setText(self.config.get('theme', 'fontcolor'))
        self.editorFontColor.setAlignment(Qt.AlignHCenter)
        self.editorCheckedFontColor = QLineEdit()
        self.editorCheckedFontColor.setText(self.config.get('theme', 'checkedfontcolor'))
        self.editorCheckedFontColor.setAlignment(Qt.AlignHCenter)
        self.editorBorderColor = QLineEdit()
        self.editorBorderColor.setText(self.config.get('theme', 'bordercolor'))
        self.editorBorderColor.setAlignment(Qt.AlignHCenter)
        self.editorFgColor = QLineEdit()
        self.editorFgColor.setText(self.config.get('theme', 'fgcolor'))
        self.editorFgColor.setAlignment(Qt.AlignHCenter)
        self.editorBgColor = QLineEdit()
        self.editorBgColor.setText(self.config.get('theme', 'bgcolor'))
        self.editorBgColor.setAlignment(Qt.AlignHCenter)
        self.editorPressedColor = QLineEdit()
        self.editorPressedColor.setText(self.config.get('theme', 'pressedcolor'))
        self.editorPressedColor.setAlignment(Qt.AlignHCenter)
        
        self.darkSelectedIcon = QPushButton('深色')
        self.darkSelectedIcon.setCheckable(True)
        self.darkSelectedIcon.clicked.connect(self.selectedIconSet)
        self.lightSelectedIcon = QPushButton('浅色')
        self.lightSelectedIcon.setCheckable(True)
        self.lightSelectedIcon.clicked.connect(self.selectedIconSet)
        self.autoSelectedIcon = QPushButton('自动')
        self.autoSelectedIcon.setCheckable(True)
        self.autoSelectedIcon.clicked.connect(self.selectedIconSet)
        selectedColor = self.config.get('theme', 'selectedcolor')
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
        self.grid.addWidget(self.saveThemeColor, 0, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.saveCheckedFontColor, 1, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.saveFgColor, 2, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.saveBgColor, 3, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.saveFontColor, 4, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.saveBorderColor, 5, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.savePressedColor, 6, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.darkSelectedIcon, 7, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.lightSelectedIcon, 7, 2, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.autoSelectedIcon, 7, 3, 1, 1, alignment=Qt.AlignCenter)

        self.resizeUI()

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
        self.saveThemeColor.setMinimumSize(rate * 70, rate * 40)
        self.saveBorderColor.setMinimumSize(rate * 70, rate * 40)
        self.savePressedColor.setMinimumSize(rate * 70, rate * 40)
        self.saveFgColor.setMinimumSize(rate * 70, rate * 40)
        self.saveBgColor.setMinimumSize(rate * 70, rate * 40)
        self.saveCheckedFontColor.setMinimumSize(rate * 70, rate * 40)
        self.saveFontColor.setMinimumSize(rate * 70, rate * 40)
        self.darkSelectedIcon.setMinimumSize(rate * 70, rate * 40)
        self.lightSelectedIcon.setMinimumSize(rate * 70, rate * 40)
        self.autoSelectedIcon.setMinimumSize(rate * 70, rate * 40)

    def selectedIconSet(self):
        source = self.sender()
        if source == self.darkSelectedIcon:
            if self.darkSelectedIcon.isChecked():
                self.lightSelectedIcon.setChecked(False)
                self.autoSelectedIcon.setChecked(False)
                self.config.set('theme', 'selectedcolor', 'dark')
            else:
                self.darkSelectedIcon.setChecked(True)
        elif source == self.lightSelectedIcon:
            if self.lightSelectedIcon.isChecked():
                self.darkSelectedIcon.setChecked(False)
                self.autoSelectedIcon.setChecked(False)
                self.config.set('theme', 'selectedcolor', 'light')
            else:
                self.lightSelectedIcon.setChecked(True)
        else:
            if self.autoSelectedIcon.isChecked():
                self.lightSelectedIcon.setChecked(False)
                self.darkSelectedIcon.setChecked(False)
                self.config.set('theme', 'selectedcolor', 'auto')
            else:
                self.autoSelectedIcon.setChecked(True)
        self.configUpdate.emit()
