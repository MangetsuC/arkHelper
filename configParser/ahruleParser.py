from os import path, getlogin

class Ahrule_Parser:
    def __init__(self, filename) -> None:
        if path.exists(f'./{filename}.ahrule'):
            self.path = f'./{filename}.ahrule'
        elif path.exists(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/{filename}.ahrule'):
            self.path = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/{filename}.ahrule'
        else:
            #无对应文件
            pass

        self.data = dict()
        self.load_ahrule()

        self.choice_name = list(self.data.keys())[0]

    def change_choice(self, new_choice_name:str) -> None:
        if new_choice_name in self.data.keys():
            self.change_choice = new_choice_name

    def load_ahrule(self) -> None:
        self.data.clear()
        with open(self.path, 'r', encoding='UTF-8') as f:
            lines = f.readlines()

        rule_name = None
        section_name = None
        for line in lines:
            line = line.strip('\n')
            if not line.strip(' '): continue 

            if line[0] == '#':
                #注释行
                continue

            if len(line) > 4 and line[0:5] == 'START':
                #配置开始行
                temp = line.split(' ')
                if len(temp) > 1:
                    rule_name = temp[1].strip(' ')
                else:
                    for i in range(1, 100):
                        rule_name = f'未命名{i}'
                        if not rule_name in self.data.keys():
                            break
                self.data[rule_name] = dict()
                continue
            elif len(line) > 2 and line[0:3] == 'END':
                #配置结束行
                rule_name = None
                section_name = None
                continue

            if rule_name != None:
                #在开始行和结束行之间
                if line.strip(' ')[0] == '[' and line.strip(' ')[-1] == ']':
                    section_name = line.strip(' ').strip('[').strip(']')
                    self.data[rule_name][section_name] = list()
                    continue

                if section_name != None:
                    line = line.split('~')
                    limit = []
                    for i in range(len(line)):
                        for j in ['|', '*', '$']:
                            if j in line[i]:
                                limit.append(j)
                        line[i] = line[i].strip(' ').strip('|').strip('*').strip('$')

                    limit = list(set(limit))
                    self.data[rule_name][section_name].append(dict(limit = limit, 
                                                                    names = line))
                    
    def get_rule(self) -> dict:
        return self.data[self.choice_name]
                
class Logistic_Rule(Ahrule_Parser):
    def __init__(self) -> None:
        super().__init__('logisticRule')


if __name__ == '__main__':
    logistic_rule = Logistic_Rule()
    print(logistic_rule.get_rule())






























