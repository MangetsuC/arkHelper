from PySide6.QtWidgets import (QComboBox, #QDesktopWidget,
                             QGridLayout, QLabel, QLineEdit,
                             QListView, QPushButton, QWidget, QTextBrowser)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from sys import path
from os import getcwd, startfile, path as osPath
from json import dumps

path.append(getcwd())
from foo.logisticDepartment import Logistic, ruleEncoder
from foo.ui.screen import ScreenRateMonitor
from common import user_data, theme

class UILogistic(QWidget):
    configUpdate = Signal()
    def __init__(self,  rulePath, app, ico = ''):
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

        self.label_meetingRoom_send = QLabel('赠送全部多余的线索:')
        self.btn_meetingRoom_send = QPushButton('')
        self.btn_meetingRoom_send.setCheckable(True)
        self.btn_meetingRoom_send.clicked.connect(self.meetingRoom_function_change)

        self.label_meetingRoom_use = QLabel('自动开启线索交流:')
        self.btn_meetingRoom_use = QPushButton('')
        self.btn_meetingRoom_use.setCheckable(True)
        self.btn_meetingRoom_use.clicked.connect(self.meetingRoom_function_change)

        self.label_meetingRoom_daily = QLabel('自动领取每日线索:')
        self.btn_meetingRoom_daily = QPushButton('')
        self.btn_meetingRoom_daily.setCheckable(True)
        self.btn_meetingRoom_daily.clicked.connect(self.meetingRoom_function_change)

        self.meetingRoom_function_ui_refresh()

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
        self.grid.addWidget(self.label_meetingRoom_send, 5, 0, 1, 2)
        self.grid.addWidget(self.btn_meetingRoom_send, 5, 2)
        self.grid.addWidget(self.label_meetingRoom_use, 6, 0, 1, 2)
        self.grid.addWidget(self.btn_meetingRoom_use, 6, 2)
        self.grid.addWidget(self.label_meetingRoom_daily, 7, 0, 1, 2)
        self.grid.addWidget(self.btn_meetingRoom_daily, 7, 2)
        self.grid.addWidget(self.labelMood, 8, 0, 1, 2)
        self.grid.addWidget(self.editMoodThreshold, 8, 2)
        self.grid.addWidget(self.labelDorm, 9, 0, 1, 2)
        self.grid.addWidget(self.editDormThreshold, 9, 2)
        self.grid.addWidget(self.labelRuleFileName, 10, 0, 1, 2)
        self.grid.addWidget(self.btnOpenRuleFolder, 10, 2)

        self.setLayout(self.grid)
        self.resizeUI()

        self.config = user_data
        self.rulePath = rulePath
        self.ruleEncoder = ruleEncoder.RuleEncoder(rulePath)
        self.logistic = Logistic.Logistic(self.config.get('logistic.rule'), self.ruleEncoder,
                                          moodThreshold = int(self.config.get('logistic.threshold.work')),
                                          dormThreshold = int(self.config.get('logistic.threshold.dorm')))

        self.setDefaultState()

    def resizeUI(self):
        rate = 1#self.app.screens()[QDesktopWidget().screenNumber(self)].logicalDotsPerInch()/96
        if rate < 1.1:
            rate = 1.0
        elif rate < 1.4:
            rate = 1.5
        elif rate < 1.8:
            rate = 1.75
        else:
            rate = 2
        x0 = int(rate * 145)
        x1 = int(rate * 110)
        y = int(rate * 40)

        self.btnRefresh.setMinimumSize(x0, y)
        self.btnEnableManufactory.setMinimumSize(x1, y)
        self.btnEnableTrade.setMinimumSize(x1, y)
        self.btnEnablePowerRoom.setMinimumSize(x1, y)
        self.btnEnableReceptionRoom.setMinimumSize(x0, y)
        self.btnEnableOfficeRoom.setMinimumSize(x0, y)
        self.comboBoxRuleNames.setMinimumHeight(y)
        self.editDormThreshold.setMinimumSize(x0, y)
        self.editMoodThreshold.setMinimumSize(x0, y)
        self.btn_meetingRoom_use.setMinimumSize(x0, y)
        self.btn_meetingRoom_daily.setMinimumSize(x0, y)
        self.btn_meetingRoom_send.setMinimumSize(x0, y)
        self.btnOpenRuleFolder.setMinimumSize(x0, y)

    def meetingRoom_function_ui_refresh(self):
        if user_data.get('logistic.meetingroom.send'):
            self.btn_meetingRoom_send.setChecked(True)
            self.btn_meetingRoom_send.setText('点击关闭')
        else:
            self.btn_meetingRoom_send.setChecked(False)
            self.btn_meetingRoom_send.setText('点击开启')
        if user_data.get('logistic.meetingroom.use'):
            self.btn_meetingRoom_use.setChecked(True)
            self.btn_meetingRoom_use.setText('点击关闭')
        else:
            self.btn_meetingRoom_use.setChecked(False)
            self.btn_meetingRoom_use.setText('点击开启')
        if user_data.get('logistic.meetingroom.daily'):
            self.btn_meetingRoom_daily.setChecked(True)
            self.btn_meetingRoom_daily.setText('点击关闭')
        else:
            self.btn_meetingRoom_daily.setChecked(False)
            self.btn_meetingRoom_daily.setText('点击开启')

    def meetingRoom_function_change(self, isChecked):
        sender = self.sender()
        if sender == self.btn_meetingRoom_send:
            user_data.change('logistic.meetingroom.send', isChecked)
        elif sender == self.btn_meetingRoom_use:
            user_data.change('logistic.meetingroom.use', isChecked)
        elif sender == self.btn_meetingRoom_daily:
            user_data.change('logistic.meetingroom.daily', isChecked)
        self.meetingRoom_function_ui_refresh()

    def setDefaultState(self):
        self.editDormThreshold.setText(str(self.config.get('logistic.threshold.dorm')))
        self.editMoodThreshold.setText(str(self.config.get('logistic.threshold.work')))
        self.btnEnableManufactory.setChecked(self.config.get('logistic.manufactory.enable'))
        self.btnEnableTrade.setChecked(self.config.get('logistic.trade.enable'))
        self.btnEnablePowerRoom.setChecked(self.config.get('logistic.powerroom.enable'))
        self.btnEnableOfficeRoom.setChecked(self.config.get('logistic.officeroom.enable'))
        self.btnEnableReceptionRoom.setChecked(self.config.get('logistic.meetingroom.enable'))

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

        defaultName = self.config.get('logistic.rule')
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
        self.config.change('logistic.rule', self.comboBoxRuleNames.currentText())
        self.ruleRelateRefresh()

    def setEnableRoom(self, isChecked):
        source = self.sender()
        #isChecked = str(isChecked)
        if source == self.btnEnableManufactory:
            self.config.change('logistic.manufactory.enable', isChecked)
        elif source == self.btnEnableTrade:
            self.config.change('logistic.trade.enable', isChecked)
        elif source == self.btnEnablePowerRoom:
            self.config.change('logistic.powerroom.enable', isChecked)
        elif source == self.btnEnableOfficeRoom:
            self.config.change('logistic.officeroom.enable', isChecked)
        elif source == self.btnEnableReceptionRoom:
            self.config.change('logistic.meetingroom.enable', isChecked)
        
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
            self.config.change('logistic.threshold.dorm', int(self.editDormThreshold.text()))
        if self.editMoodThreshold.text().isnumeric():
            self.logistic.setMoodThreshold(int(self.editMoodThreshold.text()))
            self.config.change('logistic.threshold.work', int(self.editMoodThreshold.text()))
        event.accept()
        
