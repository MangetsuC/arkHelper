from os import getcwd, getlogin, path
from sys import path as syspath

from toml import dumps

syspath.append(getcwd())

from foo.configParser import tomlBase


class Toml:
    def __init__(self, filename, default_toml, old = None):
        self.releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/' + filename
        self.devPath = './' + filename
        self.toml = tomlBase.tomlRead(filename)
        if self.toml == dict() and old != None: #将旧类型配置合并到新配置中
            self.toml = tomlBase.dictUpdate(default_toml, old)
        elif default_toml != None:
            self.toml = tomlBase.dictUpdate(default_toml, self.toml) #将用户先前的配置合并到新配置文件中
        self.write()

    def write(self):
        '更新配置文件'
        if path.exists(self.devPath):
            with open(self.devPath, 'w', encoding='UTF-8') as f:
                f.write(dumps(self.toml))
        else:
            try:
                with open(self.releasePath, 'w', encoding='UTF-8') as f:
                    f.write(dumps(self.toml))
            except:
                with open(self.devPath, 'w', encoding='UTF-8') as f:
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
        super(configToml, self).__init__('config.toml', tomlBase.defaultConfig(), tomlBase.ini2toml_config())

class simulatorToml(Toml):
    def __init__(self):
        self.releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/simulator.toml'
        self.devPath = './simulator.toml'
        self.toml = tomlBase.tomlRead('simulator.toml')
        if self.toml == dict(): #将旧类型配置合并到新配置中
            self.toml = tomlBase.dictUpdate(tomlBase.defaultSimulator(), self.toml)
        self.write()
        #可以初始化，但不会每次都补充用户删除的配置

    def get_simulators(self):
        return self.toml.keys()

class scheduleToml(Toml):
    def __init__(self):
        super(scheduleToml, self).__init__('schedule.toml', tomlBase.defaultSchedule(), tomlBase.json2toml())

if __name__ == '__main__':
    test1 = configToml()
    test2 = simulatorToml()

