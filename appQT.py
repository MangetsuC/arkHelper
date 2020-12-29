import sys
from configparser import ConfigParser
from json import dumps, loads
from os import getcwd, path, getlogin, mkdir
from threading import Thread
from webbrowser import open as openUrl
from urllib import request

from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QCursor, QIcon, QMouseEvent, QScreen
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QDesktopWidget,
                             QGridLayout, QInputDialog, QLabel, QMenu,
                             QPushButton, QWidget, QMessageBox)

from foo.adb.adbCtrl import Adb
from foo.arknight.Battle import BattleLoop
from foo.arknight.credit import Credit
from foo.arknight.Schedule import BattleSchedule
from foo.arknight.task import Task
from foo.ui.console import Console
from foo.ui.launch import Launch, BlackBoard
from foo.ui.UIPublicCall import UIPublicCall
from foo.ui.UIschedule import JsonEdit
from foo.pictureR import pictureFind


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.ver = '2.5.1'
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
        self.cwd = getcwd().replace('\\', '/')
        self.userDataPath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper'
        if path.exists(self.cwd + '/config.ini'):
            self.userDataPath = self.cwd #便于调试时不改变实际使用的配置
        elif not path.exists(self.userDataPath):
            mkdir(self.userDataPath)
        
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
        #self.setFixedSize(522,196)
        self.resize(597,196)
        

        self.setWindowFlag(Qt.FramelessWindowHint) #隐藏边框
        self.setStyleSheet('''App{background:#272626}QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:9pt;}
                                QPushButton{border:0px;background:#4d4d4d;color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QPushButton:pressed{background:#606162;font:9pt;}
                                QPushButton:checked{background:#70bbe4;}
                                QInputDialog{background-color:#272626;}''')

        
        self.btnStartAndStop = QPushButton('启动虚拟博士', self) #启动/停止按钮
        self.btnStartAndStop.setFixedSize(180, 131)
        self.btnStartAndStop.setStyleSheet('''QPushButton{font:13pt;}''')
        self.btnStartAndStop.clicked.connect(self.clickBtnStartAndStop)

        self.btnMonitorPublicCall = QPushButton('公开招募计算器', self)
        self.btnMonitorPublicCall.setFixedSize(180, 40)
        self.btnMonitorPublicCall.setCheckable(True)
        self.btnMonitorPublicCall.clicked[bool].connect(self.monitorPC)

        self.tbBattle = QPushButton('战斗', self) #战斗可选按钮
        self.tbBattle.setCheckable(True)
        self.tbBattle.setFixedSize(75, 40)
        self.tbBattle.clicked[bool].connect(self.functionSel)

        self.tbSchedule = QPushButton('计划战斗', self) #计划战斗可选按钮
        self.tbSchedule.setCheckable(True)
        self.tbSchedule.setFixedSize(75, 40)
        self.tbSchedule.clicked[bool].connect(self.functionSel)

        self.tbAutoPC = QPushButton('自动公招', self) #自动公招可选按钮
        self.tbAutoPC.setCheckable(True)
        self.tbAutoPC.setFixedSize(75, 40)
        self.tbAutoPC.clicked[bool].connect(self.functionSel)

        self.tbAutoSearch = QPushButton('自动招募', self) #自动公招可选按钮 招募部分
        self.tbAutoSearch.setCheckable(True)
        self.tbAutoSearch.setFixedSize(75, 40)
        self.tbAutoSearch.clicked[bool].connect(self.functionSel)
        self.tbAutoSearch.setChecked(True)

        self.tbAutoEmploy = QPushButton('自动聘用', self) #自动公招可选按钮 聘用部分
        self.tbAutoEmploy.setCheckable(True)
        self.tbAutoEmploy.setFixedSize(75, 40)
        self.tbAutoEmploy.clicked[bool].connect(self.functionSel)
        self.tbAutoEmploy.setChecked(True)

        self.btnSchJson = QPushButton('路线规划', self) #更改计划json
        self.btnSchJson.setFixedSize(155, 40)
        self.btnSchJson.clicked.connect(self.openSchEdit)

        self.tbTask = QPushButton('任务交付', self) #任务交付可选按钮
        self.tbTask.setCheckable(True)
        self.tbTask.setFixedSize(75, 40)
        self.tbTask.clicked[bool].connect(self.functionSel)

        self.tbCredit = QPushButton('获取信用', self)
        self.tbCredit.setCheckable(True)
        self.tbCredit.setFixedSize(75, 40)
        self.tbCredit.clicked[bool].connect(self.functionSel)

        self.tbShutdown = QPushButton('完成后关机', self)
        self.tbShutdown.setCheckable(True)
        self.tbShutdown.setFixedSize(155, 40)
        self.tbShutdown.clicked[bool].connect(self.functionSel)

        self.btnSet = QPushButton('设置',self) #设置按钮
        self.btnSet.setFixedSize(75, 40)

        self.settingMenu = QMenu() #创建设置按钮菜单
        self.settingMenu.setStyleSheet('''QMenu {color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;background-color:#222724; margin:3px;}
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
        self.actCheckUpdate = QAction('检查更新', parent=self.settingMenu)
        self.actIndex = QAction('访问主页', parent=self.settingMenu)
        
        #self.actVersion1 = QAction('版本：', parent=self.settingMenu)
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

        #self.settingMenu.addAction(self.actVersion1)
        self.settingMenu.addAction(self.actVersion2) #版本号显示

        self.btnSet.setMenu(self.settingMenu) #关联按钮与菜单
        self.btnSet.setStyleSheet('''QPushButton:menu-indicator{image:none;width:0px;}''')

        self.btnMin = QPushButton('最小化',self) #最小化按钮
        self.btnMin.setFixedSize(75, 40)
        self.btnMin.clicked.connect(self.minimize)

        self.btnClose = QPushButton('退出',self) #退出按钮
        self.btnClose.setFixedSize(75, 85)
        self.btnClose.clicked.connect(self.exit)

        self.btnShowBoard = QPushButton('有新公告！',self)
        self.btnShowBoard.setFixedSize(75, 40)
        self.btnShowBoard.clicked.connect(self.showMessage)
        self.btnShowBoard.hide()
        
        self.lNotice = QLabel('按此处可拖动窗口')

        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(5)
        self.grid.setHorizontalSpacing(5)
        
        self.grid.addWidget(self.btnStartAndStop, 0, 0, 3, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btnMonitorPublicCall, 3, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbBattle, 0, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbSchedule, 0, 4, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbAutoPC, 0, 5, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbTask, 0, 2, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btnSet, 2, 2, 1,1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbCredit, 0, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbShutdown, 1, 2, 1, 2)
        self.grid.addWidget(self.btnMin, 1, 4, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btnClose, 1, 5, 2, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbAutoSearch, 1, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.tbAutoEmploy, 2, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btnSchJson, 2, 3, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btnShowBoard, 3, 1, 1, 1, alignment=Qt.AlignRight)
        self.grid.addWidget(self.lNotice, 3, 4, 1, 2, alignment=Qt.AlignRight)

        self.setLayout(self.grid)

        #self.show()

    def initRightClickMeun(self):
        #战斗按钮
        self.tbBattle.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbBattle.customContextMenuRequested.connect(self.functionDefaultSetMeun)
        #计划战斗按钮
        self.tbSchedule.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbSchedule.customContextMenuRequested.connect(self.functionDefaultSetMeun)
        #自动公招按钮
        self.tbAutoPC.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbAutoPC.customContextMenuRequested.connect(self.functionDefaultSetMeun)
        #任务按钮
        self.tbTask.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbTask.customContextMenuRequested.connect(self.functionDefaultSetMeun)
        #信用按钮
        self.tbCredit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbCredit.customContextMenuRequested.connect(self.functionDefaultSetMeun)
        #自动关机按钮
        self.tbShutdown.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbShutdown.customContextMenuRequested.connect(self.functionDefaultSetMeun)
        #公开招募按钮
        self.btnMonitorPublicCall.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btnMonitorPublicCall.customContextMenuRequested.connect(self.functionDefaultSetMeun)

    def initVar(self):
        self.ico = self.cwd + '/res/ico.ico'
        self.selectedPNG = self.cwd + '/res/gui/selected.png'
        self.unSelPNG = self.cwd + '/res/gui/unSelected.png'

        self.__data = None

        self.console = Console(self.cwd) #接管输出与报错

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
        self.actMaxNumber.setText(f'设置上限（当前：{self.stoneMaxNum}）')
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
        if self.PCFlag:
            self.publicCall.turnOn()
        pass
    
    def initClass(self):
        self.adb = Adb(self.cwd + '/bin/adb', self.config)
        self.battle = BattleLoop(self.adb, self.cwd, self.ico)
        self.schedule = BattleSchedule(self.adb, self.cwd, self.ico) #处于测试
        self.task = Task(self.adb, self.cwd, self.ico, self.listGoTo)
        self.credit = Credit(self.adb, self.cwd, self.listGoTo)
        with open(self.cwd + '/data.json', 'r') as f:
            temp = f.read()
        self.__data = loads(temp)
        self.publicCall = UIPublicCall(self.adb, self.battle, self.cwd, self.btnMonitorPublicCall, self.listGoTo, self.__data['data'][0]['normal'], self.__data['data'][0]['high']) #公开招募
        self.schJsonEditer = JsonEdit(self.ico)
        self.board = BlackBoard()

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
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.globalPos() - self.pos() #获取鼠标相对窗口的位置
            #print(self.mousePos.x(),self.mousePos.y()) #调试参考选择可移动区域
            if self.mousePos.x() > 190 and self.mousePos.y() > 150: #判断是否在可移动区域
                self.moveFlag = True
            else:
                self.moveFlag = False
            event.accept()
            
    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.moveFlag:  
            self.move(QMouseEvent.globalPos() - self.mousePos) #更改窗口位置
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        #停止窗口移动
        self.moveFlag = False
    
    def functionDefaultSetMeun(self):
        self.source = self.sender()
        if self.source.text() == '战斗':
            if self.config.getboolean('function', 'battle'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '计划战斗':
            if self.config.getboolean('function', 'schedule'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
        elif self.source.text() == '自动公招':
            if self.config.getboolean('function', 'autoPC'):
                text = '设为默认关闭'
            else:
                text = '设为默认开启'
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
        self.contextMenu = QMenu()
        self.actionSetDeafult = self.contextMenu.addAction(text)
        self.actionSetDeafult.triggered.connect(self.setDefault)
        self.contextMenu.setStyleSheet('''QMenu {color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;background-color:#222724; margin:3px;}
                                        QMenu:item {padding:6px 15px;}
                                        QMenu:item:selected { background-color: #3f4140;}''')
        self.contextMenu.exec_(QCursor.pos())
    
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
        if source.text() == '战斗':
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
            self.changeSlr('yeshen', '62026')
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
        self.console.exit()
        self.publicCall.close()
        self.adb.killAdb()
        self.close()

    def minimize(self):
        '最小化按钮'
        self.showMinimized()

    def openUpdate(self):
        openUrl('https://www.lanzous.com/b0d1w6v7g')

    def openIndex(self):
        openUrl('https://github.com/MangetsuC/arkHelper')

    def checkUpdate(self):
        try:
            self.content = request.urlopen('http://shakuras.3vkj.net/').read().decode('utf-8')
        except request.URLError as eReason:
            print(eReason.reason)
            self.content = 'failed to get content'
        else:
            if '[version]' in self.content:
                newVersion = self.content.split('[version]')[1].split('.')
                tempSelfVersion = self.ver.split('.')
                ver0 = int(newVersion[0]) == int(tempSelfVersion[0])
                ver1 = int(newVersion[1]) == int(tempSelfVersion[1])
                ver2 = int(newVersion[2]) == int(tempSelfVersion[2])
                if ver0:
                    if ver1:
                        if not ver2:
                            if int(newVersion[2]) > int(tempSelfVersion[2]):
                                self.lNotice.setText('*有新版本*')
                    else:
                        if int(newVersion[1]) > int(tempSelfVersion[1]):
                                self.lNotice.setText('*有新版本*')
                else:
                    if int(newVersion[0]) > int(tempSelfVersion[0]):
                                self.lNotice.setText('*有新版本*')

    def checkMessage(self):
        if self.content != 'failed to get content':
            msgVer = self.content.split('[msgVer]')[1]
            if (not self.config.has_option('notice', 'msgver')) or self.config.getint('notice', 'msgver') < int(msgVer):
                self.btnShowBoard.show()

    def checkPublicCallData(self):
        if self.content != 'failed to get content':
            if '[normal]' in self.content and '[high]' in self.content:
                tempNormal = self.content.split('[normal]')[1]
                tempHigh = self.content.split('[high]')[1]
                tempData = loads("{\"data\":[{\"normal\":" + tempNormal + ",\"high\":" + tempHigh + "}]}")
                if tempData != self.__data:
                    with open(self.cwd + '/data.json', 'w') as f:
                        f.write(dumps(tempData, ensure_ascii=False))
                    self.publicCall.updateTag()
                
    def showMessage(self):
        msgVer = self.content.split('[msgVer]')[1]
        if not self.config.has_section('notice'):
            self.config.add_section('notice')
        self.changeDefault('msgver', msgVer, sec = 'notice')
        #self.changeDefault('msgver', '1', sec = 'notice')
        msg = self.content.split('[text]')[1]
        self.board.updateText(msg)
        self.board.show()
        #弹出公告

    def checkAll(self):
        if self.config.getboolean('notice', 'enable'):
            self.checkUpdate()
            self.checkMessage()
            self.checkPublicCallData()

    def afterInit(self):
        thAfterInit = Thread(target=self.checkAll)
        thAfterInit.setDaemon(True)
        thAfterInit.start()
    
    def start(self):
        self.doctorFlag = self.battle.connect()
        if self.doctorFlag and self.scheduleFlag:
            self.schedule.run(self.doctorFlag)
        if self.doctorFlag and self.battleFlag:
            self.battle.run(self.doctorFlag)
        if self.doctorFlag and self.autoPCFlag:
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

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    exLaunch = Launch()
    app.processEvents()
    ex = App()
    exLaunch.finish(ex)
    ex.afterInit()
    sys.exit(app.exec_())
