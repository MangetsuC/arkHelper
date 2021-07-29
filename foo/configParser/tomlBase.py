from os import getcwd
from sys import path as syspath

from toml import dumps, loads

syspath.append(getcwd())

from foo.configParser import iniParser


def defaultConfig():
    default = '''
    simulator = 'bluestacks'
    notice = ''

    [theme]
    themecolor = 'auto'
    fontcolor = 'auto'
    checkedfontcolor = 'auto'
    bordercolor = 'auto'
    fgcolor = 'auto'
    bgcolor = 'auto'
    pressedcolor = 'auto'
    selectedcolor = 'auto'

    [logistic]
    defaultrule = '示例配置'
    manufactory.enable = true
    trade.enable = true
    powerroom.enable = true
    officeroom.enable = true
    meetingroom.enable = true

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

def configUpdate():
    config_old = iniParser.iniParse()
    config_new = dict()
    config_new['simulator'] = config_old['connect']['simulator']
    config_new['notice'] = config_old['notice']['md5']
    config_new['theme'] = config_old['theme']
    config_new['logistic'] = config_old['logistic']
    config_new['logistic'] = dict()
    config_new['logistic']['rule'] = config_old['logistic']['defaultrule']
    config_new['logistic']['manufactory'] = {'default': f"{config_old['logistic']['manufactory']}"}
    config_new['logistic']['trade'] = {'default': f"{config_old['logistic']['trade']}"}
    config_new['logistic']['powerroom'] = {'default': f"{config_old['logistic']['powerroom']}"}
    config_new['logistic']['officeroom'] = {'default': f"{config_old['logistic']['officeroom']}"}
    config_new['logistic']['meetingroom'] = {'default': f"{config_old['logistic']['receptionroom']}"}
    config_new['logistic']['threshold'] = {'work': f"{config_old['logistic']['moodthreshold']}",
                                           'dorm': f"{config_old['logistic']['dormthreshold']}"}
    config_new['function'] = dict()
    config_new['function']['battle'] = {'default': f"{config_old['function']['battle']}"}
    config_new['function']['schedule'] = {'default': f"{config_old['function']['schedule']}"}
    config_new['function']['autopc'] = {'default': f"{config_old['function']['autopc']}",
                                        'skip1star': f"{config_old['function']['autopc_skip1star']}",
                                        'skip5star': f"{config_old['function']['autopc_skip5star']}",
                                        'skip23star': f"{config_old['function']['autopc_skip23star']}"}
    config_new['function']['task'] = {'default': f"{config_old['function']['task']}"}
    config_new['function']['credit'] = {'default': f"{config_old['function']['credit']}"}
    config_new['function']['shutdown'] = {'default': f"{config_old['function']['shutdown']}"}
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

#print(dumps(configUpdate()))
print(dumps(defaultConfig()))
