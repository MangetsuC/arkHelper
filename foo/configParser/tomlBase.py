from os import getlogin, path, getcwd
from sys import path as syspath

from toml import dumps, loads

syspath.append(getcwd())

from foo.configParser import iniParser


def defaultConfig():
    '返回默认配置文件'
    default = '''
    simulator = 'bluestacks' #当前选择的模拟器，模拟器数据存在另一文件中
    notice = '' #上一次公告对应的md5

    [theme] #主题颜色
    themecolor = 'auto'
    fontcolor = 'auto'
    checkedfontcolor = 'auto'
    bordercolor = 'auto'
    fgcolor = 'auto'
    bgcolor = 'auto'
    pressedcolor = 'auto'
    selectedcolor = 'auto'

    [logistic] #基建配置
    rule = '示例配置' #当前选择的配置名称
    manufactory.enable = true #是否处理制造站
    trade.enable = true #是否处理贸易站
    powerroom.enable = true #是否处理发电站
    officeroom.enable = true #是否处理办公室

    meetingroom.enable = true #是否处理会客室
    meetingroom.send = true #会客室是否自动赠送线索
    meetingroom.use = true #会客室是否自动开启线索交流
    meetingroom.daily = true #会客室是否自动领取每日线索（会客室右侧3选项中的第一个）

    [logistic.threshold]
    work = 0
    dorm = 24

    [function]
    battle.default = true
    schedule.default = false

    autopc.default = false
    autopc.skip1star = true
    autopc.skip5star = true
    autopc.skip23star = false
    
    task.default = true
    credit.default = false
    shutdown.default = false

    [recover]
    loop.medicine.enable = false
    loop.stone.enable = false
    loop.stone.max = 0

    schedule.medicine.enable = false
    schedule.stone.enable = false
    schedule.stone.max = 0
    '''
    return loads(default)

def ini2toml():
    '将现有的ini转为toml'
    config_old = iniParser.ini2dict()
    config_new = dict()
    if config_old != dict():
        config_new['simulator'] = config_old['connect']['simulator']
        config_new['notice'] = config_old['notice']['md5']
        config_new['theme'] = config_old['theme']
        config_new['logistic'] = config_old['logistic']
        config_new['logistic'] = dict()
        config_new['logistic']['rule'] = config_old['logistic']['defaultrule']
        config_new['logistic']['manufactory'] = {'default': config_old['logistic']['manufactory']}
        config_new['logistic']['trade'] = {'default': config_old['logistic']['trade']}
        config_new['logistic']['powerroom'] = {'default': config_old['logistic']['powerroom']}
        config_new['logistic']['officeroom'] = {'default': config_old['logistic']['officeroom']}
        config_new['logistic']['meetingroom'] = {'default': config_old['logistic']['receptionroom']}
        config_new['logistic']['threshold'] = {'work': config_old['logistic']['moodthreshold'],
                                            'dorm': config_old['logistic']['dormthreshold']}
        config_new['function'] = dict()
        config_new['function']['battle'] = {'default': config_old['function']['battle']}
        config_new['function']['schedule'] = {'default': config_old['function']['schedule']}
        config_new['function']['autopc'] = {'default': config_old['function']['autopc'],
                                            'skip1star': config_old['function']['autopc_skip1star'],
                                            'skip5star': config_old['function']['autopc_skip5star'],
                                            'skip23star': config_old['function']['autopc_skip23star']}
        config_new['function']['task'] = {'default': config_old['function']['task']}
        config_new['function']['credit'] = {'default': config_old['function']['credit']}
        config_new['function']['shutdown'] = {'default': config_old['function']['shutdown']}
        config_new['recover'] = dict()
        config_new['recover']['loop'] = dict()
        config_new['recover']['loop']['medicine'] = dict()
        config_new['recover']['loop']['medicine']['enable'] = config_old['medicament']['loop']
        config_new['recover']['loop']['stone'] = dict()
        config_new['recover']['loop']['stone']['enable'] = config_old['stone']['loop']
        config_new['recover']['loop']['stone']['max'] = config_old['stone']['maxnum']
        config_new['recover']['schedule'] = dict()
        config_new['recover']['schedule']['medicine'] = dict()
        config_new['recover']['schedule']['medicine']['enable'] = config_old['medicament']['schedule']
        config_new['recover']['schedule']['stone'] = dict()
        config_new['recover']['schedule']['stone']['enable'] = config_old['stone']['schedule']
        config_new['recover']['schedule']['stone']['max'] = config_old['stone']['maxnum']
    
    
    return config_new

def tomlRead():
    toml = dict()
    releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/config.toml'
    devPath = './config.toml'
    if path.exists(devPath):
        with open(devPath, 'r', encoding='UTF-8') as f:
            toml = loads(f.read())
    elif path.exists(releasePath):
        with open(releasePath, 'r', encoding='UTF-8') as f:
            toml = loads(f.read())
    return toml

def dictUpdate(dict_base, dict_userData):
    '递归更新字典中的每一键值对。用户数据只会包含基本字典有的键值对'
    temp = dict_base.copy()
    userData_keys = dict_userData.keys()
    for key in temp.keys():
        if isinstance(temp[key], dict):
            if key in userData_keys:
                temp[key] = dictUpdate(temp[key], dict_userData[key])
        elif key in userData_keys:
            temp[key] = dict_userData[key]
    return temp

