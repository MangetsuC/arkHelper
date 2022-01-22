import sys
from json import dumps, loads
from os import getcwd

from PySide6.QtCore import QStringListModel, Qt, QTimer
from PySide6.QtGui import QIcon, QCursor, QAction
from PySide6.QtWidgets import (QApplication, QComboBox, #QDesktopWidget,
                             QGridLayout, QInputDialog, QLabel, QLineEdit,
                             QListView, QMenu, QPushButton, QWidget)

from foo.ui.screen import ScreenRateMonitor
from foo.ui.messageBox import AMessageBox
from common import schedule_data, theme


class JsonEdit(QWidget):
    def __init__(self, app, ico, parent = None, flags = Qt.WindowCloseButtonHint):
        super(JsonEdit, self).__init__(parent, flags)
        if theme != None:
            self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;}}
                                QPushButton{{border:0px;background:{theme.getFgColor()};color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:11pt;}}
                                QPushButton:pressed{{background:{theme.getPressedColor()};font:10pt;}}
                                QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()};}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                QLineEdit{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;border:0px;padding-left:5px}}
                                QLineEdit:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};padding-left:4px;}}
                                QListView{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
                                QComboBox:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};padding-left:4px;}}
                                QComboBox{{background-color:{theme.getFgColor()};color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;padding-left:5px;border:0px;}}
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

        self.app = app

        self.setWindowIcon(QIcon(ico))
        self.isshow = False

        self.isBootyMode = False
        self.bootyName = '固源岩'

        self.selPanel = BootyChoice(self, ico, theme = theme)

        #self.json = dataPath + '/schedule.json'
        self.scheduleAdd = {'part':'MAIN', 'chap':'', 'objLevel':'', 'times':''}
        self.transEX = {'ex1':'切尔诺伯格','ex2':'龙门外环','ex3':'龙门市区','ex4':'当期委托'}

        self.partList = ['主线','物资筹备','芯片搜索','剿灭作战','选定关卡']
        self.partListJson = ['MAIN','RS','PR','EX','THIS']
        self.mainChapList = ['序章','第一章','第二章','第三章','第四章','第五章','第六章','第七章','第八章','第九章']
        self.rsChapList = ['战术演习','粉碎防御','空中威胁','货物运送','资源保障']
        self.prChapList = ['医疗重装','术士狙击','辅助先锋','特种近卫']
        self.exChapList = ['切尔诺伯格','龙门外环','龙门市区','当期委托']
        self.chapList = [self.mainChapList,self.rsChapList,self.prChapList,self.exChapList]

        self.selIndex = None
        
        self.grid = QGridLayout()
        self.lsv = QListView() #计划显示框
        self.lsv.setMinimumWidth(self.getRealSize(200))
        self.lsv.clicked.connect(self.clickSchedule)
        self.lsv.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lsv.customContextMenuRequested.connect(self.lsvRearrange)
        self.actMoveUp = QAction('上移')
        self.actMoveUp.triggered.connect(self.moveUpLine)
        self.actMoveDown = QAction('下移')
        self.actMoveDown.triggered.connect(self.moveDownLine)
        self.actEdit = QAction('修改次数/个数')
        self.actEdit.triggered.connect(self.editLine)
        self.actDel = QAction('删除')
        self.actDel.triggered.connect(self.delLine)

        self.slm = QStringListModel()

        self.partCb = QComboBox()
        self.partCb.addItems(self.partList)
        self.partCb.activated[int].connect(self.changeChapList)
        self.partCb.setFixedWidth(self.getRealSize(80))
        self.partCb.setMinimumHeight(self.getRealSize(40))
        self.partCb.setView(QListView())

        self.chapCb = QComboBox()
        self.chapCb.addItems(self.mainChapList)
        self.chapCb.activated[int].connect(self.changeLevel1List)
        self.chapCb.setFixedWidth(self.getRealSize(100))
        self.chapCb.setMinimumHeight(self.getRealSize(40))
        self.chapCb.setView(QListView())

        self.level1Cb = QComboBox()
        self.level1Cb.setFixedWidth(self.getRealSize(60))
        self.level1Cb.setMinimumHeight(self.getRealSize(40))
        self.level1Cb.setView(QListView())

        self.level1Edit = QLineEdit()
        self.level1Edit.setFixedWidth(self.getRealSize(60))
        self.level1Edit.setMinimumHeight(self.getRealSize(40))

        self.lineLable = QLabel()
        self.lineLable.setText('-')

        self.level2Edit = QLineEdit()
        self.level2Edit.setFixedWidth(self.getRealSize(60))
        self.level2Edit.setMinimumHeight(self.getRealSize(40))

        self.timesLable = QLabel()
        self.timesLable.setText('次数:')

        self.timeEdit = QLineEdit()
        self.timeEdit.setFixedWidth(self.getRealSize(50))
        self.timeEdit.setMinimumHeight(self.getRealSize(40))

        self.bootyModeBtn = QPushButton()
        self.bootyModeBtn.setCheckable(True)
        self.bootyModeBtn.setText('素材模式')
        self.bootyModeBtn.setMinimumHeight(self.getRealSize(40))
        self.bootyModeBtn.clicked[bool].connect(self.setBootMode)

        self.bootySelEdit = QLineEdit()
        self.bootySelEdit.setText('非素材模式')
        self.bootySelEdit.setEnabled(False)
        self.bootySelEdit.setMinimumHeight(self.getRealSize(40))

        self.bootySelBtn = QPushButton()
        self.bootySelBtn.setText('——')
        self.bootySelBtn.setMinimumHeight(self.getRealSize(40))
        self.bootySelBtn.clicked.connect(self.selPanel.myShow)

        self.delBtn = QPushButton()
        self.delBtn.setText('删除')
        self.delBtn.clicked.connect(self.delLine)
        self.delBtn.setMinimumHeight(self.getRealSize(40))
        self.clearBtn = QPushButton()
        self.clearBtn.setText('清空')
        self.clearBtn.clicked.connect(self.clearLine)
        self.clearBtn.setMinimumHeight(self.getRealSize(40))

        self.addBtn = QPushButton()
        self.addBtn.setText('添加')
        self.addBtn.clicked.connect(self.addLine)
        self.addBtn.setMinimumHeight(self.getRealSize(40))

        self.planCb = QComboBox()
        self.planCb.setMinimumSize(self.getRealSize(200), self.getRealSize(40))
        self.planCb.setView(QListView())

        self.loadPlanBtn = QPushButton()
        self.loadPlanBtn.setText('加载配置')
        self.loadPlanBtn.setMinimumHeight(self.getRealSize(40))
        self.loadPlanBtn.clicked.connect(self.loadPlan)

        self.addPlanBtn = QPushButton()
        self.addPlanBtn.setText('以当前配置新建')
        self.addPlanBtn.setMinimumHeight(self.getRealSize(40))
        self.addPlanBtn.clicked.connect(self.addPlan)

        self.delPlanBtn = QPushButton()
        self.delPlanBtn.setText('删除此配置')
        self.delPlanBtn.setMinimumHeight(self.getRealSize(40))
        self.delPlanBtn.clicked.connect(self.delPlan)

        self.listScheduleBefore = []
        self.listSchedule = []
        self.initJson()
        self.slm.setStringList(self.listSchedule)
        self.lsv.setModel(self.slm)
        self.lsv.setEditTriggers(QListView.NoEditTriggers)

        self.changeLevel1List(0)

        self.grid.addWidget(self.lsv,0,0,3,1)
        self.grid.addWidget(self.partCb,0,1,1,1)
        self.grid.addWidget(self.chapCb,0,2,1,1)
        self.grid.addWidget(self.level1Edit,0,3,1,1)
        self.grid.addWidget(self.lineLable,0,4,1,1)
        self.grid.addWidget(self.level2Edit,0,5,1,1)
        self.grid.addWidget(self.timesLable,0,6,1,1)
        self.grid.addWidget(self.timeEdit,0,7,1,1)
        self.grid.addWidget(self.bootyModeBtn,1,1,1,1)
        self.grid.addWidget(self.bootySelEdit,1,2,1,4)
        self.grid.addWidget(self.addBtn,1,6,1,2)
        self.grid.addWidget(self.delBtn,2,1,1,4)
        self.grid.addWidget(self.clearBtn,2,5,1,3)
        self.grid.addWidget(self.planCb,3,0,1,1)
        self.grid.addWidget(self.loadPlanBtn,3,1,1,1)
        self.grid.addWidget(self.addPlanBtn,3,2,1,3)
        self.grid.addWidget(self.delPlanBtn,3,5,1,3)

        self.setLayout(self.grid)

        self.setWindowTitle('路线规划')
        #self.resize(600,400)

        self.myTimer()

        self.setMaximumHeight(self.getRealSize(200))

    def getRealSize(self, size):
        rate = 1#self.app.screens()[QDesktopWidget().screenNumber(self)].logicalDotsPerInch()/96
        if rate < 1.1:
            rate = 1.0
        elif rate < 1.4:
            rate = 1.5
        elif rate < 1.8:
            rate = 1.75
        else:
            rate = 2
        
        return int(size * rate)

    def resizeUI(self):
        self.setMaximumHeight(self.getRealSize(200))
        self.lsv.setMinimumWidth(self.getRealSize(80))
        self.partCb.setFixedWidth(self.getRealSize(80))
        self.partCb.setMinimumHeight(self.getRealSize(40))
        self.chapCb.setFixedWidth(self.getRealSize(100))
        self.chapCb.setMinimumHeight(self.getRealSize(40))
        self.level1Cb.setFixedWidth(self.getRealSize(60))
        self.level1Cb.setMinimumHeight(self.getRealSize(40))
        self.level1Edit.setFixedWidth(self.getRealSize(60))
        self.level1Edit.setMinimumHeight(self.getRealSize(40))
        self.level2Edit.setFixedWidth(self.getRealSize(60))
        self.level2Edit.setMinimumHeight(self.getRealSize(40))
        self.timeEdit.setFixedWidth(self.getRealSize(50))
        self.timeEdit.setMinimumHeight(self.getRealSize(40))
        self.bootyModeBtn.setMinimumHeight(self.getRealSize(40))
        self.bootySelEdit.setMinimumHeight(self.getRealSize(40))
        self.bootySelBtn.setMinimumHeight(self.getRealSize(40))
        self.delBtn.setMinimumHeight(self.getRealSize(40))
        self.clearBtn.setMinimumHeight(self.getRealSize(40))
        self.addBtn.setMinimumHeight(self.getRealSize(40))
        self.planCb.setMinimumSize(self.getRealSize(200), self.getRealSize(40))
        self.loadPlanBtn.setMinimumHeight(self.getRealSize(40))
        self.addPlanBtn.setMinimumHeight(self.getRealSize(40))
        self.delPlanBtn.setMinimumHeight(self.getRealSize(40))

    def editerShow(self):
        if not self.isVisible():
            self.show()
            #cp = QDesktopWidget().availableGeometry().center()
            #self.move(int(cp.x() - self.width()/2), int(cp.y() - self.height()/2))

    def myTimer(self):
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateList)
        self.updateTimer.start(10)

    def lsvRearrange(self):
        self.selIndex = self.lsv.currentIndex().row()
        rightClickMeun = QMenu()
        rightClickMeun.setStyleSheet(f'''QMenu {{color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                        background-color:#272626; margin:3px;}}
                                        QMenu:item {{padding:8px 32px;}}
                                        QMenu:item:selected {{ background-color: #3f4140;}}
                                        QMenu:icon{{padding: 8px 20px;}}
                                        QMenu:separator{{background-color: #7C7C7C; height:1px; margin-left:2px; margin-right:2px;}}''')
        rightClickMeun.addAction(self.actMoveUp)
        rightClickMeun.addAction(self.actMoveDown)
        rightClickMeun.addAction(self.actEdit)
        rightClickMeun.addAction(self.actDel)
        rightClickMeun.exec_(QCursor.pos())
        
    
    def initJson(self):
        #with open(self.json,'r', encoding='UTF-8') as s:
        #    data = s.read()
        self.jsonAll = schedule_data.get('main')
        self.selPlan = self.jsonAll[0]
        self.allPlanList = self.selPlan['allplan'].split('|')

        #配置选单显示
        self.planCb.addItems(self.allPlanList)

        self.jsonDict = self.jsonAll[0]['sel']
        self.selList = self.jsonDict.copy()
        self.refreshJsonView()

    def refreshJsonView(self):
        self.listSchedule = []
        for eachDict in self.selList:
            temp = eachDict['objLevel']
            if 'ex' in temp:
                temp = self.transEX[temp]
            elif temp == 'this':
                temp = '选定关卡'
            if eachDict['chap'] == 'LS':
                temp = temp.replace('S', 'LS')
            if isinstance(eachDict['times'], dict):
                self.listSchedule.append('{0}（{1}共{2}个）'.format(temp,eachDict['times']['bootyName'],eachDict['times']['bootyNum']))
            else:
                self.listSchedule.append('{0}（共{1}次）'.format(temp,eachDict['times']))

    def updateJson(self):
        self.jsonAll[0]['sel'] = self.selList.copy()
        self.jsonAll[0]['allplan'] = '|'.join(self.allPlanList)
        #self.jsonAll[0]['selno'] = str(self.selNo)
        schedule_data.change('main', self.jsonAll)
        '''newData = dumps(tempNewJson, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        with open(self.json,'w', encoding = 'UTF-8') as j:
            j.write(newData)'''


    def updateList(self):
        if self.listSchedule != self.listScheduleBefore:
            self.listScheduleBefore = self.listSchedule.copy()
            self.slm.setStringList(self.listSchedule)
            self.updateJson()
    
    def changeChapList(self,indexI):
        self.scheduleAdd['part'] = self.partListJson[indexI]
        self.chapCb.clear()
        if indexI == 4:#当前关卡
            self.chapCb.setEnabled(False)
            self.level1Cb.clear()
            self.level1Cb.setEnabled(False)
            self.level1Edit.clear()
            self.level1Edit.setReadOnly(True)
            self.level2Edit.clear()
            self.level2Edit.setReadOnly(True)
            self.scheduleAdd['chap'] = 'this'
            self.scheduleAdd['objLevel'] = 'this'
            pass
        else:
            self.chapCb.setEnabled(True)
            self.level1Cb.setEnabled(True)
            self.chapCb.addItems(self.chapList[indexI])
            self.changeLevel1List(0)
    
    def changeLevel1List(self,indexI):
        self.level1Cb.clear()
        selChap = self.chapCb.currentText()
        self.level2Edit.setReadOnly(False)
        levelList = []
        if '章' in selChap:
            self.scheduleAdd['chap'] = str(int(indexI))
            if int(indexI) != 8:
                levelList.append(f'{int(indexI)}')
            if int(indexI) != 0 and int(indexI) != 1:
                if int(indexI) != 8:
                    levelList.append(f'S{int(indexI)}')
                elif int(indexI) == 8:
                    levelList.extend([f'R{int(indexI)}', f'M{int(indexI)}', f'JT{int(indexI)}'])

        elif selChap == '战术演习':
            self.scheduleAdd['chap'] = 'LS'
            levelList.append('LS')

        elif selChap == '粉碎防御':
            self.scheduleAdd['chap'] = 'AP'
            levelList.append('AP')

        elif selChap == '空中威胁':
            self.scheduleAdd['chap'] = 'CA'
            levelList.append('CA')

        elif selChap == '货物运送':
            self.scheduleAdd['chap'] = 'CE'
            levelList.append('CE')

        elif selChap == '资源保障':
            self.scheduleAdd['chap'] = 'SK'
            levelList.append('SK')

        elif selChap == '医疗重装':
            self.scheduleAdd['chap'] = 'A'
            levelList.append('PR-A')

        elif selChap == '术士狙击':
            self.scheduleAdd['chap'] = 'B'
            levelList.append('PR-B')

        elif selChap == '辅助先锋':
            self.scheduleAdd['chap'] = 'C'
            levelList.append('PR-C')

        elif selChap == '特种近卫':
            self.scheduleAdd['chap'] = 'D'
            levelList.append('PR-D')

        else:
            if selChap == '切尔诺伯格':
                self.scheduleAdd['chap'] = 'external'
                self.scheduleAdd['objLevel'] = 'ex1'
            elif selChap == '龙门外环':
                self.scheduleAdd['chap'] = 'external'
                self.scheduleAdd['objLevel'] = 'ex2'
            elif selChap == '龙门市区':
                self.scheduleAdd['chap'] = 'external'
                self.scheduleAdd['objLevel'] = 'ex3'
            elif selChap == '当期委托':
                self.scheduleAdd['chap'] = 'external'
                self.scheduleAdd['objLevel'] = 'ex4'

            self.level1Edit.clear()
            self.level1Edit.setReadOnly(True)
            self.level2Edit.clear()
            self.level2Edit.setReadOnly(True)

        self.level1Cb.addItems(levelList)
    
    def addLine(self):
        tempLevel = self.level2Edit.text()
        if self.scheduleAdd['part'] != 'EX' and self.scheduleAdd['part'] != 'THIS':
            self.scheduleAdd['objLevel'] = ''
        tempTimes = self.timeEdit.text()
        self.scheduleAdd['times'] = ''
        if tempLevel != '':
            part1 = self.level1Edit.text()
            if part1 == 'LS':
                part1 = 'S'
            if tempLevel.isdecimal():
                self.scheduleAdd['objLevel'] = part1 + '-' + tempLevel
        if tempTimes.isdecimal():
            if self.isBootyMode:
                #self.scheduleAdd['times'] = {'bootyName':self.bootyName,'bootyNum':tempTimes}
                self.scheduleAdd['times'] = {'bootyName':self.bootySelEdit.text(),'bootyNum':tempTimes}
            else:
                self.scheduleAdd['times'] = tempTimes
        if self.scheduleAdd['objLevel'] != '' and self.scheduleAdd['times'] != '':
            self.selList.append(self.scheduleAdd.copy())
            self.refreshJsonView()
    
    def clickSchedule(self,qModelIndex):
        self.selIndex = qModelIndex.row()

    def delLine(self):
        if self.selIndex != None:
            self.listSchedule.pop(self.selIndex)
            self.selList.pop(self.selIndex)
        self.selIndex = None

    def moveUpLine(self):
        if self.selIndex != 0 and self.selIndex != None:
            #temp = self.listSchedule[self.selIndex - 1]
            self.listSchedule[self.selIndex - 1], self.listSchedule[self.selIndex] = \
                                            self.listSchedule[self.selIndex], self.listSchedule[self.selIndex - 1]
            self.selList[self.selIndex - 1], self.selList[self.selIndex] = \
                                            self.selList[self.selIndex], self.selList[self.selIndex - 1]
        self.selIndex = None

    def moveDownLine(self):
        if self.selIndex != (len(self.listSchedule) - 1) and self.selIndex != None:
            #temp = self.listSchedule[self.selIndex - 1]
            self.listSchedule[self.selIndex + 1], self.listSchedule[self.selIndex] = \
                                            self.listSchedule[self.selIndex], self.listSchedule[self.selIndex + 1]
            self.selList[self.selIndex + 1], self.selList[self.selIndex] = \
                                            self.selList[self.selIndex], self.selList[self.selIndex + 1]
        self.selIndex = None

    def editLine(self):
        if self.selIndex != None:
            if isinstance(self.selList[self.selIndex]['times'], dict):
                newNum, isOk = AMessageBox.input(self, '修改', '请输入新的掉落物个数')
                if isOk:
                    self.selList[self.selIndex]['times']['bootyNum'] = newNum
            else:
                newNum, isOk = AMessageBox.input(self, '修改', '请输入新的次数')
                self.selList[self.selIndex]['times'] = newNum
            self.refreshJsonView()
        self.selIndex = None

    def clearLine(self):
        self.listSchedule.clear()
        self.selList.clear()

    def loadPlan(self):
        if self.planCb.currentIndex() != 0:
            self.jsonDict = self.jsonAll[self.planCb.currentIndex() + 1][self.allPlanList[self.planCb.currentIndex()]]
            self.selList = self.jsonDict.copy()
            self.refreshJsonView()

    def addPlan(self):
        planName, ok = AMessageBox.input(self, '配置名称', '请输入配置名称：')
        if ok:
            if '|' in planName:
                planName.replace('|', '·')
            self.allPlanList.append(planName)
            tempDict = dict()
            tempDict[planName] = self.selList.copy()
            self.jsonAll.append(tempDict)
            self.updateJson()
            self.planCb.clear()
            self.planCb.addItems(self.allPlanList)

    def delPlan(self):
        if self.planCb.currentIndex() != 0:
            self.allPlanList.pop(self.planCb.currentIndex())
            self.jsonAll.pop(self.planCb.currentIndex() + 1)
            self.updateJson()
            self.planCb.clear()
            self.planCb.addItems(self.allPlanList)
    
    def setBootMode(self, isChecked):
        self.isBootyMode = isChecked
        if self.isBootyMode:
            self.timesLable.setText('个数:')
            self.bootySelBtn.setText('选择掉落物')
            self.bootySelEdit.setText('请输入掉落物')
            self.bootySelEdit.setEnabled(True)
        else:
            self.timesLable.setText('次数:')
            self.bootySelBtn.setText('———')
            self.bootySelEdit.setText('非素材模式')
            self.bootySelEdit.setEnabled(False)
    

class BootyChoice(QWidget):
    def __init__(self, scheduleEdit, ico, theme):
        super().__init__()
        self.scheduleEdit = scheduleEdit
        self.setWindowIcon(QIcon(ico))
        if theme != None:
            self.setStyleSheet(f'''BootyChoice{{background:{theme.getBgColor()}}}
                                QPushButton{{border:0px;background:{theme.getFgColor()};
                                            color:{theme.getFontColor()};
                                            font-family: "Microsoft YaHei", SimHei, SimSun;font:15pt;qproperty-iconSize:60px 60px;}}
                                QPushButton:pressed{{background:{theme.getThemeColor()};font:14pt;color:{theme.getCheckedFontColor()}}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}''')

        self.resPath = getcwd() + '/res/booty/btn/'
        self.RMA70L1 = QPushButton(icon=QIcon(self.resPath + 'RMA70-24.png'), text='RMA70-24')
        self.RMA70L1.clicked.connect(self.setBooty)
        self.RMA70L0 = QPushButton(icon=QIcon(self.resPath + 'RMA70-12.png'), text='RMA70-12')
        self.RMA70L0.clicked.connect(self.setBooty)
        self.alcholL1 = QPushButton(icon=QIcon(self.resPath + '白马醇.png'), text='白马醇')
        self.alcholL1.clicked.connect(self.setBooty)
        self.alcholL0 = QPushButton(icon=QIcon(self.resPath + '扭转醇.png'), text='扭转醇')
        self.alcholL0.clicked.connect(self.setBooty)
        self.MnL1 = QPushButton(icon=QIcon(self.resPath + '三水锰矿.png'), text='三水锰矿')
        self.MnL1.clicked.connect(self.setBooty)
        self.MnL0 = QPushButton(icon=QIcon(self.resPath + '轻锰矿.png'), text='轻锰矿')
        self.MnL0.clicked.connect(self.setBooty)
        self.alloyL1 = QPushButton(icon=QIcon(self.resPath + '炽合金块.png'), text='炽合金块')
        self.alloyL1.clicked.connect(self.setBooty)
        self.alloyL0 = QPushButton(icon=QIcon(self.resPath + '炽合金.png'), text='炽合金')
        self.alloyL0.clicked.connect(self.setBooty)
        self.gelL1 = QPushButton(icon=QIcon(self.resPath + '聚合凝胶.png'), text='聚合凝胶')
        self.gelL1.clicked.connect(self.setBooty)
        self.gelL0 = QPushButton(icon=QIcon(self.resPath + '凝胶.png'), text='凝胶')
        self.gelL0.clicked.connect(self.setBooty)
        self.circuitL2 = QPushButton(icon=QIcon(self.resPath + '晶体电路.png'), text='晶体电路')
        self.circuitL2.clicked.connect(self.setBooty)
        self.circuitL1 = QPushButton(icon=QIcon(self.resPath + '晶体电子单元.png'), text='晶体电子单元')
        self.circuitL1.clicked.connect(self.setBooty)
        self.circuitL0 = QPushButton(icon=QIcon(self.resPath + '晶体元件.png'), text='晶体元件')
        self.circuitL0.clicked.connect(self.setBooty)
        self.pStoneL1 = QPushButton(icon=QIcon(self.resPath + '五水研磨石.png'), text='五水研磨石')
        self.pStoneL1.clicked.connect(self.setBooty)
        self.pStoneL0 = QPushButton(icon=QIcon(self.resPath + '研磨石.png'), text='研磨石')
        self.pStoneL0.clicked.connect(self.setBooty)
        self.deviceL3 = QPushButton(icon=QIcon(self.resPath + '改量装置.png'), text='改量装置')
        self.deviceL3.clicked.connect(self.setBooty)
        self.deviceL2 = QPushButton(icon=QIcon(self.resPath + '全新装置.png'), text='全新装置')
        self.deviceL2.clicked.connect(self.setBooty)
        self.deviceL1 = QPushButton(icon=QIcon(self.resPath + '装置.png'), text='装置')
        self.deviceL1.clicked.connect(self.setBooty)
        self.deviceL0 = QPushButton(icon=QIcon(self.resPath + '破损装置.png'), text='破损装置')
        self.deviceL0.clicked.connect(self.setBooty)
        self.stoneL3 = QPushButton(icon=QIcon(self.resPath + '提纯源岩.png'), text='提纯源岩')
        self.stoneL3.clicked.connect(self.setBooty)
        self.stoneL2 = QPushButton(icon=QIcon(self.resPath + '固源岩组.png'), text='固源岩组')
        self.stoneL2.clicked.connect(self.setBooty)
        self.stoneL1 = QPushButton(icon=QIcon(self.resPath + '固源岩.png'), text='固源岩')
        self.stoneL1.clicked.connect(self.setBooty)
        self.stoneL0 = QPushButton(icon=QIcon(self.resPath + '源岩.png'), text='源岩')
        self.stoneL0.clicked.connect(self.setBooty)
        self.ironL3 = QPushButton(icon=QIcon(self.resPath + '异铁块.png'), text='异铁块')
        self.ironL3.clicked.connect(self.setBooty)
        self.ironL2 = QPushButton(icon=QIcon(self.resPath + '异铁组.png'), text='异铁组')
        self.ironL2.clicked.connect(self.setBooty)
        self.ironL1 = QPushButton(icon=QIcon(self.resPath + '异铁.png'), text='异铁')
        self.ironL1.clicked.connect(self.setBooty)
        self.ironL0 = QPushButton(icon=QIcon(self.resPath + '异铁碎片.png'), text='异铁碎片')
        self.ironL0.clicked.connect(self.setBooty)
        self.ketoneL3 = QPushButton(icon=QIcon(self.resPath + '酮阵列.png'), text='酮阵列')
        self.ketoneL3.clicked.connect(self.setBooty)
        self.ketoneL2 = QPushButton(icon=QIcon(self.resPath + '酮凝集组.png'), text='酮凝集组')
        self.ketoneL2.clicked.connect(self.setBooty)
        self.ketoneL1 = QPushButton(icon=QIcon(self.resPath + '酮凝集.png'), text='酮凝集')
        self.ketoneL1.clicked.connect(self.setBooty)
        self.ketoneL0 = QPushButton(icon=QIcon(self.resPath + '双酮.png'), text='双酮')
        self.ketoneL0.clicked.connect(self.setBooty)
        self.sugarL3 = QPushButton(icon=QIcon(self.resPath + '糖聚块.png'), text='糖聚块')
        self.sugarL3.clicked.connect(self.setBooty)
        self.sugarL2 = QPushButton(icon=QIcon(self.resPath + '糖组.png'), text='糖组')
        self.sugarL2.clicked.connect(self.setBooty)
        self.sugarL1 = QPushButton(icon=QIcon(self.resPath + '糖.png'), text='糖')
        self.sugarL1.clicked.connect(self.setBooty)
        self.sugarL0 = QPushButton(icon=QIcon(self.resPath + '代糖.png'), text='代糖')
        self.sugarL0.clicked.connect(self.setBooty)
        self.esterL3 = QPushButton(icon=QIcon(self.resPath + '聚酸酯块.png'), text='聚酸酯块')
        self.esterL3.clicked.connect(self.setBooty)
        self.esterL2 = QPushButton(icon=QIcon(self.resPath + '聚酸酯组.png'), text='聚酸酯组')
        self.esterL2.clicked.connect(self.setBooty)
        self.esterL1 = QPushButton(icon=QIcon(self.resPath + '聚酸酯.png'), text='聚酸酯')
        self.esterL1.clicked.connect(self.setBooty)
        self.esterL0 = QPushButton(icon=QIcon(self.resPath + '酯原料.png'), text='酯原料')
        self.esterL0.clicked.connect(self.setBooty)

        self.suppoerterL1 = QPushButton(icon=QIcon(self.resPath + '辅助芯片组.png'), text='辅助芯片组')
        self.suppoerterL1.clicked.connect(self.setBooty)
        self.suppoerterL0 = QPushButton(icon=QIcon(self.resPath + '辅助芯片.png'), text='辅助芯片')
        self.suppoerterL0.clicked.connect(self.setBooty)
        self.guardL1 = QPushButton(icon=QIcon(self.resPath + '近卫芯片组.png'), text='近卫芯片组')
        self.guardL1.clicked.connect(self.setBooty)
        self.guardL0 = QPushButton(icon=QIcon(self.resPath + '近卫芯片.png'), text='近卫芯片')
        self.guardL0.clicked.connect(self.setBooty)
        self.sniperL1 = QPushButton(icon=QIcon(self.resPath + '狙击芯片组.png'), text='狙击芯片组')
        self.sniperL1.clicked.connect(self.setBooty)
        self.sniperL0 = QPushButton(icon=QIcon(self.resPath + '狙击芯片.png'), text='狙击芯片')
        self.sniperL0.clicked.connect(self.setBooty)
        self.casterL1 = QPushButton(icon=QIcon(self.resPath + '术师芯片组.png'), text='术师芯片组')
        self.casterL1.clicked.connect(self.setBooty)
        self.casterL0 = QPushButton(icon=QIcon(self.resPath + '术师芯片.png'), text='术师芯片')
        self.casterL0.clicked.connect(self.setBooty)
        self.specialistL1 = QPushButton(icon=QIcon(self.resPath + '特种芯片组.png'), text='特种芯片组')
        self.specialistL1.clicked.connect(self.setBooty)
        self.specialistL0 = QPushButton(icon=QIcon(self.resPath + '特种芯片.png'), text='特种芯片')
        self.specialistL0.clicked.connect(self.setBooty)
        self.vanguardL1 = QPushButton(icon=QIcon(self.resPath + '先锋芯片组.png'), text='先锋芯片组')
        self.vanguardL1.clicked.connect(self.setBooty)
        self.vanguardL0 = QPushButton(icon=QIcon(self.resPath + '先锋芯片.png'), text='先锋芯片')
        self.vanguardL0.clicked.connect(self.setBooty)
        self.medicL1 = QPushButton(icon=QIcon(self.resPath + '医疗芯片组.png'), text='医疗芯片组')
        self.medicL1.clicked.connect(self.setBooty)
        self.medicL0 = QPushButton(icon=QIcon(self.resPath + '医疗芯片.png'), text='医疗芯片')
        self.medicL0.clicked.connect(self.setBooty)
        self.defenderL1 = QPushButton(icon=QIcon(self.resPath + '重装芯片组.png'), text='重装芯片组')
        self.defenderL1.clicked.connect(self.setBooty)
        self.defenderL0 = QPushButton(icon=QIcon(self.resPath + '重装芯片.png'), text='重装芯片')
        self.defenderL0.clicked.connect(self.setBooty)

        self.grid = QGridLayout()

        self.grid.addWidget(self.RMA70L1,0,0)
        self.grid.addWidget(self.RMA70L0,0,1)
        self.grid.addWidget(self.alcholL1,0,2)
        self.grid.addWidget(self.alcholL0,0,3)
        self.grid.addWidget(self.MnL1,0,4)
        self.grid.addWidget(self.MnL0,0,5)
        self.grid.addWidget(self.alloyL1,1,0)
        self.grid.addWidget(self.alloyL0,1,1)
        self.grid.addWidget(self.gelL1,1,2)
        self.grid.addWidget(self.gelL0,1,3)
        self.grid.addWidget(self.circuitL2,1,4)
        self.grid.addWidget(self.circuitL1,1,5)
        self.grid.addWidget(self.circuitL0,1,6)
        self.grid.addWidget(self.pStoneL1,0,6)
        self.grid.addWidget(self.pStoneL0,0,7)
        self.grid.addWidget(self.deviceL3,2,0)
        self.grid.addWidget(self.deviceL2,2,1)
        self.grid.addWidget(self.deviceL1,2,2)
        self.grid.addWidget(self.deviceL0,2,3)
        self.grid.addWidget(self.stoneL3,2,4)
        self.grid.addWidget(self.stoneL2,2,5)
        self.grid.addWidget(self.stoneL1,2,6)
        self.grid.addWidget(self.stoneL0,2,7)
        self.grid.addWidget(self.ironL3,3,0)
        self.grid.addWidget(self.ironL2,3,1)
        self.grid.addWidget(self.ironL1,3,2)
        self.grid.addWidget(self.ironL0,3,3)
        self.grid.addWidget(self.ketoneL3,3,4)
        self.grid.addWidget(self.ketoneL2,3,5)
        self.grid.addWidget(self.ketoneL1,3,6)
        self.grid.addWidget(self.ketoneL0,3,7)
        self.grid.addWidget(self.sugarL3,4,0)
        self.grid.addWidget(self.sugarL2,4,1)
        self.grid.addWidget(self.sugarL1,4,2)
        self.grid.addWidget(self.sugarL0,4,3)
        self.grid.addWidget(self.esterL3,4,4)
        self.grid.addWidget(self.esterL2,4,5)
        self.grid.addWidget(self.esterL1,4,6)
        self.grid.addWidget(self.esterL0,4,7)

        self.grid.addWidget(self.suppoerterL1,5,0)
        self.grid.addWidget(self.guardL1,5,1)
        self.grid.addWidget(self.sniperL1,5,2)
        self.grid.addWidget(self.casterL1,5,3)
        self.grid.addWidget(self.specialistL1,5,4)
        self.grid.addWidget(self.vanguardL1,5,5)
        self.grid.addWidget(self.medicL1,5,6)
        self.grid.addWidget(self.defenderL1,5,7)
        self.grid.addWidget(self.suppoerterL0,6,0)
        self.grid.addWidget(self.guardL0,6,1)
        self.grid.addWidget(self.sniperL0,6,2)
        self.grid.addWidget(self.casterL0,6,3)
        self.grid.addWidget(self.specialistL0,6,4)
        self.grid.addWidget(self.vanguardL0,6,5)
        self.grid.addWidget(self.medicL0,6,6)
        self.grid.addWidget(self.defenderL0,6,7)

        self.setLayout(self.grid)
        self.resize(1400, 517)

        self.setWindowTitle('指定素材')

    def setBooty(self):
        bootyName = self.sender().text()
        self.scheduleEdit.bootyName = bootyName
        self.scheduleEdit.bootySelBtn.setText(f'当前:{bootyName}')
        #print(self.scheduleEdit.bootyName)
        self.close()

    def myShow(self):
        if self.scheduleEdit.isBootyMode and not self.isVisible():
            self.center()
            self.show()

    def center(self):
        #显示到屏幕中心
        pass
        #cp = QDesktopWidget().availableGeometry().center()
        #self.move(int(cp.x() - self.width()/2), int(cp.y() - self.height()/2))

