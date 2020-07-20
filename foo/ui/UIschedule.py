import sys
from os import getcwd
from PyQt5.QtWidgets import QWidget,QApplication,QGridLayout,QListView,QPushButton,QMenu,QComboBox,QLineEdit,QLabel,QListView
from PyQt5.QtCore import Qt,QStringListModel,QTimer
from PyQt5.QtGui import QIcon
from json import loads,dumps


class JsonEdit(QWidget):
    def __init__(self, ico, parent = None, flags = Qt.WindowCloseButtonHint):
        super().__init__(parent, flags)

        self.setStyleSheet('''JsonEdit{background:#272626}QLabel{color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;}
                                QPushButton{border:0px;background:#4d4d4d;color:#ffffff;font-family: "Microsoft YaHei", SimHei, SimSun;font:11pt;}
                                QPushButton:pressed{background:#606162;font:10pt;}
                                QPushButton:hover{border-style:solid;border-width:1px;border-color:#ffffff;}
                                QLineEdit{background-color:#4d4d4d;color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;border:0px;padding-left:5px}
                                QLineEdit:hover{border-style:solid;border-width:1px;border-color:#ffffff;padding-left:4px;}
                                QListView{background-color:#4d4d4d;color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}
                                QComboBox:hover{border-style:solid;border-width:1px;border-color:#ffffff;padding-left:4px;}
                                QComboBox{background-color:#4d4d4d;color:#ffffff;font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;padding-left:5px;border:0px;}
                                QComboBox:drop-down{width:0px;}
                                QComboBox:down-arrow{width:0px}
                                QComboBox:selected{background-color:#606162;}
                                QComboBox:QAbstractItemView::item{font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;}
                                QComboBox:QAbstractItemView::item:selected{background-color:#606162;}''')

        self.setWindowIcon(QIcon(ico))
        self.isshow = False
        self.json = getcwd() + '/schedule.json'
        self.scheduleAdd = {'part':'MAIN', 'chap':'', 'objLevel':'', 'times':''}
        self.transEX = {'ex1':'切尔诺伯格','ex2':'龙门外环','ex3':'龙门市区'}

        self.partList = ['主线','物资筹备','芯片搜索','剿灭作战']
        self.partListJson = ['MAIN','RS','PR','EX']
        self.mainChapList = ['序章','第一章','第二章','第三章','第四章','第五章','第六章','第七章']
        self.rsChapList = ['战术演习','粉碎防御','空中威胁','货物运送','资源保障']
        self.prChapList = ['医疗重装','术士狙击','辅助先锋','特种近卫']
        self.exChapList = ['切尔诺伯格','龙门外环','龙门市区']
        self.chapList = [self.mainChapList,self.rsChapList,self.prChapList,self.exChapList]

        self.selIndex = None
        
        self.grid = QGridLayout()
        self.lsv = QListView()
        self.lsv.setFixedWidth(200)
        self.lsv.clicked.connect(self.clickSchedule)
        self.slm = QStringListModel()

        self.partCb = QComboBox()
        self.partCb.addItems(self.partList)
        self.partCb.activated[int].connect(self.changeChapList)
        self.partCb.setFixedSize(80, 40)
        self.partCb.setView(QListView())

        self.chapCb = QComboBox()
        self.chapCb.addItems(self.mainChapList)
        self.chapCb.activated[int].connect(self.changeLevel1List)
        self.chapCb.setFixedSize(100, 40)
        self.chapCb.setView(QListView())

        self.level1Cb = QComboBox()
        self.level1Cb.setFixedSize(60, 40)
        self.level1Cb.setView(QListView())

        self.lineLable = QLabel()
        self.lineLable.setText('-')

        self.level2Edit = QLineEdit()
        self.level2Edit.setFixedSize(50, 40)

        self.timesLable = QLabel()
        self.timesLable.setText('次数:')

        self.timeEdit = QLineEdit()
        self.timeEdit.setFixedSize(50, 40)

        self.delBtn = QPushButton()
        self.delBtn.setText('删除')
        self.delBtn.clicked.connect(self.delLine)
        self.delBtn.setFixedHeight(40)
        self.clearBtn = QPushButton()
        self.clearBtn.setText('清空')
        self.clearBtn.clicked.connect(self.clearLine)
        self.clearBtn.setFixedHeight(40)

        self.addBtn = QPushButton()
        self.addBtn.setText('添加')
        self.addBtn.clicked.connect(self.addLine)
        self.addBtn.setFixedHeight(40)

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
        self.grid.addWidget(self.level1Cb,0,3,1,1)
        self.grid.addWidget(self.lineLable,0,4,1,1)
        self.grid.addWidget(self.level2Edit,0,5,1,1)
        self.grid.addWidget(self.timesLable,0,6,1,1)
        self.grid.addWidget(self.timeEdit,0,7,1,1)
        self.grid.addWidget(self.addBtn,1,1,1,7)
        self.grid.addWidget(self.delBtn,2,1,1,4)
        self.grid.addWidget(self.clearBtn,2,5,1,3)

        self.setLayout(self.grid)

        self.setWindowTitle('路线规划')
        #self.resize(600,400)

        self.myTimer()
        #self.show()

    def editerShow(self):
        self.isshow = not self.isshow
        if self.isshow:
            self.show()
        else:
            self.close()

    def closeEvent(self,event):
        self.isshow = False
        event.accept()

    def myTimer(self):
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateList)
        self.updateTimer.start(10)
    
    def initJson(self):
        with open(self.json,'r') as s:
            data = s.read()
        data = loads(data)
        self.jsonDict = data['levels']
        for eachDict in self.jsonDict:
            temp = eachDict['objLevel']
            if 'ex' in temp:
                temp = self.transEX[temp]
            if eachDict['chap'] == 'LS':
                temp = temp.replace('S', 'LS')
            self.listSchedule.append('{0}（共{1}次）'.format(temp,eachDict['times']))

    def refreshJsonView(self):
        temp = self.jsonDict[-1]['objLevel']
        if 'ex' in temp:
            temp = self.transEX[temp]
        if self.jsonDict[-1]['chap'] == 'LS':
            temp = temp.replace('S', 'LS')
        self.listSchedule.append('{0}（共{1}次）'.format(temp,self.jsonDict[-1]['times']))

    def updateJson(self):
        tempNewJson = {'levels':self.jsonDict}
        newData = dumps(tempNewJson)
        newData = newData.replace(',',',\n')
        newData = newData.replace('[','[\n')
        newData = newData.replace('{','{\n')
        newData = newData.replace(']','\n]')
        newData = newData.replace(' {','{')
        newData = newData.replace('\"part\"','\t\"part\"')
        newData = newData.replace(' \"chap\"','\t\"chap\"')
        newData = newData.replace(' \"objLevel\"','\t\"objLevel\"')
        newData = newData.replace(' \"times\"','\t\"times\"')
        with open(self.json,'w') as j:
            j.write(newData)

    def updateList(self):
        if self.listSchedule != self.listScheduleBefore:
            self.listScheduleBefore = self.listSchedule.copy()
            self.slm.setStringList(self.listSchedule)
            self.updateJson()
    
    def changeChapList(self,indexI):
        self.scheduleAdd['part'] = self.partListJson[indexI]
        self.chapCb.clear()
        self.chapCb.addItems(self.chapList[indexI])
        self.changeLevel1List(0)
    
    def changeLevel1List(self,indexI):
        self.level1Cb.clear()
        selChap = self.chapCb.currentText()
        self.level2Edit.setReadOnly(False)
        levelList = []
        if '章' in selChap:
            self.scheduleAdd['chap'] = str(int(indexI))
            levelList.append(f'{int(indexI)}')
            if int(indexI) != 0 and int(indexI) != 1:
                levelList.append(f'S{int(indexI)}')

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
                self.scheduleAdd['chap'] = 'ex1'
            elif selChap == '龙门外环':
                self.scheduleAdd['chap'] = 'ex2'
            elif selChap == '龙门市区':
                self.scheduleAdd['chap'] = 'ex3'

            self.level2Edit.clear()
            self.level2Edit.setReadOnly(True)

        self.level1Cb.addItems(levelList)
    
    def addLine(self):
        tempLevel = self.level2Edit.text()
        self.scheduleAdd['objLevel'] = tempLevel
        tempTimes = self.timeEdit.text()
        self.scheduleAdd['times'] = tempTimes
        if 'ex' in self.scheduleAdd['chap']:
            self.scheduleAdd['objLevel'] = self.scheduleAdd['chap']
        elif tempLevel != '':
            part1 = self.level1Cb.currentText()
            if part1 == 'LS':
                part1 = 'S'
            self.scheduleAdd['objLevel'] = part1 + '-' + tempLevel
        if tempTimes.isdecimal():
                self.scheduleAdd['times'] = tempTimes
        if self.scheduleAdd['objLevel'] != '' and self.scheduleAdd['times'] != '':
            self.jsonDict.append(self.scheduleAdd.copy())
            self.refreshJsonView()
    
    def clickSchedule(self,qModelIndex):
        self.selIndex = qModelIndex.row()

    def delLine(self):
        if self.selIndex != None:
            self.listSchedule.pop(self.selIndex)
            self.jsonDict.pop(self.selIndex)
        self.selIndex = None

    def clearLine(self):
        self.listSchedule.clear()
        self.jsonDict.clear()

    
    def test(self):
        self.listSchedule.append('add')
        print(self.listSchedule)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    ex = JsonEdit(getcwd()+'/res/ico.ico')
    ex.editerShow()
    sys.exit(app.exec_())