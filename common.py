from os import getcwd, getlogin, path, mkdir
from configParser.tomlParser import ConfigToml, Recruit_data, SimulatorToml, ScheduleToml, Res_config
from foo.ui.theme import Theme
import sys
from time import strftime, localtime
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from os import remove

def beforeLaunch():
    sys.stdout = EmittingStr()
    sys.stderr = EmittingStr()

def logWrite(text):
    try:
        with open('./arkhelper.log', 'a', encoding='UTF-8') as log:
            log.write(text)
    except:
        remove('./arkhelper.log')
        with open('./arkhelper.log', 'a', encoding='UTF-8') as log:
            log.write(text)

class EmittingStr(QObject):
    sgnConsole = Signal(str)

    def write(self, text):
        if text != '\n':
            timeNow = strftime("%Y-%m-%d %H:%M:%S" ,localtime())
            text = '[{logTime}]{logText}'.format(logTime = timeNow, logText = str(text))
        self.sgnConsole.emit(text)

#beforeLaunch()
config_path = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper' #如果非开发模式则创建配置文件目录
if not (path.exists('./config.ini') or path.exists('./config.toml')):
    #正常用户模式
    if not path.exists(config_path):
        try:
            mkdir(config_path)
        except Exception as creatDirErr:
            print(creatDirErr)
            config_path = getcwd()
else:
    #开发者模式
    config_path = getcwd()

user_data = ConfigToml()
simulator_data = SimulatorToml()
schedule_data = ScheduleToml()
recruit_data = Recruit_data()

res_config = Res_config()

theme = Theme(user_data, True)

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QApplication(sys.argv)


app_ico = QIcon('./gres/ico.ico')

