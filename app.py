from configparser import ConfigParser
from os import getcwd
from threading import Thread
from time import sleep
from tkinter import *

from foo.adb import adbCtrl
from foo.arknight import Battle, task
from foo.win import toast


class APP():
    def __init__(self, TKapp):
        self.mainGate = False
        self.__app = TKapp
        self.__cwd = getcwd().replace('\\', '/')
        self.__config = ConfigParser()
        self.__config.read(filenames=self.__cwd + "/config.ini", encoding="UTF-8")
        self.__ip = self.__config.get("connect", "ip")
        self.__port = self.__config.get("connect", "port")
        self.__adb = adbCtrl.adb(self.__cwd + "/bin/adb", self.__ip, self.__port)
        self.icon = self.__cwd + "/res/ico.ico"
        
        self.__battle = Battle.BattleLoop(self.__adb, self.__cwd, self)
        self.__task = task.Task(self.__adb,self.__cwd)
        self.__threadStart = None
        
        #根窗口属性
        self.__app.resizable(width=False, height=False)
        self.__app.title('明日方舟虚拟博士')
        self.__app.iconbitmap(bitmap = self.icon)
        self.__app.protocol(name = "WM_DELETE_WINDOW", func = self.beforeClosed) #挂接窗口关闭事件

        #启动按钮属性
        self.__buttonRunAndStopVar = StringVar()
        self.__buttonRunAndStopVar.set('启动虚拟博士')

        #创建复选框属性
        self.__cbBattleVar = IntVar()
        self.__cbBattleVar.set(1)
        #self.__cbConstructionVar = IntVar()
        #self.__cbConstructionVar.set(1)
        #self.__cbSendCluenVar = IntVar()
        self.__cbTaskVar = IntVar()
        self.__cbTaskVar.set(1)

        #创建状态标签属性
        self.__lableStateVar = StringVar()

        self.createWindowsControl()
        self.setWindowsControl()

    def beforeClosed(self):
        '窗口关闭事件'
        self.stop()
        #if (self.__threadStart != None) and (self.__threadStart.is_alive()):
        #    self.__threadStart.join()
        self.__app.quit()

    def createWindowsControl(self):
        '创建窗口控件'
        self.__buttonRunAndStop = Button(self.__app, 
                                        textvariable = self.__buttonRunAndStopVar, 
                                        width = 36, 
                                        command = self.buttonRunAndStopClick)
        self.__groupConfig = LabelFrame(self.__app, text = '配置', padx = 2, pady = 2)
        self.__lableState = Label(self.__app, textvariable = self.__lableStateVar)

        self.__cbBattle = Checkbutton(self.__groupConfig, text = '战斗', variable = self.__cbBattleVar, padx = 3, pady = 3)
        #self.__cbConstruction = Checkbutton(self.__groupConfig, text = '基建', variable = self.__cbConstructionVar, padx = 3, pady = 3)
        #self.__cbSendClue = Checkbutton(self.__groupConfig, text = '赠送线索', variable = self.__cbSendCluenVar, padx = 3, pady = 3)
        self.__cbTask = Checkbutton(self.__groupConfig, text = '任务交付', variable = self.__cbTaskVar, padx = 3, pady = 3)
        pass
    
    def setWindowsControl(self):
        '置控件属性'
        self.__buttonRunAndStop.grid(row = 0, column = 0, padx = 8, pady = 8)

        #选择模式的复选框，目前只有单一模式故不显示
        self.__groupConfig.grid(row = 1, padx = 5)
        self.__cbBattle.grid(row = 0, column = 0)
        #self.__cbConstruction.grid(row = 0, column = 1)
        #self.__cbSendClue.grid(row = 0, column = 2, columnspan = 2)
        self.__cbTask.grid(row = 0, column = 6, columnspan = 2)

        self.__lableState.grid(row = 2, padx = 0, pady = 0, sticky = W)
        self.setState('未启动')
        pass

    def buttonRunAndStopClick(self):
        if self.__buttonRunAndStopVar.get() == '启动虚拟博士':
            self.setState('正在尝试连接')
            self.__buttonRunAndStopVar.set('停止虚拟博士')
            self.__threadStart = Thread(target= self.start)
            self.__threadStart.setDaemon(True)
            self.__threadStart.start()
            
        elif self.__buttonRunAndStopVar.get() == '停止虚拟博士':
            self.stop()
            self.setState('正在停止')
            #self.__threadStart.join()
            sleep(1)
            self.setState('已停止')
            self.__buttonRunAndStopVar.set('启动虚拟博士')

        else:
            pass

    def setState(self, state):
        self.__lableStateVar.set('状态：' + state)

    def setButton(self, state):
        '修改按钮状态，state为1则是未运行状态'
        if state:
            self.__buttonRunAndStopVar.set('启动虚拟博士')
        else:
            self.__buttonRunAndStopVar.set('停止虚拟博士')

    def stop(self):
        self.mainGate = False
        self.__battle.stop()
        self.__task.stop()

    def start(self):
        self.mainGate = self.__battle.connect()
        if self.__cbBattleVar.get() and self.mainGate:
            self.__battle.run(self.mainGate)
        if self.__cbTaskVar.get() and self.mainGate:
            self.setState('开始交付任务')
            self.__task.run(self.mainGate)

        self.setState('已结束')
        self.setButton(1)


app = APP(Tk())
print('''+--------------------------+
|          调试窗口        |
+--------------------------+

信息：普通用户请直接最小化''')
mainloop()

