import cgitb
import sys
from configparser import ConfigParser
from json import dumps, loads
from os import getcwd, getlogin, mkdir, path, startfile
from threading import Thread
from webbrowser import open as openUrl

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QGridLayout, QHBoxLayout, QInputDialog, QLabel,
                             QMenu, QMessageBox, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog)

from foo.adb.adbCtrl import Adb
from foo.arknight.Battle import BattleLoop
from foo.arknight.credit import Credit
from foo.arknight.Schedule import BattleSchedule
from foo.arknight.task import Task
from foo.pictureR import pictureFind
from foo.ui.console import Console
from foo.ui.launch import AfterInit, BlackBoard, Launch
from foo.ui.UIPublicCall import UIPublicCall
from foo.ui.UIschedule import JsonEdit
from foo.ui.screen import Screen


class App(QWidget):
    def __init__(self):
        super(App, self).__init__()
        self.ver = '2.6.3'

        self.cwd = getcwd().replace('\\', '/')
        self.console = Console(self.cwd) #接管输出与报错

        #获取整块屏幕的尺寸
        self.totalWidth = 0
        self.totalHeight = 0
        tempScreenList = []
        for i in range(QDesktopWidget().screenCount()):
            tempScreenList.append(QDesktopWidget().availableGeometry(i))
        self.screen = Screen(tempScreenList)
        theBottomOne = sorted(tempScreenList, key = lambda screen:screen.y())[-1]
        theTopOne = sorted(tempScreenList, key = lambda screen:screen.y())[0]
        theRightOne = sorted(tempScreenList, key = lambda screen:screen.x())[-1]
        theLeftOne = sorted(tempScreenList, key = lambda screen:screen.x())[0]
        self.topPos = theTopOne.y()
        self.leftPos = theLeftOne.x()
        self.totalWidth = theRightOne.x() + theRightOne.width()
        self.totalHeight = theBottomOne.y() + theBottomOne.height()

        self.initFile()
        self.initVar()
        self.initNormalPicRes()
        self.initUI()
        self.initClass()
        self.initRightClickMeun()
        self.initState()
        self.isRun = False
        self.center()
        self.show()

    def initFile(self):
        self.userDataPath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper'
        if path.exists(self.cwd + '/config.ini'):
            self.userDataPath = self.cwd #便于调试时不改变实际使用的配置
        elif not path.exists(self.userDataPath):
            try:
                mkdir(self.userDataPath)
            except Exception as creatDirErr:
                print(creatDirErr)
                self.userDataPath = self.cwd
        
        if not path.exists(self.userDataPath + '/config.ini'):
            with open(self.userDataPath + '/config.ini', 'w') as c:
                c.write('')

        self.configPath = self.userDataPath + '/config.ini'  #读
        self.config = ConfigParser()
        self.config.read(filenames=self.configPath, encoding="UTF-8")

        isNeedWrite = False
        if not self.config.has_section('connect'):
            self.config.add_section('connect')
            isNeedWrite = True
        if not self.config.has_option('connect', 'ip'):
            self.config.set('connect','ip','127.0.0.1')
            isNeedWrite = True
        if not self.config.has_option('connect', 'port'):
            self.config.set('connect','port','5555')
            isNeedWrite = True
        if not self.config.has_option('connect', 'simulator'):
            self.config.set('connect','simulator','bluestacks')
            isNeedWrite = True

        if not self.config.has_section('function'):
            self.config.add_section('function')
            isNeedWrite = True
        if not self.config.has_option('function', 'battle'):
            self.config.set('function','battle','True')
            isNeedWrite = True
        if not self.config.has_option('function', 'schedule'):
            self.config.set('function','schedule','False')
            isNeedWrite = True
        if not self.config.has_option('function', 'autoPC'):
            self.config.set('function','autoPC','False')
            isNeedWrite = True
        if not self.config.has_option('function', 'autoPC_skip1Star'):
            self.config.set('function','autoPC_skip1Star','True')
            isNeedWrite = True
        if not self.config.has_option('function', 'autoPC_skip5Star'):
            self.config.set('function','autoPC_skip5Star','True')
            isNeedWrite = True
        if not self.config.has_option('function', 'task'):
            self.config.set('function','task','True')
            isNeedWrite = True
        if not self.config.has_option('function', 'credit'):
            self.config.set('function','credit','False')
            isNeedWrite = True
        if not self.config.has_option('function', 'shutdown'):
            self.config.set('function','shutdown','False')
            isNeedWrite = True
        if not self.config.has_option('function', 'publiccall'):
            self.config.set('function','publiccall','False')
            isNeedWrite = True

        if not self.config.has_section('medicament'):
            self.config.add_section('medicament')
            isNeedWrite = True
        if not self.config.has_option('medicament', 'loop'):
            self.config.set('medicament','loop','False')
            isNeedWrite = True
        if not self.config.has_option('medicament', 'schedule'):
            self.config.set('medicament','schedule','False')
            isNeedWrite = True

        if not self.config.has_section('stone'):
            self.config.add_section('stone')
            isNeedWrite = True
        if not self.config.has_option('stone', 'loop'):
            self.config.set('stone','loop','False')
            isNeedWrite = True
        if not self.config.has_option('stone', 'schedule'):
            self.config.set('stone','schedule','False')
            isNeedWrite = True
        if not self.config.has_option('stone', 'maxnum'):
            self.config.set('stone','maxnum','0')
            isNeedWrite = True

        if not self.config.has_section('notice'):
            self.config.add_section('notice')
            isNeedWrite = True
        if not self.config.has_option('notice', 'enable'):
            self.config.set('notice','enable','True')
            isNeedWrite = True
        if not self.config.has_option('notice', 'md5'):
            self.config.set('notice','md5','0')
            isNeedWrite = True

        if isNeedWrite:
            configInI = open(self.configPath, 'w')  #写
            self.config.write(configInI)
            configInI.close()  #配置文件初始化结束

        if not path.exists(self.userDataPath + '/schedule.json'):
            with open(self.userDataPath + '/schedule.json', 'w', encoding = 'UTF-8') as j:
                j.write('{\n\t\"main\": [\n\t\t{\n\t\t\t\"allplan\": \"未选择\",\n\t\t\t\"sel\": []\n\t\t},\n\t\t{\n\t\t\t\"未选择\": []\n\t\t}\n\t]\n}')
        else:
            with open(self.userDataPath + '/schedule.json', 'r', encoding = 'UTF-8') as j:
                tempText = j.read()
            if 'allplan' not in tempText:
                oldJson = loads(tempText)
                newJson = dict()
                newJson['main'] = [{'allplan':'未选择','sel':oldJson['levels']},{'未选择':[]}]
                newJson = dumps(newJson, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
                with open(self.userDataPath + '/schedule.json', 'w', encoding = 'UTF-8') as j:
                    j.write(newJson)
                #计划json初始化结束
    
    def initUI(self): 
        self.setWindowIcon(QIcon(self.ico))
        self.setWindowTitle('明日方舟小助手')

        self.resize(420,150)

        self.line = QAction()
        self.line.setSeparator(True)

        self.setWindowFlag(Qt.FramelessWindowHint) #隐藏边框

        self.setStyleSheet('''App{background:#272626}QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:9pt;}
                                QPushButton{border:0px;background:#4d4d4d;
                                color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QPushButton:pressed{background:#606162;font:9pt;}
                                QPushButton:checked{background:#70bbe4;}
                                QInputDialog{background-color:#4d4d4d;}
                                QMessageBox{background-color:#4d4d4d;}
                                QToolTip {font-family:"Microsoft YaHei", SimHei, SimSun; font-size:10pt; color:#ffffff;
                                        padding:5px;
                                        border-style:solid; border-width:1px; border-color:gray;
                                        background-color:#272626;}
                            ''')

        self.lTitle = QLabel('明日方舟小助手')
        self.lTitle.setStyleSheet('''
                                    QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}
                                    ''')
        self.lVer = QLabel(f'v{self.ver}')
        self.lVer.setStyleSheet('''
                                    QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}
                                    ''')

        self.btnExit = QPushButton('×',self)
        self.btnExit.setFixedSize(30,30)
        self.btnExit.setStyleSheet('''QPushButton{background:#272626;font-family:SimHei, SimSun;font:20pt;}
                                    QPushButton:pressed{background:#272626;font:16pt;}
                                    ''')
        self.btnExit.clicked.connect(self.exit)
        self.btnExit.setToolTip('关闭')

        self.btnMinimize = QPushButton('-',self)
        self.btnMinimize.setFixedSize(30,30)
        self.btnMinimize.setStyleSheet('''QPushButton{background:#272626;font-family:SimSun;font:normal 28pt;}
                                    QPushButton:pressed{background:#272626;font-family:SimSun;font:20pt;}
                                    ''')
        self.btnMinimize.clicked.connect(self.minimize)
        self.btnMinimize.setToolTip('最小化')

        self.btnSetting = QPushButton('≡',self)
        self.btnSetting.setFixedSize(30,30)
        self.btnSetting.setStyleSheet('''QPushButton{background:#272626;font-family:SimHei, SimSun;font:16pt;}
                                    QPushButton:pressed{background:#272626;font-family:SimHei, SimSun;font:14pt;}
                                    QPushButton:menu-indicator{image:none;width:0px;}
                                    ''')
        self.btnSetting.setToolTip('设置')

        self.btnUpdate = QPushButton('∧',self)
        self.btnUpdate.setFixedSize(30,30)
        self.btnUpdate.setStyleSheet('''QPushButton{background:#272626;font-family:SimHei, SimSun;font:14pt;}
                                    QPushButton:pressed{background:#272626;font-family:SimHei, SimSun;font:12pt;}
                                    ''')
        self.btnUpdate.clicked.connect(self.startUpdate)
        self.btnUpdate.setToolTip('自动更新')
        self.btnUpdate.hide()

        self.btnStartAndStop = QPushButton('启动虚拟博士', self) #启动/停止按钮
        self.btnStartAndStop.setFixedSize(180, 131)
        self.btnStartAndStop.setStyleSheet('''QPushButton{font:13pt;}''')
        self.btnStartAndStop.clicked.connect(self.clickBtnStartAndStop)

        self.btnMonitorPublicCall = QPushButton('公开招募计算器', self)
        self.btnMonitorPublicCall.setFixedSize(155, 40)
        self.btnMonitorPublicCall.setCheckable(True)
        self.btnMonitorPublicCall.clicked[bool].connect(self.monitorPC)
        self.btnMonitorPublicCall.setToolTip('打开公招计算器，它会自动帮你计算模拟器屏幕上的tag组合')

        self.tbBattle = QPushButton('战斗：无限', self) #战斗可选按钮
        self.tbBattle.setCheckable(True)
        self.tbBattle.setFixedSize(75, 40)
        self.tbBattle.clicked[bool].connect(self.functionSel)
        self.tbBattle.setToolTip('从你目前处在的关卡开始循环作战，直到理智不足')

        self.actBattleTimes = QAction('设定次数(当前：无限)')
        self.actBattleTimes.triggered.connect(self.setLoopBattleTimes)

        self.tbSchedule = QPushButton('计划战斗', self) #计划战斗可选按钮
        self.tbSchedule.setCheckable(True)
        self.tbSchedule.setFixedSize(75, 40)
        self.tbSchedule.clicked[bool].connect(self.functionSel)
        self.tbSchedule.setToolTip('在右键菜单中设定你的计划，会按照设定的计划作战')

        self.tbAutoPC = QPushButton('自动公招', self) #自动公招可选按钮
        self.tbAutoPC.setCheckable(True)
        self.tbAutoPC.setFixedSize(75, 40)
        self.tbAutoPC.clicked[bool].connect(self.functionSel)
        self.tbAutoPC.setToolTip('自动进行公开招募，在右键菜单中进行配置')

        self.actAutoSearch = QAction('自动招募')
        self.actAutoSearch.triggered.connect(self.setAutoPCFunc)
        self.actAutoSearch.setIcon(QIcon(self.selectedPNG))
        self.actAutoEmploy = QAction('自动聘用')
        self.actAutoEmploy.triggered.connect(self.setAutoPCFunc)
        self.actAutoEmploy.setIcon(QIcon(self.selectedPNG))
        self.actSkipStar1 = QAction('保留1星')
        self.actSkipStar1.triggered.connect(self.setAutoPCFunc)
        if self.config.getboolean('function','autoPC_skip1Star'):
            self.actSkipStar1.setIcon(QIcon(self.selectedPNG))
        self.actSkipStar5 = QAction('保留5星')
        self.actSkipStar5.triggered.connect(self.setAutoPCFunc)
        if self.config.getboolean('function','autoPC_skip5Star'):
            self.actSkipStar5.setIcon(QIcon(self.selectedPNG))

        self.actSchJson = QAction('路线规划')
        self.actSchJson.triggered.connect(self.openSchEdit)

        self.tbTask = QPushButton('任务交付', self) #任务交付可选按钮
        self.tbTask.setCheckable(True)
        self.tbTask.setFixedSize(75, 40)
        self.tbTask.clicked[bool].connect(self.functionSel)
        self.tbTask.setToolTip('自动交付任务')

        self.tbCredit = QPushButton('获取信用', self)
        self.tbCredit.setCheckable(True)
        self.tbCredit.setFixedSize(75, 40)
        self.tbCredit.clicked[bool].connect(self.functionSel)
        self.tbCredit.setToolTip('自动拜访好友的基建以获取信用点')

        self.tbShutdown = QPushButton('完成后关机', self)
        self.tbShutdown.setCheckable(True)
        self.tbShutdown.setFixedSize(155, 40)
        self.tbShutdown.clicked[bool].connect(self.functionSel)

        #self.btnSet = QPushButton('设置',self) #设置按钮
        #self.btnSet.setFixedSize(75, 40)

        self.settingMenu = QMenu() #创建设置按钮菜单
        self.settingMenu.setStyleSheet('''QMenu {color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                        background-color:#272626; margin:3px;}
                                        QMenu:item {padding:8px 32px;}
                                        QMenu:item:selected { background-color: #3f4140;}
                                        QMenu:icon{padding: 8px 20px;}''')
        self.actSimulator = QMenu('模拟器', parent=self.settingMenu) #模拟器二级菜单
        self.actSlrBlueStacks = QAction('蓝叠模拟器', parent=self.actSimulator)
        self.actSlrMumu = QAction('Mumu模拟器', parent=self.actSimulator)
        self.actSlrYeshen = QAction('夜神模拟器', parent=self.actSimulator)
        self.actSlrXiaoyao = QAction('逍遥模拟器', parent=self.actSimulator)
        self.actSlrLeidian = QAction('雷电模拟器', parent=self.actSimulator)
        self.actSlrCustom = QAction('自定义', parent=self.actSimulator)

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

        self.actConsole = QAction('控制台', parent=self.settingMenu)
        self.actCheckUpdate = QAction('前往下载', parent=self.settingMenu)
        self.actIndex = QAction('访问主页', parent=self.settingMenu)
        
        self.actVersion2 = QAction(f'v{self.ver}', parent=self.settingMenu)

        self.slrList = [self.actSlrBlueStacks, self.actSlrMumu, self.actSlrXiaoyao, self.actSlrYeshen, self.actSlrLeidian, self.actSlrCustom]
        #添加菜单选项
        self.settingMenu.addMenu(self.actSimulator) #模拟器二级菜单
        for eachSlr in self.slrList:
            self.actSimulator.addAction(eachSlr)
            eachSlr.triggered.connect(self.simulatorSel)

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
        self.HBox.addWidget(self.btnUpdate)
        self.HBox.addWidget(self.btnSetting)
        self.HBox.addWidget(self.btnMinimize)
        self.HBox.addWidget(self.btnExit)

        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(5)
        self.grid.setHorizontalSpacing(5)
        
        self.grid.addWidget(self.btnStartAndStop, 0, 0, 3, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btnMonitorPublicCall, 1, 1, 1, 2, alignment=Qt.AlignCenter)
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
        self.btnMonitorPublicCall.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btnMonitorPublicCall.customContextMenuRequested.connect(self.functionSetMeun)

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

    def initNormalPicRes(self):
        self.home = pictureFind.picRead(self.cwd + "/res/panel/other/home.png")
        self.mainpage = pictureFind.picRead(self.cwd + "/res/panel/other/mainpage.png")
        self.mainpageMark = pictureFind.picRead(self.cwd + "/res/panel/other/act.png")

        self.listGoTo = [self.mainpage, self.home, self.mainpageMark]

    def changeRecStateMedLoop(self):
        if self.autoMediFlag:
            self.actAtuoMedicament.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(0, False)
        else:
            self.actAtuoMedicament.setIcon(QIcon(self.selectedPNG))
            self.battle.recChange(0, True)
        self.autoMediFlag = not self.autoMediFlag
        self.changeDefault('loop', self.autoMediFlag, 'medicament')

    def changeRecStateMedSche(self):
        if self.autoMediScheFlag:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(0, False)
        else:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.selectedPNG))
            self.schedule.recChange(0, True)
        self.autoMediScheFlag = not self.autoMediScheFlag
        self.changeDefault('schedule', self.autoMediScheFlag, 'medicament')

    def changeRecStateStoneLoop(self):
        if self.autoStoneFlag:
            self.actAutoStone.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(1, False)
        else:
            self.actAutoStone.setIcon(QIcon(self.selectedPNG))
            self.battle.recChange(1, True)
        self.autoStoneFlag = not self.autoStoneFlag
        self.changeDefault('loop', self.autoStoneFlag, 'stone')

    def changeRecStateStoneSche(self):
        if self.autoStoneScheFlag:
            self.actAutoStoneSche.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(1, False)
        else:
            self.actAutoStoneSche.setIcon(QIcon(self.selectedPNG))
            self.schedule.recChange(1, True)
        self.autoStoneScheFlag = not self.autoStoneScheFlag
        self.changeDefault('schedule', self.autoStoneScheFlag, 'stone')

    def changeMaxNum(self):
        num, ok = QInputDialog.getText(self, f'当前（{self.stoneMaxNum}）', '请输入最大源石消耗数量：')
        if ok:
            if not num.isdecimal():
                num = '0'

            self.stoneMaxNum = int(num)
            self.battle.recChange(2, int(num))
            self.schedule.recChange(2, int(num))
            self.changeDefault('maxnum', num, 'stone')
            self.actMaxNumber.setText(f'设置上限（当前：{self.stoneMaxNum}）')

    def setLoopBattleTimes(self):
        nowLoopTimes = self.battle.getLoopTimes()
        if nowLoopTimes == -1:
            nowLoopTimes = '无限'
        times, ok = QInputDialog.getText(self, f'当前（{nowLoopTimes}）', '请输入作战次数(输入0即为无限)：')
        if ok:
            if not times.isdecimal():
                times = -1
            elif times == '0':
                times = -1
            self.battle.setLoopTimes(int(times))
            if times == -1:
                times = '无限'
            self.actBattleTimes.setText(f'设定次数(当前：{times})')
            self.tbBattle.setText(f'战斗：{times}')

    def initState(self):
        self.initSlrSel()
        #额外理智恢复设置初始化
        self.autoMediFlag = self.config.getboolean('medicament', 'loop')
        if self.autoMediFlag:
            self.actAtuoMedicament.setIcon(QIcon(self.selectedPNG))
            self.battle.recChange(0, True)
        else:
            self.actAtuoMedicament.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(0, False)
        self.autoMediScheFlag = self.config.getboolean('medicament', 'schedule')
        if self.autoMediScheFlag:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.selectedPNG))
            self.schedule.recChange(0, True)
        else:
            self.actAtuoMedicamentSch.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(0, False)
        self.autoStoneFlag = self.config.getboolean('stone', 'loop')
        if self.autoStoneFlag:
            self.actAutoStone.setIcon(QIcon(self.selectedPNG))
            self.battle.recChange(1, True)
        else:
            self.actAutoStone.setIcon(QIcon(self.unSelPNG))
            self.battle.recChange(1, False)
        self.autoStoneScheFlag = self.config.getboolean('stone', 'schedule')
        if self.autoStoneScheFlag:
            self.actAutoStoneSche.setIcon(QIcon(self.selectedPNG))
            self.schedule.recChange(1, True)
        else:
            self.actAutoStoneSche.setIcon(QIcon(self.unSelPNG))
            self.schedule.recChange(1, False)
        self.stoneMaxNum = self.config.getint('stone', 'maxnum')
        self.actMaxNumber.setText(f'设置上限(当前：{self.stoneMaxNum})')
        self.battle.recChange(2, self.stoneMaxNum)
        self.schedule.recChange(2, self.stoneMaxNum)

        #功能开关
        self.battleFlag = self.config.getboolean('function', 'battle')
        self.tbBattle.setChecked(self.battleFlag) #战斗选项
        self.scheduleFlag = self.config.getboolean('function', 'schedule')
        self.tbSchedule.setChecked(self.scheduleFlag)
        self.autoPCFlag = self.config.getboolean('function', 'autoPC')
        self.tbAutoPC.setChecked(self.autoPCFlag)
        
        self.taskFlag = self.config.getboolean('function', 'task')
        self.tbTask.setChecked(self.taskFlag) #任务选项
        self.creditFlag = self.config.getboolean('function', 'credit')
        self.tbCredit.setChecked(self.creditFlag)

        self.shutdownFlag = self.config.getboolean('function', 'shutdown')
        self.tbShutdown.setChecked(self.shutdownFlag) #自动关机

        self.PCFlag = self.config.getboolean('function', 'publiccall')
        self.btnMonitorPublicCall.setChecked(self.PCFlag)
        if self.PCFlag and self.publicCall != None:
            self.publicCall.turnOn()
    
    def initClass(self):
        self.adb = Adb(self.cwd + '/bin/adb', self.config)

        self.battle = BattleLoop(self.adb, self.cwd, self.ico)
        self.battle.noBootySignal.connect(self.battleWarning)
        self.battle.errorSignal.connect(self.clickBtnStartAndStop)
        
        self.schedule = BattleSchedule(self.adb, self.cwd, self.userDataPath, self.ico) #处于测试
        self.schedule.errorSignal.connect(self.clickBtnStartAndStop)
        
        self.task = Task(self.adb, self.cwd, self.ico, self.listGoTo)
        self.credit = Credit(self.adb, self.cwd, self.listGoTo)

        if path.exists(self.cwd + '/data.json'):
            self.initPc()
        else:
            self._data = None
            self.publicCall = None
            self.tbAutoPC.setEnabled(False)
            self.btnMonitorPublicCall.setEnabled(False)
        
        
        self.schJsonEditer = JsonEdit(self.userDataPath, self.ico)
        self.board = BlackBoard()

        self.afterInit_Q = AfterInit(self, self.cwd)
        self.afterInit_Q.boardNeedShow.connect(self.showMessage)
        self.afterInit_Q.reloadPcModule.connect(self.initPc)

    def initPc(self):
        try:
            with open(self.cwd + '/data.json', 'r', encoding = 'gbk') as f:
                temp = f.read()
        except UnicodeDecodeError:
            with open(self.cwd + '/data.json', 'r', encoding = 'UTF-8') as f:
                temp = f.read()
        self._data = loads(temp)
        self.publicCall = UIPublicCall(self.adb, self.battle, self.cwd, self.btnMonitorPublicCall, 
                    self.listGoTo, self._data['data'][0]['normal'], self._data['data'][0]['high']) #公开招募
        self.publicCall.setStar(1, 1, self.config.getboolean('function', 'autoPC_skip1Star')) #自动公招保留一星设定
        self.publicCall.setStar(5, 1, self.config.getboolean('function', 'autoPC_skip5Star'))
        self.tbAutoPC.setEnabled(True)
        self.btnMonitorPublicCall.setEnabled(True)

    def initSlrSel(self):
        '初始化模拟器选择'
        slrName = self.config.get('connect', 'simulator')
        if slrName == 'bluestacks':
            self.actSlrBlueStacks.setIcon(QIcon(self.selectedPNG))
        elif slrName == 'mumu':
            self.actSlrMumu.setIcon(QIcon(self.selectedPNG))
        elif slrName == 'yeshen':
            self.actSlrYeshen.setIcon(QIcon(self.selectedPNG))
        elif slrName == 'xiaoyao':
            self.actSlrXiaoyao.setIcon(QIcon(self.selectedPNG))
        elif slrName == 'leidian':
            self.actSlrLeidian.setIcon(QIcon(self.selectedPNG))
        elif slrName == 'custom':
            self.actSlrCustom.setIcon(QIcon(self.selectedPNG))


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
    
    def functionSetMeun(self):
        self.source = self.sender()
        rightClickMeun = QMenu()
        rightClickMeun.setStyleSheet('''QMenu {color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                        background-color:#272626; margin:3px;}
                                        QMenu:item {padding:8px 32px;}
                                        QMenu:item:selected { background-color: #3f4140;}
                                        QMenu:icon{padding: 8px 20px;}
                                        QMenu:separator{background-color: #7C7C7C; height:1px; margin-left:2px; margin-right:2px;}''')
        if self.source == self.tbBattle:
            if self.config.getboolean('function', 'battle'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            rightClickMeun.addAction(self.actBattleTimes)
            rightClickMeun.addAction(self.line)
        elif self.source.text() == '计划战斗':
            if self.config.getboolean('function', 'schedule'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            rightClickMeun.addAction(self.actSchJson)
            rightClickMeun.addAction(self.line)
        elif self.source.text() == '自动公招':
            if self.config.getboolean('function', 'autoPC'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
            #自动招募和自动聘用
            rightClickMeun.addAction(self.actAutoSearch)
            rightClickMeun.addAction(self.actAutoEmploy)
            rightClickMeun.addAction(self.actSkipStar1)
            rightClickMeun.addAction(self.actSkipStar5)
            rightClickMeun.addAction(self.line)
        elif self.source.text() == '任务交付':
            if self.config.getboolean('function', 'task'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '获取信用':
            if self.config.getboolean('function', 'credit'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '公开招募计算器':
            if self.config.getboolean('function', 'publiccall'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '完成后关机':
            if self.config.getboolean('function', 'shutdown'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        self.actionSetDeafult = rightClickMeun.addAction(text)
        self.actionSetDeafult.triggered.connect(self.setDefault)
        rightClickMeun.exec_(QCursor.pos())
    
    def setDefault(self):
        if self.source.text() == '战斗':
            key = 'battle'
            value = not self.config.getboolean('function', 'battle')
        elif self.source.text() == '计划战斗':
            key = 'schedule'
            value = not self.config.getboolean('function', 'schedule')
        elif self.source.text() == '自动公招':
            key = 'autoPC'
            value = not self.config.getboolean('function', 'autoPC')
        elif self.source.text() == '任务交付':
            key = 'task'
            value = not self.config.getboolean('function', 'task')
        elif self.source.text() == '获取信用':
            key = 'credit'
            value = not self.config.getboolean('function', 'credit')
        elif self.source.text() == '公开招募计算器':
            key = 'publiccall'
            value = not self.config.getboolean('function', 'publiccall')
        elif self.source.text() == '完成后关机':
            key = 'shutdown'
            value = not self.config.getboolean('function', 'shutdown')

        self.changeDefault(key, value)
    
    def functionSel(self, isChecked):
        source = self.sender()
        #if '战斗：' in source.text():
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

    def setAutoPCFunc(self):
        source = self.sender()
        if source.text() == '自动招募':
            self.publicCall.searchFlag = not self.publicCall.searchFlag
            if self.publicCall.searchFlag:
                source.setIcon(QIcon(self.selectedPNG))
            else:
                source.setIcon(QIcon(''))
        elif source.text() == '自动聘用':
            self.publicCall.employFlag = not self.publicCall.employFlag
            if self.publicCall.employFlag:
                source.setIcon(QIcon(self.selectedPNG))
            else:
                source.setIcon(QIcon(''))
        elif source.text() == '保留1星':
            self.publicCall.setStar(1, 1, not self.publicCall.setStar(1, 0))
            if self.publicCall.setStar(1,0):
                source.setIcon(QIcon(self.selectedPNG))
                self.changeDefault('autopc_skip1star', True)
            else:
                source.setIcon(QIcon(''))
                self.changeDefault('autopc_skip1star', False)
        elif source.text() == '保留5星':
            self.publicCall.setStar(5, 1, not self.publicCall.setStar(5, 0))
            if self.publicCall.setStar(5,0):
                source.setIcon(QIcon(self.selectedPNG))
                self.changeDefault('autopc_skip5star', True)
            else:
                source.setIcon(QIcon(''))
                self.changeDefault('autopc_skip5star', False)
    
    def openSchEdit(self):
        self.schJsonEditer.editerShow()
    
    def monitorPC(self, isChecked):
        if isChecked:
            self.publicCall.turnOn()
        else:
            self.publicCall.turnOff()

    def changeSlr(self, name, port, ip = '127.0.0.1'):
        self.config.set('connect', 'simulator', name)
        self.config.set('connect', 'port', port)
        self.config.set('connect', 'ip', ip)
        
        configInI = open(self.configPath, 'w')
        self.config.write(configInI)
        configInI.close()
        self.adb.changeConfig(self.config)

    def changeDefault(self, func, flag, sec = 'function'):
        self.config.set(sec, func, str(flag))
        configInI = open(self.configPath, 'w')
        self.config.write(configInI)
        configInI.close()


    def simulatorSel(self):
        slrName = self.sender().text()
        if slrName == '蓝叠模拟器':
            self.changeSlr('bluestacks', '5555')
        elif slrName == 'Mumu模拟器':
            self.changeSlr('mumu', '7555')
        elif slrName == '夜神模拟器':
            noxPath = QFileDialog.getOpenFileName(None, '选取文件', './', '夜神模拟器程序 (Nox.exe)')
            noxPath = path.dirname(noxPath[0])
            self.changeDefault('noxPath', noxPath, sec = 'connect')
            self.changeSlr('yeshen', '59865')
        elif slrName == '逍遥模拟器':
            self.changeSlr('xiaoyao', '21503')
        elif slrName == '雷电模拟器':
            self.changeSlr('leidian', '5555')
        else:
            customIp, isOk = QInputDialog.getText(self, '自定义', '请输入模拟器IP地址')
            if isOk:
                customPort, isOk = QInputDialog.getText(self, '自定义', '请输入模拟器端口号')
                if isOk:
                    self.changeSlr('custom', customPort, customIp)

        for each in self.slrList:
            each.setIcon(QIcon(''))

        self.initSlrSel()
        
    def exit(self):
        '退出按钮'
        self.schJsonEditer.close()
        self.hide()
        self.stop()
        self.console.close()
        if self.publicCall != None:
            self.publicCall.close()
        self.adb.killAdb()
        #self.close()
        sys.exit() #为了解决Error in atexit._run_exitfuncs:的问题，实际上我完全不知道这为什么出现

    def minimize(self):
        '最小化按钮'
        self.showMinimized()

    def openUpdate(self):
        openUrl('https://www.lanzous.com/b0d1w6v7g')

    def openIndex(self):
        openUrl('https://github.com/MangetsuC/arkHelper')
                
    def showMessage(self):
        self.changeDefault('md5', self.noticeMd5, sec = 'notice')
        self.board.updateText(self._notice)
        self.board.show()
        #弹出公告

    def startUpdate(self):
        if path.exists(self.cwd + '/update.exe'):
            selfPidList = self.adb.cmd.getTaskList('arkhelper.exe')
            updateJson = {'localPath': self.cwd, 
                            'onlinePath': self._updateData['onlinePath'] + '/v' +self._updateData['version'],
                            'Pid': ','.join(selfPidList),
                            'exceptionFile': self._updateData['exception']}
            with open('updateData.json', 'w', encoding='UTF-8') as f:
                f.write(dumps(updateJson, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
            startfile('update.exe')
    
    def battleWarning(self):
        reply = QMessageBox.warning(self, '警告', '发现您选中的关卡可能无掉落，是否继续？', 
                                    QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            self.battle.stop()
        elif reply == QMessageBox.Yes:
            self.battle.isUselessContinue = True
        self.battle.isWaitingUser = False

    def testUpdate(self):
        version, isOk = QInputDialog.getText(self, '???', '神秘代码')
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
        if self.doctorFlag and self.taskFlag:
            self.task.run(self.doctorFlag)
        if self.doctorFlag and self.creditFlag:
            self.credit.run(self.doctorFlag)
        if self.shutdownFlag and self.doctorFlag:
            self.adb.cmd.shutdown(time=120)
            self.exit()
        else:
            self.stop()

    def stop(self):
        self.doctorFlag = False
        if self.publicCall != None:
            self.publicCall.autoPCStop()
        self.schedule.stop()
        self.battle.stop()
        self.task.stop()
        self.credit.stop()
        self.btnMainClicked = False
        self.btnStartAndStop.setText('启动虚拟博士')

    def clickBtnStartAndStop(self):
        self.btnMainClicked = not self.btnMainClicked
        if self.btnMainClicked:
            self.btnStartAndStop.setText('停止虚拟博士')
            self.thRun = Thread(target=self.start)
            self.thRun.setDaemon(True)
            self.thRun.start()
        else:
            self.stop()  
            self.thRun.join()

if __name__ == '__main__':
    cgitb.enable(format = 'text')
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    exLaunch = Launch()
    app.processEvents()
    ex = App()
    exLaunch.finish(ex)
    ex.afterInit_Q.start()
    sys.exit(app.exec_())
