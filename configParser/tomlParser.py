from os import getcwd, getlogin, path
from sys import path as syspath

from toml import dumps

syspath.append(getcwd())

from configParser import tomlBase


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
            if keys[-1] in temp.keys():
                temp.pop(keys[-1])
        self.write()



class ConfigToml(Toml):
    def __init__(self):
        super().__init__('config.toml', tomlBase.defaultConfig(), tomlBase.ini2toml_config())

class SimulatorToml(Toml):
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

class ScheduleToml(Toml):
    def __init__(self):
        super().__init__('schedule.toml', tomlBase.defaultSchedule(), tomlBase.json2toml())

class Res_config(Toml):
    def __init__(self):
        super().__init__('res_config.toml', None, None)

    def get_res_config(self, key, part):
        try:
            ans = self.get('{}.{}'.format(key, part))
        except:
            ans = dict()

        return ans

    def get_res_list(self):
        return list(set(self.get('ress')))

    def get_res_readme(self, key):
        return self.get(f'{key}.readme')

class Recruit_data(Toml):
    def __init__(self):
        super().__init__('recruit_data.toml', None, None)

    def get_tags_ops(self, tags_on_screen:list) -> dict:
        tags_combs = \
        [[0], [1], [2], [3], [4], 
        [0, 1], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4], 
        [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 3], [0, 2, 4], [0, 3, 4], [1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4],
        [0, 1, 2, 3], [0, 1, 2, 4], [0, 1, 3, 4], [0, 2, 3, 4], [1, 2, 3, 4],
        [0, 1, 2, 3, 4]]
        ans_star = []
        ans_detailed = []
        for i in tags_combs:
            is_may_get_6 = False
            for j in i:
                if tags_on_screen[j] == '高级资深干员':
                    is_may_get_6 = True
                    break

            temp = [[], []]
            for op in self.toml.keys():
                if self.toml[op]['star'] == 6 and not is_may_get_6:
                    continue

                for j in i:
                    if not tags_on_screen[j] in self.toml[op]['tags']:
                        break
                else:
                    temp[0].append(self.toml[op]['star'])
                    temp[1].append([op, self.toml[op]['star']])
            ans_star.append(temp[0])
            ans_detailed.append(temp[1])
        
        min_4 = [[],[]]
        min_5 = [[],[]]
        min_6 = [[],[]]
        max_2 = [[],[]]
        max_1 = [[],[]]
        other = [[],[]]
        
        for i in range(len(tags_combs)):
            if ans_star[i] == []:
                continue
            ans_star[i].sort()
            if ans_star[i][-1] != 1 and ans_star[i][-1] != 2: #9小时滤除一星二星
                for k in range(len(ans_star)):
                    if ans_star[i][k] > 2:
                        break
                ans_star[i] = ans_star[i][k:]

            if ans_star[i][0] == 4:
                min_4[0].append(tags_combs[i])
                min_4[1].append(ans_detailed[i])
            elif ans_star[i][0] == 5:
                min_5[0].append(tags_combs[i])
                min_5[1].append(ans_detailed[i])
            elif ans_star[i][0] == 6:
                min_6[0].append(tags_combs[i])
                min_6[1].append(ans_detailed[i])
            elif ans_star[i][-1] == 2:
                max_2[0].append(tags_combs[i])
                max_2[1].append(ans_detailed[i])
            elif ans_star[i][-1] == 1:
                max_1[0].append(tags_combs[i])
                max_1[1].append(ans_detailed[i])
            else:
                other[0].append(tags_combs[i])
                other[1].append(ans_detailed[i])

        return dict(min_4 = min_4,
                    min_5 = min_5,
                    min_6 = min_6,
                    max_2 = max_2,
                    max_1 = max_1,
                    other = other)




if __name__ == '__main__':
    test1 = Recruit_data()
    tags_on_screen = ['医疗干员', '术师干员','特种干员','支援','快速复活']
    print(test1.get_tags_ops(tags_on_screen))

