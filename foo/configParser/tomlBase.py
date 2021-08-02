from os import getlogin, path, getcwd
from sys import path as syspath

from toml import dumps, loads

syspath.append(getcwd())

from foo.configParser import iniParser, jsonParser


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
    default = false
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
    work = 0 #基建中心情低于此值的工作中干员会被撤下
    dorm = 24 #宿舍中心情高于此值的干员会被撤下

    [function]
    loop.default = true #循环作战是否默认打开，下同
    schedule.default = false #计划作战

    autopc.default = false #自动公招
    autopc.skip1star = true #自动公招保留1星tag组合
    autopc.skip5star = true #自动公招保留5星tag组合
    autopc.skip23star = false #自动公招保留2，3星tag组合
    #自动公招始终会保留6星tag高级资深干员
    
    task.default = true #自动交付任务
    credit.default = false #自动访问好友获取信用点
    shutdown.default = false #自动关机

    [recover]
    loop.medicine.enable = false #循环作战中使用理智药剂恢复理智
    loop.stone.enable = false #循环作战中使用源石恢复理智
    loop.stone.max = 0 #循环作战中使用源石的最大数量

    schedule.medicine.enable = false #计划作战中使用理智药剂恢复理智
    schedule.stone.enable = false #计划作战中使用源石恢复理智
    schedule.stone.max = 0 #计划作战中使用源石的最大数量
    '''
    return loads(default)

def defaultSimulator():
    default = '''
    [bluestacks]
    ip = '127.0.0.1:5555'
    adb = 'internal'
    name = '蓝叠(设置中开启adb)'

    [mumu]
    ip = '127.0.0.1:7555'
    adb = 'internal'
    name = '蓝色mumu(旧版)'

    [yeshen]
    ip = '*req*'
    adb = 'external'
    name = '夜神模拟器'

    [leidian]
    ip = 'emulator-5554'
    adb = 'internal'
    name = '雷电模拟器'

    [xiaoyao]
    ip = '127.0.0.1:21503'
    adb = 'internal'
    name = '逍遥模拟器'
    '''
    return loads(default)

def defaultSchedule():
    default = '''
    [[main]]
    allplan = '未选择'
    sel = []

    [[main]]
    未选择 = []
    '''
    return loads(default)

def json2toml():
    return jsonParser.jsonRead()

def ini2toml_config():
    '将现有的ini转为toml'
    config_old = iniParser.ini2dict()
    config_new = dict()
    if config_old != dict(): #存在旧配置文件才进行以下操作
        config_new['simulator'] = config_old['connect']['simulator']
        config_new['notice'] = config_old['notice']['md5']
        config_new['theme'] = config_old['theme']
        config_new['logistic'] = config_old['logistic']
        config_new['logistic'] = dict()
        config_new['logistic']['default'] = config_old['function']['logistic']
        config_new['logistic']['rule'] = config_old['logistic']['defaultrule']
        config_new['logistic']['manufactory'] = {'default': config_old['logistic']['manufactory']}
        config_new['logistic']['trade'] = {'default': config_old['logistic']['trade']}
        config_new['logistic']['powerroom'] = {'default': config_old['logistic']['powerroom']}
        config_new['logistic']['officeroom'] = {'default': config_old['logistic']['officeroom']}
        config_new['logistic']['meetingroom'] = {'default': config_old['logistic']['receptionroom']}
        config_new['logistic']['threshold'] = {'work': config_old['logistic']['moodthreshold'],
                                            'dorm': config_old['logistic']['dormthreshold']}
        config_new['function'] = dict()
        config_new['function']['loop'] = {'default': config_old['function']['battle']}
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

def tomlRead(filename):
    '在两个不同的目录下读取相关文件'
    toml = dict()
    releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/{filename}' #小助手各类配置通常的存储位置
    devPath = f'./{filename}' #当前目录下的配置文件会优先读取，这样可以不干扰日常使用
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
