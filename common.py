from os import getcwd, getlogin, path, mkdir
from foo.configParser.tomlParser import configToml, simulatorToml, scheduleToml
from foo.ui.theme import Theme

config_path = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper' #如果非开发模式则创建配置文件目录
if not (path.exists('./config.ini') or path.exists('./config.toml')):
    if not path.exists(config_path):
        try:
            mkdir(config_path)
        except Exception as creatDirErr:
            print(creatDirErr)
            config_path = getcwd()
else:
    config_path = getcwd()

user_data = configToml()
simulator_data = simulatorToml()
schedule_data = scheduleToml()

theme = Theme(user_data, True)

