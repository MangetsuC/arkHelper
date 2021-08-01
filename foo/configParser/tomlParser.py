from os import getcwd, getlogin, path
from sys import path as syspath

from toml import dumps

syspath.append(getcwd())

from foo.configParser import tomlBase


class Toml:
    def __init__(self, filename, default_toml):
        self.releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/' + filename
        self.devPath = './' + filename
        self.toml = tomlBase.tomlRead(filename)
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

    def get(self, key):
        '获取值'
        keys = key.split('.')
        temp = self.toml
        for i in keys:
            temp = temp[i]
        return temp

    def change(self, key, value):
        '修改或增加条目'
        keys = key.split('.')
        temp = self.toml
        for i in keys[:-1]:
            if not i in temp.keys():
                temp[i] = dict()
            temp = temp[i]
        temp[keys[-1]] = value
        self.write()

    def delete(self, key):
        '删除某一条目'
        keys = key.split('.')
        temp = self.toml
        for i in keys[:-1]:
            if not i in temp.keys():
                break #找不到对应键直接返回
            temp = temp[i]
        else:
            temp.pop(keys[-1])
        self.write()



class configToml(Toml):
    def __init__(self):
        super(configToml, self).__init__('config.toml', tomlBase.defaultConfig())

class simulatorToml(Toml):
    def __init__(self):
        super(simulatorToml, self).__init__('simulator.toml', tomlBase.defaultSimulator())

    def get_simulators(self):
        return self.toml.keys()

if __name__ == '__main__':
    test1 = configToml()
    test2 = simulatorToml()

