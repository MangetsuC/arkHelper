from configparser import ConfigParser
from os import getlogin, path

def iniRead():
    releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/config.ini'
    devPath = './config.ini'
    config = ConfigParser()
    if path.exists(devPath):
        try:
            config.read(filenames=devPath, encoding="UTF-8")
        except UnicodeDecodeError:
            config.read(filenames=devPath, encoding="gbk")
    elif path.exists(releasePath):
        try:
            config.read(filenames=releasePath, encoding="UTF-8")
        except UnicodeDecodeError:
            config.read(filenames=releasePath, encoding="gbk")
    return config

def ini2dict():
    ini = iniRead()
    config_old = dict()
    for section in ini.sections():
        config_old[section] = dict()
        for option in ini.options(section):
            value = ini.get(section, option)
            if value.isnumeric():
                value = int(value)
            elif value == 'True' or value == 'False':
                value = bool(value)
            config_old[section][option] = value

    return config_old