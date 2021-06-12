from os import getcwd

class RuleEncoder:
    def __init__(self, rulePath):
        self.rules = self.loadRules(rulePath)

    def loadRules(self, rulePath):
        rules = dict()
        thisRule = dict()
        ruleOneRoom = []
        roomName = None
        ruleName = None
        with open(rulePath, 'r', encoding = 'utf-8') as f:
            while True:
                text = f.readline()
                if text == '':
                    break
                else:
                    text = text.strip()
                if text != '' and text[0] != '#':
                    if 'START' in text and text[0:5] == 'START':
                        #规则开始
                        temp = text.split(' ')
                        if len(temp) != 1:
                            ruleName = temp[1]
                        else:
                            ruleName = '未命名'
                        pass
                    elif 'END' in text and text[0:3] == 'END':
                        '规则结束'
                        thisRule[roomName] = ruleOneRoom.copy()
                        rules[ruleName] = thisRule.copy()
                        thisRule.clear()
                        ruleOneRoom.clear()
                    else:
                        #读取规则
                        if '[' in text and ']' in text:
                            text = text.strip('[').strip(']')
                            if roomName != None and text != roomName:
                                thisRule[roomName] = ruleOneRoom.copy()
                                ruleOneRoom.clear()
                                roomName = text
                            else:
                                roomName = text
                        else:
                            text = text.split('~')
                            if len(text) == 1:
                                #非组合
                                ruleOneRoom.append(text[0])
                            else:
                                for i in range(0, len(text) - 1):
                                    ruleOneRoom.append('+' + text[i])
                                ruleOneRoom.append(text[-1])
        return rules

    def getAllRulesName(self):
        return list(self.rules.keys())

    def getOneRule(self, ruleName):
        return self.rules.get(ruleName, 'CANNOT FIND THIS RULE')

if __name__ == '__main__':
    test = RuleEncoder(getcwd() + '/logisticRule')
    print(test.getOneRule('测试配置'))