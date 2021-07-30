from os import getcwd, getlogin, path
from sys import path as syspath

from toml import dumps

syspath.append(getcwd())

from foo.configParser import tomlBase


class Toml:
    releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/config.toml'
    devPath = './config.toml'
    def __init__(self):
        self.toml = tomlBase.tomlRead()
        default_toml = tomlBase.defaultConfig()
        if self.toml == dict():
            ini = tomlBase.ini2toml()
            self.toml = tomlBase.dictUpdate(default_toml, ini)
        else:
            self.toml = tomlBase.dictUpdate(default_toml, self.toml)
        self.write()

    def write(self):
        '更新配置文件'
        if path.exists(self.devPath):
            with open(self.devPath, 'w', encoding='UTF-8') as f:
                f.write(dumps(self.toml))
        else:
            with open(self.releasePath, 'w', encoding='UTF-8') as f:
                f.write(dumps(self.toml))

if __name__ == '__main__':
    test = Toml()

