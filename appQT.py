import cgitb
import sys
from json import dumps, loads
from os import getcwd, getlogin, mkdir, path, startfile
from threading import Thread
from webbrowser import open as openUrl

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMenu, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)

from foo.adb.adbCtrl import Cmd
from foo.arknight.Battle import BattleLoop
from foo.arknight.credit import Credit
from foo.arknight.Schedule import BattleSchedule
from foo.arknight.task import Task
from foo.pictureR import pictureFind
from foo.ui.console import Console
from foo.ui.launch import AfterInit, BlackBoard, Launch
from foo.ui.screen import Screen, ScreenRateMonitor
from foo.ui.UItheme import ThemeEditor
from foo.ui.UILogistic import UILogistic
from foo.ui.UIPublicCall import UIPublicCall
from foo.ui.UIschedule import JsonEdit
from foo.ui.messageBox import AMessageBox
from foo.win.exitThread import forceThreadStop
from common import user_data, simulator_data, config_path, theme
from common2 import adb


class App(QWidget):
    exitBeforeShutdown = pyqtSignal()
    startBtnPressed = pyqtSignal(str)
    def __init__(self, app):
        super(App, self).__init__()
        self.app = app

        self.cwd = getcwd().replace('\\', '/')
        self.ver = Cmd(self.cwd).getVersion() #获取版本号

        self.console = Console(self.cwd, self.ver)  # 接管输出与报错
        self.console.adbCloseError.connect(self.adbClosedHandle)

        #获取整块屏幕的尺寸
        self.totalWidth = 0
        self.totalHeight = 0
        tempScreenList = []
        for i in range(QDesktopWidget().screenCount()):
            tempScreenList.append(QDesktopWidget().availableGeometry(i))
        self.screen = Screen(tempScreenList)

        self.initVar()
        self.initNormalPicRes()
        self.initUI()
        self.initClass()
        self.initRightClickMeun()
        self.initState()
        self.applyStyleSheet()

        self.exitBeforeShutdown.connect(self.exit)
        self.startBtnPressed.connect(self.btnStartAndStop.setText)

        self.isRun = False
        self.center()
        self.show()

    def getRealSize(self, size):
        rate = self.app.screens()[QDesktopWidget().screenNumber(self)].logicalDotsPerInch()/96
        if rate < 1.1:
            rate = 1.0
        elif rate < 1.4:
            rate = 1.5
        elif rate < 1.8:
            rate = 1.75
        else:
            rate = 2
        
        return int(size * rate)
    
    def resizeUI(self, windowChangedScreen):
        if windowChangedScreen == self:
            self.setMaximumSize(self.getRealSize(420), self.getRealSize(150))
            self.btnExit.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
            self.btnMinimize.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
            self.btnSetting.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
            self.btnUpdate.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
            self.btnStartAndStop.setMinimumSize(self.getRealSize(180), self.getRealSize(131))
            self.tbLogistic.setMinimumSize(self.getRealSize(155), self.getRealSize(40))
            self.tbBattle.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
            self.tbSchedule.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
            self.tbAutoPC.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
            self.tbTask.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
            self.tbCredit.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
            self.tbShutdown.setMinimumSize(self.getRealSize(155), self.getRealSize(40))

    def initUI(self): 
        self.theme = theme #在UI初始化前加载主题

        self.setWindowIcon(QIcon(self.ico))
        self.setWindowTitle('明日方舟小助手')

        self.resize(self.getRealSize(420), self.getRealSize(150))

        self.line = QAction()
        self.line.setSeparator(True)

        self.setWindowFlag(Qt.FramelessWindowHint) #隐藏边框

        self.rightClickMenu = QMenu()#右键菜单

        self.lTitle = QLabel('明日方舟小助手')
        
        self.lVer = QLabel(f'v{self.ver}')
        

        self.btnExit = QPushButton('×',self)
        self.btnExit.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
        
        self.btnExit.clicked.connect(self.exit)
        self.btnExit.setToolTip('关闭')

        self.btnMinimize = QPushButton('-',self)
        self.btnMinimize.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
        
        self.btnMinimize.clicked.connect(self.minimize)
        self.btnMinimize.setToolTip('最小化')

        self.btnSetting = QPushButton('≡',self)
        self.btnSetting.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
        
        self.btnSetting.setToolTip('设置')

        self.btnUpdate = QPushButton('∧',self)
        self.btnUpdate.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
        
        self.btnUpdate.clicked.connect(self.startUpdate)
        self.btnUpdate.setToolTip('自动更新')
        self.btnUpdate.hide()

        self.btnShowMsg = QPushButton('!',self)
        self.btnShowMsg.setMinimumSize(self.getRealSize(30), self.getRealSize(30))
        
        self.btnShowMsg.clicked.connect(self.showMessage)
        self.btnShowMsg.setToolTip('查看公告')
        self.btnShowMsg.hide()

        self.btnStartAndStop = QPushButton('启动虚拟博士', self) #启动/停止按钮
        self.btnStartAndStop.setMinimumSize(self.getRealSize(180), self.getRealSize(131))
        
        self.btnStartAndStop.clicked.connect(self.clickBtnStartAndStop)

        self.tbBattle = QPushButton('战斗:无限', self) #战斗可选按钮
        self.tbBattle.setCheckable(True)
        self.tbBattle.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
        self.tbBattle.clicked[bool].connect(self.functionSel)
        self.tbBattle.setToolTip('从你目前处在的关卡开始循环作战，直到理智不足')

        self.actBattleTimes = QAction('设定次数(当前：无限)')
        self.actBattleTimes.triggered.connect(self.setLoopBattleTimes)

        self.tbSchedule = QPushButton('计划战斗', self) #计划战斗可选按钮
        self.tbSchedule.setCheckable(True)
        self.tbSchedule.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
        self.tbSchedule.clicked[bool].connect(self.functionSel)
        self.tbSchedule.setToolTip('在右键菜单中设定你的计划，会按照设定的计划作战')

        self.tbAutoPC = QPushButton('自动公招', self) #自动公招可选按钮
        self.tbAutoPC.setCheckable(True)
        self.tbAutoPC.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
        self.tbAutoPC.clicked[bool].connect(self.functionSel)
        self.tbAutoPC.setToolTip('自动进行公开招募，在右键菜单中进行配置')

        self.actAutoSearch = QAction('自动招募')
        self.actAutoSearch.triggered.connect(self.setAutoPCFunc)
        self.actAutoSearch.setIcon(QIcon(self.theme.getSelectedIcon()))
        self.actAutoEmploy = QAction('自动聘用')
        self.actAutoEmploy.triggered.connect(self.setAutoPCFunc)
        self.actAutoEmploy.setIcon(QIcon(self.theme.getSelectedIcon()))
        self.actSkipStar23 = QAction('跳过3星及以下')
        self.actSkipStar23.triggered.connect(self.setAutoPCFunc)
        if user_data.get('function.autopc.skip23star'):
            self.actSkipStar23.setIcon(QIcon(self.theme.getSelectedIcon()))
        self.actSkipStar1 = QAction('保留1星')
        self.actSkipStar1.triggered.connect(self.setAutoPCFunc)
        if user_data.get('function.autopc.skip1star'):
            self.actSkipStar1.setIcon(QIcon(self.theme.getSelectedIcon()))
        self.actSkipStar5 = QAction('保留5星')
        self.actSkipStar5.triggered.connect(self.setAutoPCFunc)
        if user_data.get('function.autopc.skip5star'):
            self.actSkipStar5.setIcon(QIcon(self.theme.getSelectedIcon()))
        self.actPcCalculate = QAction('公招计算器')
        self.actPcCalculate.triggered.connect(self.monitorPC)
        self.pcCalculateChecked = False

        self.actSchJson = QAction('路线规划')
        self.actSchJson.triggered.connect(self.openSchEdit)

        self.tbTask = QPushButton('任务交付', self) #任务交付可选按钮
        self.tbTask.setCheckable(True)
        self.tbTask.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
        self.tbTask.clicked[bool].connect(self.functionSel)
        self.tbTask.setToolTip('自动交付任务')

        self.tbCredit = QPushButton('获取信用', self)
        self.tbCredit.setCheckable(True)
        self.tbCredit.setMinimumSize(self.getRealSize(75), self.getRealSize(40))
        self.tbCredit.clicked[bool].connect(self.functionSel)
        self.tbCredit.setToolTip('自动拜访好友的基建以获取信用点')

        self.tbLogistic = QPushButton('自动基建', self) #战斗可选按钮
        self.tbLogistic.setCheckable(True)
        self.tbLogistic.setMinimumSize(self.getRealSize(155), self.getRealSize(40))
        self.tbLogistic.clicked[bool].connect(self.functionSel)
        self.tbLogistic.setToolTip('自动进行基建操作，右键以配置')

        self.actLogisticConfig = QAction('配置自动基建')

        self.tbShutdown = QPushButton('完成后关机', self)
        self.tbShutdown.setCheckable(True)
        self.tbShutdown.setMinimumSize(self.getRealSize(155), self.getRealSize(40))
        self.tbShutdown.clicked[bool].connect(self.functionSel)

        #self.btnSet = QPushButton('设置',self) #设置按钮
        #self.btnSet.setFixedSize(75, 40)

        self.settingMenu = QMenu() #创建设置按钮菜单
        
        self.actSimulator = QMenu('模拟器', parent=self.settingMenu) #模拟器二级菜单
        self.actSimulator_del = QMenu('删除', parent=self.actSimulator) #删除模拟器三级菜单
        self.simulators = []
        self.simulator_choices()

        self.actRecovery = QMenu('额外理智', parent=self.settingMenu)
        self.actMedicament = QMenu('理智顶液', parent=self.actRecovery)
        self.actAtuoMedicament = QAction('自动使用（普通）', parent=self.actMedicament)
        self.actAtuoMedicament.triggered.connect(self.changeRecStateMedLoop)
        self.actAtuoMedicamentSch = QAction('自动使用（计划）', parent=self.actMedicament)
        self.actAtuoMedicamentSch.triggered.connect(self.changeRecStateMedSche)
        self.actStone = QMenu('源石', parent=self.actRecovery)
        self.actAutoStone = QAction('自动使用（普通）', self.actStone)
        self.actAutoStone.triggered.connect(self.changeRecStateStoneLoop)
        self.actAutoStoneSche = QAction('自动使用（计划）', self.actStone)
        self.actAutoStoneSche.triggered.connect(self.changeRecStateStoneSche)
        self.actMaxNumber = QAction('设置上限', self.actStone)
        self.actMaxNumber.triggered.connect(self.changeMaxNum)

        self.actTheme = QAction('主题设置', parent=self.settingMenu)
        self.actConsole = QAction('控制台', parent=self.settingMenu)
        self.actCheckUpdate = QAction('前往下载', parent=self.settingMenu)
        self.actIndex = QAction('访问主页', parent=self.settingMenu)
        
        self.actVersion2 = QAction(f'v{self.ver}', parent=self.settingMenu)

        self.settingMenu.addMenu(self.actSimulator) #模拟器二级菜单
        '''self.slrList = [self.actSlrBlueStacks, self.actSlrMumu, self.actSlrXiaoyao, self.actSlrYeshen, self.actSlrLeidian, self.actSlrCustom]
        #添加菜单选项
        
        for eachSlr in self.slrList:
            self.actSimulator.addAction(eachSlr)'''

        self.settingMenu.addMenu(self.actRecovery)
        self.actRecovery.addMenu(self.actMedicament)
        self.actRecovery.addMenu(self.actStone)
        self.actMedicament.addAction(self.actAtuoMedicament)
        self.actMedicament.addAction(self.actAtuoMedicamentSch)
        self.actStone.addAction(self.actAutoStone)
        self.actStone.addAction(self.actAutoStoneSche)
        self.actStone.addAction(self.actMaxNumber)

        self.settingMenu.addAction(self.actConsole) #控制台
        self.actConsole.triggered.connect(self.console.showOrHide)

        self.settingMenu.addAction(self.actTheme) 
        self.actTheme.triggered.connect(self.openThemeEditor)

        self.settingMenu.addAction(self.actCheckUpdate) #蓝奏云地址
        self.actCheckUpdate.triggered.connect(self.openUpdate)

        self.settingMenu.addAction(self.actIndex) #主页
        self.actIndex.triggered.connect(self.openIndex)

        self.settingMenu.addAction(self.actVersion2) #版本号显示
        self.actVersion2.triggered.connect(self.testUpdate)

        self.btnSetting.setMenu(self.settingMenu)
        
        self.topLayout = QVBoxLayout(self)

        self.HBox = QHBoxLayout()
        self.HBox.addWidget(self.lTitle)
        self.HBox.addWidget(self.lVer)
        self.HBox.addStretch(1)
        self.HBox.addWidget(self.btnShowMsg)
        self.HBox.addWidget(self.btnUpdate)
        self.HBox.addWidget(self.btnSetting)
        self.HBox.addWidget(self.btnMinimize)
        self.HBox.addWidget(self.btnExit)

        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(5)
        self.grid.setHorizontalSpacing(5)
        
        self.grid.addWidget(self.btnStartAndStop, 0, 0, 3, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbLogistic, 1, 1, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbBattle, 0, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbSchedule, 2, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbAutoPC, 1, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbTask, 0, 2, 1, 1, alignment=Qt.AlignCenter)
        #self.grid.addWidget(self.btnSet, 2, 1, 1,1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbCredit, 0, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbShutdown, 2, 2, 1, 2)
        #self.grid.addWidget(self.btnMin, 2, 2, 1, 2, alignment=Qt.AlignCenter)
        #self.grid.addWidget(self.btnClose, 1, 4, 2, 1, alignment=Qt.AlignCenter)
        #self.grid.addWidget(self.btnShowBoard, 3, 1, 1, 1, alignment=Qt.AlignCenter)
        #self.grid.addWidget(self.btnUpdateLeft, 3, 1, 1, 1, alignment=Qt.AlignCenter)
        #self.grid.addWidget(self.btnUpdateRight, 3, 2, 1, 1, alignment=Qt.AlignCenter)
        #self.grid.addWidget(self.lNotice, 3, 3, 1, 2, alignment=Qt.AlignRight)

        self.topLayout.addLayout(self.HBox)
        self.topLayout.addLayout(self.grid)

        #self.show()

    def applyStyleSheet(self):
        self.setStyleSheet(f'''QWidget{{background:{self.theme.getBgColor()}}}
                                QLabel{{color:{self.theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:9pt;}}
                                QPushButton{{border:0px;background:{self.theme.getFgColor()};
                                color:{self.theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{self.theme.getBorderColor()};}}
                                QPushButton:pressed{{background:{self.theme.getPressedColor()};font:9pt;}}
                                QPushButton:checked{{background:{self.theme.getThemeColor()};color:{self.theme.getCheckedFontColor()}}}
                                QInputDialog{{background-color:{self.theme.getBgColor()};}}
                                QLineEdit{{color:{self.theme.getFontColor()};}}
                                QMessageBox{{background-color:{self.theme.getFgColor()};}}
                                QToolTip {{font-family:"Microsoft YaHei", SimHei, SimSun; font-size:10pt; 
                                        color:{self.theme.getFontColor()};
                                        padding:5px;
                                        border-style:solid; border-width:1px; border-color:gray;
                                        background-color:{self.theme.getBgColor()};}}
                            ''')
        self.lTitle.setStyleSheet(f'''
                                    QLabel{{color:{self.theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')
        self.lVer.setStyleSheet(f'''
                                    QLabel{{color:{self.theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')
        self.btnExit.setStyleSheet(f'''QPushButton{{background:{self.theme.getBgColor()};font-family:SimHei, SimSun;font:20pt;}}
                                            QPushButton:pressed{{background:{self.theme.getBgColor()};font:16pt;}}
                                            ''')
        self.btnMinimize.setStyleSheet(f'''QPushButton{{background:{self.theme.getBgColor()};font-family:SimSun;font:normal 28pt;}}
                                            QPushButton:pressed{{background:{self.theme.getBgColor()};
                                            font-family:SimSun;font:20pt;}}
                                            ''')
        self.btnSetting.setStyleSheet(f'''QPushButton{{background:{self.theme.getBgColor()};font-family:SimHei, SimSun;font:16pt;}}
                                            QPushButton:pressed{{background:{self.theme.getBgColor()};
                                            font-family:SimHei, SimSun;font:14pt;}}
                                            QPushButton:menu-indicator{{image:none;width:0px;}}
                                            ''')
        self.btnUpdate.setStyleSheet(f'''QPushButton{{background:{self.theme.getBgColor()};font-family:SimHei, SimSun;font:14pt;}}
                                            QPushButton:pressed{{background:{self.theme.getBgColor()};
                                            font-family:SimHei, SimSun;font:12pt;}}
                                            ''')
        self.btnShowMsg.setStyleSheet(f'''QPushButton{{background:{self.theme.getBgColor()};font-family:SimHei, SimSun;font:14pt;}}
                                            QPushButton:pressed{{background:{self.theme.getBgColor()};
                                            font-family:SimHei, SimSun;font:12pt;}}
                                            ''')
        self.btnStartAndStop.setStyleSheet('''QPushButton{font:13pt;}''')
        self.settingMenu.setStyleSheet(f'''QMenu {{color:{self.theme.getFontColor()};
                                                font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                                background-color:{self.theme.getBgColor()}; margin:3px;}}
                                                QMenu:item {{padding:8px 32px;}}
                                                QMenu:item:selected {{background-color: {self.theme.getFgColor()};}}
                                                QMenu:icon{{padding: 8px 20px;}}
                                                QMenu:separator{{background-color: {self.theme.getFontColor()}; 
                                                        height:1px; margin-left:2px; margin-right:2px;}}''')
        self.rightClickMenu.setStyleSheet(f'''QMenu {{color:{self.theme.getFontColor()};
                                                    font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                                    background-color:{self.theme.getBgColor()}; margin:3px;}}
                                                QMenu:item {{padding:8px 32px;}}
                                                QMenu:item:selected {{ background-color: {self.theme.getFgColor()};}}
                                                QMenu:icon{{padding: 8px 20px;}}
                                                QMenu:separator{{background-color: {self.theme.getFontColor()}; 
                                                    height:1px; margin-left:2px; margin-right:2px;}}''')

        #self.console.applyStyleSheet(self.theme)

    def initRightClickMeun(self):
        #战斗按钮
        self.tbBattle.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbBattle.customContextMenuRequested.connect(self.functionSetMeun)
        #计划战斗按钮
        self.tbSchedule.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbSchedule.customContextMenuRequested.connect(self.functionSetMeun)
        #自动公招按钮
        self.tbAutoPC.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbAutoPC.customContextMenuRequested.connect(self.functionSetMeun)
        #任务按钮
        self.tbTask.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbTask.customContextMenuRequested.connect(self.functionSetMeun)
        #信用按钮
        self.tbCredit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbCredit.customContextMenuRequested.connect(self.functionSetMeun)
        #自动关机按钮
        self.tbShutdown.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbShutdown.customContextMenuRequested.connect(self.functionSetMeun)
        #公开招募按钮
        #self.btnMonitorPublicCall.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.btnMonitorPublicCall.customContextMenuRequested.connect(self.functionSetMeun)
        #自动基建
        self.tbLogistic.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbLogistic.customContextMenuRequested.connect(self.functionSetMeun)

    def initVar(self):
        self.ico = self.cwd + '/res/ico.ico'
        self.selectedPNG = self.cwd + '/res/gui/selected.png'
        self.unSelPNG = self.cwd + '/res/gui/unSelected.png'

        self.moveFlag = False
        
        self.noticeMd5 = ''
        self._notice = ''
        self._updateData = None

        self._data = None
        
        self.btnMainClicked = False

        self.battleFlag = None
        self.scheduleFlag = None
        self.taskFlag = None
        self.creditFlag = None
        self.shutdownFlag = None
        self.autoPCFlag = None
        self.doctorFlag = False
        self.logisticFlag = None

        self.inputSwitch = None

        self.forceStop = False

    def initNormalPicRes(self):
        self.home = pictureFind.picRead(self.cwd + "/res/panel/other/home.png")
        self.mainpage = pictureFind.picRead(self.cwd + "/res/panel/other/mainpage.png")
        self.mainpageMark = pictureFind.picRead(self.cwd + "/res/panel/other/act.png")

        self.listGoTo = [self.mainpage, self.home, self.mainpageMark]

    def changeRecStateMedLoop(self):
        if self.flag_loop_recovery_medicine:
            self.actAtuoMedicament.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(0, False)
        else:
            self.actAtuoMedicament.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.battle.recChange(0, True)
        self.flag_loop_recovery_medicine = not self.flag_loop_recovery_medicine
        #self.changeDefault('loop', self.flag_loop_recovery_medicine, 'medicament')
        user_data.change('recover.loop.medicine.enable', self.flag_loop_recovery_medicine)

    def changeRecStateMedSche(self):
        if self.flag_schedule_recovery_medicine:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(0, False)
        else:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.schedule.recChange(0, True)
        self.flag_schedule_recovery_medicine = not self.flag_schedule_recovery_medicine
        #self.changeDefault('schedule', self.flag_schedule_recovery_medicine, 'medicament')
        user_data.change('recover.schedule.medicine.enable', self.flag_schedule_recovery_medicine)
        

    def changeRecStateStoneLoop(self):
        if self.flag_loop_recovery_stone:
            self.actAutoStone.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(1, False)
        else:
            self.actAutoStone.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.battle.recChange(1, True)
        self.flag_loop_recovery_stone = not self.flag_loop_recovery_stone
        #self.changeDefault('loop', self.flag_loop_recovery_stone, 'stone')
        user_data.change('recover.loop.stone.enable', self.flag_loop_recovery_stone)

    def changeRecStateStoneSche(self):
        if self.flag_schedule_recovery_stone:
            self.actAutoStoneSche.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(1, False)
        else:
            self.actAutoStoneSche.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.schedule.recChange(1, True)
        self.flag_schedule_recovery_stone = not self.flag_schedule_recovery_stone
        #self.changeDefault('schedule', self.flag_schedule_recovery_stone, 'stone')
        user_data.change('recover.schedule.stone.enable', self.flag_schedule_recovery_stone)
        

    def changeMaxNum(self):
        #num, ok = QInputDialog.getText(self, f'当前（{self.stoneMaxNum}）', '请输入最大源石消耗数量：')
        num, ok = AMessageBox.input(self, f'当前({self.maxNum_loop_recovery_stone})', '请输入最大源石消耗数量:')
        if ok:
            if not num.isdecimal():
                num = '0'

            self.maxNum_loop_recovery_stone = int(num)
            self.battle.recChange(2, int(num))
            self.schedule.recChange(2, int(num))
            user_data.change('recover.loop.stone.max', int(num))
            self.actMaxNumber.setText(f'设置上限（当前：{self.maxNum_loop_recovery_stone}）')

    def setLoopBattleTimes(self):
        nowLoopTimes = self.battle.getLoopTimes()
        if nowLoopTimes == -1:
            nowLoopTimes = '无限'
        times, ok = AMessageBox.input(self, f'当前（{nowLoopTimes}）', '请输入作战次数(输入0即为无限)：')
        if ok:
            if not times.isdecimal():
                times = -1
            elif times == '0':
                times = -1
            self.battle.setLoopTimes(int(times))
            if times == -1:
                times = '无限'
            self.actBattleTimes.setText(f'设定次数(当前：{times})')
            self.tbBattle.setText(f'战斗:{times}')

    def initState(self):
        self.initSlrSel()
        #额外理智恢复设置初始化
        self.flag_loop_recovery_medicine = user_data.get('recover.loop.medicine.enable')
        if self.flag_loop_recovery_medicine:
            self.actAtuoMedicament.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.battle.recChange(0, True)
        else:
            self.actAtuoMedicament.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(0, False)
        self.flag_schedule_recovery_medicine = user_data.get('recover.schedule.medicine.enable')
        if self.flag_schedule_recovery_medicine:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.schedule.recChange(0, True)
        else:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(0, False)

        self.flag_loop_recovery_stone = user_data.get('recover.loop.stone.enable')
        if self.flag_loop_recovery_stone:
            self.actAutoStone.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.battle.recChange(1, True)
        else:
            self.actAutoStone.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(1, False)
        self.flag_schedule_recovery_stone = user_data.get('recover.schedule.stone.enable')
        if self.flag_schedule_recovery_stone:
            self.actAutoStoneSche.setIcon(QIcon(self.theme.getSelectedIcon()))
            self.schedule.recChange(1, True)
        else:
            self.actAutoStoneSche.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(1, False)
        self.maxNum_loop_recovery_stone = user_data.get('recover.loop.stone.max')
        self.actMaxNumber.setText(f'设置上限(当前：{self.maxNum_loop_recovery_stone})')
        self.maxNum_schedule_recovery_stone = user_data.get('recover.schedule.stone.max')
        self.battle.recChange(2, self.maxNum_loop_recovery_stone)
        self.schedule.recChange(2, self.maxNum_schedule_recovery_stone)

        #功能开关
        self.battleFlag = user_data.get('function.loop.default')
        self.tbBattle.setChecked(self.battleFlag) #战斗选项
        self.scheduleFlag = user_data.get('function.schedule.default')
        self.tbSchedule.setChecked(self.scheduleFlag)
        self.autoPCFlag = user_data.get('function.autopc.default')
        self.tbAutoPC.setChecked(self.autoPCFlag)
        
        self.taskFlag = user_data.get('function.task.default')
        self.tbTask.setChecked(self.taskFlag) #任务选项
        self.creditFlag = user_data.get('function.credit.default')
        self.tbCredit.setChecked(self.creditFlag)

        self.logisticFlag = user_data.get('logistic.default')
        self.tbLogistic.setChecked(self.logisticFlag)

        self.shutdownFlag = user_data.get('function.shutdown.default')
        self.tbShutdown.setChecked(self.shutdownFlag) #自动关机

    
    def initClass(self):
        self.rateMonitor = ScreenRateMonitor([self])

        self.themeEditor = ThemeEditor(self.app, ico = self.ico)
        self.rateMonitor.addWidget(self.themeEditor)

        adb.changeSimulator(user_data)
        adb.adbErr.connect(self.stop)
        adb.adbNotice.connect(self.noticeFromOtherWidget)

        self.battle = BattleLoop(self.cwd, self.ico)
        self.battle.noBootySignal.connect(self.battleWarning)
        self.battle.errorSignal.connect(self.errorDetect)
        
        self.schedule = BattleSchedule(self.cwd, self.ico) #处于测试
        self.schedule.errorSignal.connect(self.errorDetect)
        
        self.task = Task(self.cwd, self.ico, self.listGoTo)
        self.credit = Credit(self.cwd, self.listGoTo)

        if path.exists(config_path + '/logisticRule.ahrule'):
            self.logisticReady()
        else:
            self.logistic = None
            self.tbLogistic.setEnabled(False)
            self.logisticFlag = False
            self.tbLogistic.setChecked(self.logisticFlag)

        if path.exists(self.cwd + '/data.json'):
            self.initPc()
        else:
            self._data = None
            self.publicCall = None
            self.tbAutoPC.setEnabled(False)
            #self.btnMonitorPublicCall.setEnabled(False)
        
        
        self.schJsonEditer = JsonEdit(self.app, self.ico)
        self.rateMonitor.addWidget(self.schJsonEditer)

        self.board = BlackBoard()

        self.afterInit_Q = AfterInit(self, self.cwd)
        self.afterInit_Q.boardNeedShow.connect(self.showMessage)
        self.afterInit_Q.reloadPcModule.connect(self.initPc)
        self.afterInit_Q.logisticReady.connect(self.logisticReady)
        self.afterInit_Q.widgetShow.connect(self.widgetShow)


    def initPc(self):
        try:
            with open(self.cwd + '/data.json', 'r', encoding = 'gbk') as f:
                temp = f.read()
        except UnicodeDecodeError:
            with open(self.cwd + '/data.json', 'r', encoding = 'UTF-8') as f:
                temp = f.read()
        self._data = loads(temp)
        self.publicCall = UIPublicCall(self.battle, self.cwd, #self.btnMonitorPublicCall, 
                    self.listGoTo, self._data['data'][0]['normal'], self._data['data'][0]['high']) #公开招募
        self.publicCall.setStar(1, 1, user_data.get('function.autopc.skip1star')) #自动公招保留一星设定
        self.publicCall.setStar(5, 1, user_data.get('function.autopc.skip5star'))
        self.publicCall.skip23Star = user_data.get('function.autopc.skip23star')
        self.tbAutoPC.setEnabled(True)
        #self.btnMonitorPublicCall.setEnabled(True)

    def initSlrSel(self):
        '初始化模拟器选择'
        slrName = user_data.get('simulator')
        for i in self.simulators:
            if i.key == slrName:
                i.setIcon(QIcon(self.theme.getSelectedIcon()))
                break
        else:
            if len(self.simulators) != 0: #删除当前使用的模拟器时的处理
                self.simulators[0].setIcon(QIcon(self.theme.getSelectedIcon()))
                user_data.change('simulator', self.simulators[0].key)
            else:
                user_data.change('simulator', 'unknow')


    def center(self):
        #显示到屏幕中心
        cp = QDesktopWidget().availableGeometry().center()
        self.move(int(cp.x() - self.width()/2), int(cp.y() - self.height()/2))


    def mousePressEvent(self, event):
        self.moveFlag = False
        self.mousePos = event.globalPos() - self.pos() #获取鼠标相对窗口的位置
        if event.button() == Qt.LeftButton:
            if self.mousePos.y() < self.btnStartAndStop.y(): #判断是否在可移动区域
                self.moveFlag = True
            event.accept()
            
    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.moveFlag:  
            self.move(QMouseEvent.globalPos() - self.mousePos) #更改窗口位置
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        #停止窗口移动
        if Qt.LeftButton and self.moveFlag:
            self.moveFlag = False
            newPos = self.screen.checkWidget(QMouseEvent.globalPos().x() - self.mousePos.x(),
                                             QMouseEvent.globalPos().y() - self.mousePos.y(), 
                                             self.width(), self.height())
            self.move(newPos[0], newPos[1])
            #self.resizeUI()
    
    def functionSetMeun(self):
        self.source = self.sender()
        self.rightClickMenu.clear()
        
        if self.source == self.tbBattle:
            if user_data.get('function.loop.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            self.rightClickMenu.addAction(self.actBattleTimes)
            self.rightClickMenu.addAction(self.line)
        elif self.source.text() == '计划战斗':
            if user_data.get('function.schedule.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            self.rightClickMenu.addAction(self.actSchJson)
            self.rightClickMenu.addAction(self.line)
        elif self.source.text() == '自动公招':
            if user_data.get('function.autopc.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            #自动招募和自动聘用
            self.rightClickMenu.addAction(self.actAutoSearch)
            self.rightClickMenu.addAction(self.actAutoEmploy)
            self.rightClickMenu.addAction(self.actSkipStar23)
            self.rightClickMenu.addAction(self.actSkipStar1)
            self.rightClickMenu.addAction(self.actSkipStar5)
            self.rightClickMenu.addAction(self.line)
            self.rightClickMenu.addAction(self.actPcCalculate)
        elif self.source.text() == '任务交付':
            if user_data.get('function.task.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '获取信用':
            if user_data.get('function.credit.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '完成后关机':
            if user_data.get('function.shutdown.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source == self.tbLogistic:
            if user_data.get('logistic.default'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            self.rightClickMenu.addAction(self.actLogisticConfig)
            self.rightClickMenu.addAction(self.line)
        self.actionSetDeafult = self.rightClickMenu.addAction(text)
        self.actionSetDeafult.triggered.connect(self.setDefault)
        self.rightClickMenu.exec_(QCursor.pos())
    
    def setDefault(self):
        if self.source == self.tbBattle:
            key = 'function.loop.default'
            value = not user_data.get('function.loop.default')
        elif self.source.text() == '计划战斗':
            key = 'function.schedule.default'
            value = not user_data.get('function.schedule.default')
        elif self.source.text() == '自动公招':
            key = 'function.autopc.default'
            value = not user_data.get('function.autopc.default')
        elif self.source.text() == '任务交付':
            key = 'function.task.default'
            value = not user_data.get('function.task.default')
        elif self.source.text() == '获取信用':
            key = 'function.credit.default'
            value = not user_data.get('function.credit.default')
        elif self.source.text() == '完成后关机':
            key ='function.shutdown.default'
            value = not user_data.get('function.shutdown.default')
        elif self.source == self.tbLogistic:
            key = 'logistic.default'
            value = not user_data.get('logistic.default')

        user_data.change(key, value)
    
    def functionSel(self, isChecked):
        source = self.sender()
        if source == self.tbBattle:
            self.battleFlag = isChecked
        elif source.text() == '计划战斗':
            self.scheduleFlag = isChecked
        elif source.text() == '自动公招':
            self.autoPCFlag = isChecked
        elif source.text() == '任务交付':
            self.taskFlag = isChecked
        elif source.text() == '获取信用':
            self.creditFlag = isChecked
        elif source.text() == '完成后关机':
            self.shutdownFlag = isChecked
        elif source.text() == '自动招募':
            self.publicCall.searchFlag = isChecked
        elif source.text() == '自动聘用':
            self.publicCall.employFlag = isChecked
        elif source == self.tbLogistic:
            self.logisticFlag = isChecked

    def setAutoPCFunc(self):
        source = self.sender()
        if source.text() == '自动招募':
            self.publicCall.searchFlag = not self.publicCall.searchFlag
            if self.publicCall.searchFlag:
                source.setIcon(QIcon(self.theme.getSelectedIcon()))
            else:
                source.setIcon(QIcon(''))
        elif source.text() == '自动聘用':
            self.publicCall.employFlag = not self.publicCall.employFlag
            if self.publicCall.employFlag:
                source.setIcon(QIcon(self.theme.getSelectedIcon()))
            else:
                source.setIcon(QIcon(''))
        elif source.text() == '跳过3星及以下':
            self.publicCall.skip23Star = not self.publicCall.skip23Star
            if self.publicCall.skip23Star:
                source.setIcon(QIcon(self.theme.getSelectedIcon()))
                user_data.change('function.autopc.skip23star', True)
            else:
                source.setIcon(QIcon(''))
                user_data.change('function.autopc.skip23star', False)
        elif source.text() == '保留1星':
            self.publicCall.setStar(1, 1, not self.publicCall.setStar(1, 0))
            if self.publicCall.setStar(1,0):
                source.setIcon(QIcon(self.theme.getSelectedIcon()))
                user_data.change('function.autopc.skip1star', True)
            else:
                source.setIcon(QIcon(''))
                user_data.change('function.autopc.skip1star', False)
        elif source.text() == '保留5星':
            self.publicCall.setStar(5, 1, not self.publicCall.setStar(5, 0))
            if self.publicCall.setStar(5,0):
                source.setIcon(QIcon(self.theme.getSelectedIcon()))
                user_data.change('function.autopc.skip5star', True)
            else:
                source.setIcon(QIcon(''))
                user_data.change('function.autopc.skip5star', False)
    
    def openSchEdit(self):
        self.schJsonEditer.editerShow()
    
    def monitorPC(self):
        if not self.doctorFlag:
            self.publicCall.turnOn()

    def simulatorSel(self):
        #slrName = self.sender()
        slr = self.sender()
        user_data.change('simulator', slr.key)

        for each in self.simulators:
            each.setIcon(QIcon(''))

        slr.setIcon(QIcon(self.theme.getSelectedIcon()))
        adb.changeSimulator(user_data)

        
    def exit(self):
        '退出按钮'
        self.schJsonEditer.close()
        self.hide()
        self.stop(isExit = True)
        self.console.close()
        if self.publicCall != None:
            self.publicCall.close()
        adb.killAdb()

        #退出两个窗口的放大倍率检测线程
        #self.schJsonEditer.rateMonitor.stop()
        self.rateMonitor.stop()

        sys.exit() #为了解决Error in atexit._run_exitfuncs:的问题，实际上我完全不知道这为什么出现

    def minimize(self):
        '最小化按钮'
        self.showMinimized()

    def openUpdate(self):
        openUrl('https://mangetsuc.lanzoui.com/b0d1w6v7g')

    def openIndex(self):
        openUrl('https://github.com/MangetsuC/arkHelper')
                
    def showMessage(self):
        user_data.change('notice', self.noticeMd5)
        self.board.updateText(self._notice)
        self.board.show()
        #弹出公告

    def openThemeEditor(self):
        self.themeEditor.show()

    def startUpdate(self):
        if path.exists(self.cwd + '/update.exe'):
            selfPidList = adb.cmd.getTaskList('arkhelper.exe')
            exceptions = self._updateData['exception'].split(',') #不再排除update.exe自身
            if 'update.exe' in exceptions:
                exceptions.remove('update.exe')
            self._updateData['exception'] = ','.join(exceptions)
            updateJson = {'localPath': self.cwd, 
                            'onlinePath': self._updateData['onlinePath'] + '/v' +self._updateData['version'],
                            'commonPath': self._updateData['commonPath'],
                            'Pid': ','.join(selfPidList),
                            'exceptionFile': self._updateData['exception']}
            with open('updateData.json', 'w', encoding='UTF-8') as f:
                f.write(dumps(updateJson, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
            startfile('update.exe')
    
    def battleWarning(self):
        reply = AMessageBox.question(self, '警告', '发现您选中的关卡可能无掉落，是否继续？')
        if reply:
            self.battle.isUselessContinue = True
        else:
            self.battle.stop()
        self.battle.isWaitingUser = False

    def testUpdate(self):
        version, isOk = AMessageBox.input(self, '???', '神秘代码')
        if isOk:
            if self._updateData != None:
                self._updateData['version'] = version
                self.startUpdate()

    def start(self):
        self.doctorFlag = self.battle.connect()
        if self.doctorFlag and self.scheduleFlag:
            self.schedule.run(self.doctorFlag)
        if self.doctorFlag and self.battleFlag:
            self.battle.run(self.doctorFlag)
        if (self.publicCall != None) and self.doctorFlag and self.autoPCFlag:
            self.publicCall.autoPCRun(self.doctorFlag)
        if self.doctorFlag and self.logisticFlag:
            self.logistic.run(self.doctorFlag)
        if self.doctorFlag and self.taskFlag:
            self.task.run(self.doctorFlag)
        if self.doctorFlag and self.creditFlag:
            self.credit.run(self.doctorFlag)
        if self.shutdownFlag and self.doctorFlag:
            adb.cmd.shutdown(time=120)
            self.exitBeforeShutdown.emit()
        else:
            self.stop(isExit = True)

    def stop(self, isErrStop = False, isExit = False):
        self.doctorFlag = False
        if self.publicCall != None:
            self.publicCall.autoPCStop()
        self.schedule.stop()
        self.battle.stop()
        self.task.stop()
        self.credit.stop()
        if self.logistic != None:
            self.logistic.stop()
        self.btnMainClicked = False
        #self.btnStartAndStop.setText('启动虚拟博士')

        if not isExit:
            aliveCheck = Thread(target=self.threadAliveCheck)
            aliveCheck.setDaemon(True)
            aliveCheck.start()
        else:
            self.startBtnPressed.emit('启动虚拟博士')

        if isErrStop:
            self.lTitle.setText('出现错误 请检查控制台')

    def adbClosedHandle(self):
        forceThreadStop(self.thRun)
        self.lTitle.setText('出现错误 请检查控制台')
        self.startBtnPressed.emit('启动虚拟博士')

    def clickBtnStartAndStop(self):
        if not '虚拟博士' in self.btnStartAndStop.text():
            forceThreadStop(self.thRun)
            self.forceStop = True
            print('收到用户指令强制终止，可能存在部分未释放的资源')
        else:
            self.btnMainClicked = not self.btnMainClicked
            if self.btnMainClicked:
                self.forceStop = False
                self.btnStartAndStop.setText('停止虚拟博士')
                self.thRun = Thread(target=self.start)
                self.thRun.setDaemon(True)
                self.thRun.start()
            else:
                self.stop()  
                self.thRun.join(0.5)

    def threadAliveCheck(self):
        self.startBtnPressed.emit('正在停止\n再次点击强制关闭\n-不推荐-\n仅供特殊情况')
        while not self.forceStop:
            if not self.thRun.is_alive():
                break
        self.startBtnPressed.emit('启动虚拟博士')


    def errorDetect(self, source):
        if source == 'loop':
            self.battle.isWaitingUser = True
            self.battle.isRecovered = False
            reply = AMessageBox.question(self, '警告', '发现网络中断或代理异常，是否继续？（请在恢复异常后继续）')
            self.battle.isWaitingUser = False
            if reply:
                self.battle.isRecovered = True
        elif source == 'schedule':
            self.schedule.isWaitingUser = True
            self.schedule.isRecovered = False
            reply = AMessageBox.question(self, '警告', '发现网络中断或代理异常，是否继续？（请在恢复异常后继续）')
            self.schedule.isWaitingUser = False
            if reply:
                self.schedule.isRecovered = True

    def logisticReady(self):
        self.logistic = UILogistic(config_path + '/logisticRule.ahrule', self.app, ico = self.ico)
        self.actLogisticConfig.triggered.connect(self.logistic.show)
        self.tbLogistic.setEnabled(True)

        self.logisticFlag = user_data.get('logistic.default')
        self.tbLogistic.setChecked(self.logisticFlag)
        self.rateMonitor.addWidget(self.logistic)

    def widgetShow(self, widgetNo):
        if widgetNo == 0:
            self.btnShowMsg.show()
        elif widgetNo == 1:
            self.lVer.setText('*有新版本*')
            self.btnUpdate.show()

    def noticeFromOtherWidget(self, text):
        AMessageBox.warning(self, '警告', text)

    def simulator_choices(self):
        '添加模拟器菜单中的选项'
        self.actSimulator_add = QAction('添加')
        self.actSimulator_add.triggered.connect(self.simulator_add)

        self.actSimulator.clear()
        self.actSimulator_del.clear()
        self.simulators.clear()
        for i in simulator_data.get_simulators():
            temp_act = SimulatorAction(simulator_data.get(i)['name'], i, self.actSimulator)
            temp_act.triggered.connect(self.simulatorSel)
            self.simulators.append(temp_act)
            self.actSimulator.addAction(temp_act)

            temp_act_del = SimulatorAction(simulator_data.get(i)['name'], i, self.actSimulator)
            temp_act_del.triggered.connect(self.simulator_del)
            self.actSimulator_del.addAction(temp_act_del)
        self.actSimulator.addSeparator()
        self.actSimulator.addAction(self.actSimulator_add)
        self.actSimulator.addMenu(self.actSimulator_del)

    def simulator_add(self):
        '添加模拟器配置'
        simulator_new = AMessageBox.input(self, '请输入模拟器信息', 
                '数据格式:名称;ID;adb来源[internal|external];IP地址\n\
如:蓝叠模拟器;bluestacks;internal;127.0.0.1:5555\n\
如:雷电模拟器;leidian;internal;emulator-5554')
        if simulator_new[1]:
            simulator_new = simulator_new[0].split(';')
            if len(simulator_new) == 4:
                id = simulator_new[1]
                simulator_data.change(f'{id}.ip', simulator_new[3])
                simulator_data.change(f'{id}.adb', simulator_new[2])
                simulator_data.change(f'{id}.name', simulator_new[0])
                self.simulator_choices() #更新菜单
                self.initSlrSel() #更新选中项
                adb.changeSimulator(user_data)

    def simulator_del(self):
        '删除模拟器配置'
        sender = self.sender()
        simulator_data.delete(sender.key)
        self.simulator_choices()
        self.initSlrSel()
        adb.changeSimulator(user_data)

class SimulatorAction(QAction):
    def __init__(self, text, key, parent = None):
        super(SimulatorAction, self).__init__(text, parent)
        self.key = key

if __name__ == '__main__':
    cgitb.enable(format = 'text')
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    exLaunch = Launch()
    app.processEvents()
    ex = App(app)
    exLaunch.finish(ex)
    ex.afterInit_Q.start()
    ex.rateMonitor.start()
    sys.exit(app.exec_())
