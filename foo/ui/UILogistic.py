from PyQt5.QtWidgets import (QComboBox, QDesktopWidget,
                             QGridLayout, QLabel, QLineEdit,
                             QListView, QPushButton, QWidget, QTextBrowser)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from sys import path
from os import getcwd, startfile, path as osPath
from json import dumps

path.append(getcwd())
from foo.logisticDepartment import logistic, ruleEncoder
from foo.ui.screen import ScreenRateMonitor

class UILogistic(QWidget):
    configUpdate = pyqtSignal()
    def __init__(self, adb, rulePath, config, app, theme = None, ico = ''):
        super(UILogistic, self).__init__()
        self.app = app

        self.setWindowTitle('自动公招配置(默认配置由:七十七提供)')
        self.setWindowIcon(QIcon(ico))
        if theme != None:
            self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}
            QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;}}
            QTextBrowser{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
            QPushButton{{border:0px;background:{theme.getFgColor()};color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:11pt;}}
            QPushButton:pressed{{background:{theme.getPressedColor()};font:10pt;}}
            QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()};}}
            QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
            QLineEdit{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};
                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;border:0px;padding-left:5px}}
            QLineEdit:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};padding-left:4px;}}
            QListView{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
            QComboBox:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};padding-left:4px;}}
            QComboBox{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};
                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;padding-left:5px;border:0px;}}
            QComboBox:drop-down{{width:0px;}}
            QComboBox:down-arrow{{width:0px}}
            QComboBox:selected{{background-color:{theme.getPressedColor()};}}
            QComboBox:QAbstractItemView::item{{font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;}}
            QComboBox:QAbstractItemView::item:selected{{background-color:{theme.getPressedColor()};}}
            QInputDialog{{background-color:{theme.getBgColor()};}}
            QScrollBar:vertical{{width:8px;background:rgba(0,0,0,0%);margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}}
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

        self.comboBoxRuleNames = QComboBox()
        self.comboBoxRuleNames.setView(QListView())
        self.comboBoxRuleNames.activated.connect(self.selRule)

        self.editMoodThreshold = QLineEdit()
        self.editDormThreshold = QLineEdit()

        self.btnRefresh = QPushButton('刷新')
        self.btnRefresh.clicked.connect(self.refreshRule)

        self.btnEnableManufactory = QPushButton('制造站')
        self.btnEnableManufactory.setCheckable(True)
        self.btnEnableManufactory.clicked.connect(self.setEnableRoom)
        self.btnEnableTrade = QPushButton('贸易站')
        self.btnEnableTrade.setCheckable(True)
        self.btnEnableTrade.clicked.connect(self.setEnableRoom)
        self.btnEnablePowerRoom = QPushButton('发电站')
        self.btnEnablePowerRoom.setCheckable(True)
        self.btnEnablePowerRoom.clicked.connect(self.setEnableRoom)
        self.btnEnableReceptionRoom = QPushButton('会客室')
        self.btnEnableReceptionRoom.setCheckable(True)
        self.btnEnableReceptionRoom.clicked.connect(self.setEnableRoom)
        self.btnEnableOfficeRoom = QPushButton('办公室')
        self.btnEnableOfficeRoom.setCheckable(True)
        self.btnEnableOfficeRoom.clicked.connect(self.setEnableRoom)
        self.btnOpenRuleFolder = QPushButton('打开所在文件夹')
        self.btnOpenRuleFolder.clicked.connect(self.openRuleFileFolder)

        self.labelRooms = QLabel('启用的房间:')
        self.labelRuleInUseName = QLabel('当前使用规则:')
        self.labelMood = QLabel('撤下工作干员理智阈值:')
        self.labelDorm = QLabel('撤出宿舍干员理智阈值:')
        self.labelRuleFileName = QLabel('配置文件名称:logisticRule.ahrule')

        self.browserRule = QTextBrowser()

        self.grid = QGridLayout()

        self.grid.addWidget(self.labelRuleInUseName, 0, 0, 1, 2)
        self.grid.addWidget(self.btnRefresh, 0, 2)
        self.grid.addWidget(self.comboBoxRuleNames, 1, 0, 1, 3)
        self.grid.addWidget(self.browserRule, 2, 0, 1, 3)
        self.grid.addWidget(self.labelRooms, 3, 0)
        self.grid.addWidget(self.btnEnableManufactory, 4, 0)
        self.grid.addWidget(self.btnEnableTrade, 4, 1)
        self.grid.addWidget(self.btnEnableReceptionRoom, 3, 2)
        self.grid.addWidget(self.btnEnableOfficeRoom, 4, 2)
        self.grid.addWidget(self.btnEnablePowerRoom, 3, 1)
        self.grid.addWidget(self.labelMood, 5, 0, 1, 2)
        self.grid.addWidget(self.editMoodThreshold, 5, 2)
        self.grid.addWidget(self.labelDorm, 6, 0, 1, 2)
        self.grid.addWidget(self.editDormThreshold, 6, 2)
        self.grid.addWidget(self.labelRuleFileName, 7, 0, 1, 2)
        self.grid.addWidget(self.btnOpenRuleFolder, 7, 2)

        self.setLayout(self.grid)
        self.resizeUI()

        self.config = config
        self.rulePath = rulePath
        self.ruleEncoder = ruleEncoder.RuleEncoder(rulePath)
        self.logistic = logistic.Logistic(adb, self.config.get('logistic', 'defaultrule'), self.ruleEncoder,
                                          moodThreshold = int(self.config.get('logistic', 'moodThreshold')),
                                          dormThreshold = int(self.config.get('logistic', 'dormThreshold')))

        self.setDefaultState()

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
        self.btnRefresh.setMinimumSize(rate * 145, rate * 40)
        self.btnEnableManufactory.setMinimumSize(rate * 110, rate * 40)
        self.btnEnableTrade.setMinimumSize(rate * 110, rate * 40)
        self.btnEnablePowerRoom.setMinimumSize(rate * 110, rate * 40)
        self.btnEnableReceptionRoom.setMinimumSize(rate * 145, rate * 40)
        self.btnEnableOfficeRoom.setMinimumSize(rate * 145, rate * 40)
        self.comboBoxRuleNames.setMinimumHeight(rate * 40)
        self.editDormThreshold.setMinimumSize(rate * 145, rate * 40)
        self.editMoodThreshold.setMinimumSize(rate * 145, rate * 40)
        self.btnOpenRuleFolder.setMinimumSize(rate * 145, rate * 40)

    def setDefaultState(self):
        self.editDormThreshold.setText(self.config.get('logistic', 'dormthreshold'))
        self.editMoodThreshold.setText(self.config.get('logistic', 'moodthreshold'))
        self.btnEnableManufactory.setChecked(self.config.getboolean('logistic', 'manufactory'))
        self.btnEnableTrade.setChecked(self.config.getboolean('logistic', 'trade'))
        self.btnEnablePowerRoom.setChecked(self.config.getboolean('logistic', 'powerroom'))
        self.btnEnableOfficeRoom.setChecked(self.config.getboolean('logistic', 'officeroom'))
        self.btnEnableReceptionRoom.setChecked(self.config.getboolean('logistic', 'receptionroom'))

        self.ruleRelateRefresh()
        self.logistic.setEnableRooms(self.getEnableRooms())

    def openRuleFileFolder(self):
        startfile(osPath.dirname(self.rulePath))

    def refreshRule(self):
        self.ruleEncoder.reloadRule()
        self.ruleRelateRefresh()

    def ruleRelateRefresh(self):
        '刷新与规则有关的所有内容，包括规则下拉框、规则预览'
        self.comboBoxRuleNames.clear()
        self.comboBoxRuleNames.addItems(self.ruleEncoder.getAllRulesName())

        defaultName = self.config.get('logistic', 'defaultrule')
        allRuleNames = self.ruleEncoder.getAllRulesName()
        if defaultName in allRuleNames:
            self.comboBoxRuleNames.setCurrentIndex(allRuleNames.index(defaultName))
        oneRule = self.ruleEncoder.getOneRule(self.comboBoxRuleNames.currentText())
        if isinstance(oneRule, dict):
            oneRule = dumps(oneRule, sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False)
        self.browserRule.setText(oneRule)
        self.logistic.setRuleName(self.comboBoxRuleNames.currentText())

    def selRule(self):
        self.logistic.setRuleName(self.comboBoxRuleNames.currentText())
        self.config.set('logistic', 'defaultrule', self.comboBoxRuleNames.currentText())
        self.ruleRelateRefresh()

    def setEnableRoom(self, isChecked):
        source = self.sender()
        isChecked = str(isChecked)
        if source == self.btnEnableManufactory:
            self.config.set('logistic', 'manufactory', isChecked)
        elif source == self.btnEnableTrade:
            self.config.set('logistic', 'trade', isChecked)
        elif source == self.btnEnablePowerRoom:
            self.config.set('logistic', 'powerroom', isChecked)
        elif source == self.btnEnableOfficeRoom:
            self.config.set('logistic', 'officeroom', isChecked)
        elif source == self.btnEnableReceptionRoom:
            self.config.set('logistic', 'receptionroom', isChecked)
        
        self.logistic.setEnableRooms(self.getEnableRooms())

    def getEnableRooms(self):
        rooms = []
        if self.btnEnableManufactory.isChecked():
            rooms.append('制造站')
        if self.btnEnableTrade.isChecked():
            rooms.append('贸易站')
        if self.btnEnablePowerRoom.isChecked():
            rooms.append('发电站')
        if self.btnEnableOfficeRoom.isChecked():
            rooms.append('办公室')
        if self.btnEnableReceptionRoom.isChecked():
            rooms.append('会客室')
        return rooms

    def run(self, flag):
        self.logistic.run(flag)

    def stop(self):
        self.logistic.stop()

    def closeEvent(self, event):
        if self.editDormThreshold.text().isnumeric():
            self.logistic.setDormThreshold(int(self.editDormThreshold.text()))
            self.config.set('logistic', 'dormthreshold', self.editDormThreshold.text())
        if self.editMoodThreshold.text().isnumeric():
            self.logistic.setMoodThreshold(int(self.editMoodThreshold.text()))
            self.config.set('logistic', 'moodthreshold', self.editMoodThreshold.text())
            
        self.configUpdate.emit()
        event.accept()
        
