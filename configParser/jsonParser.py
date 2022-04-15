from os import getlogin, path
from json import loads

def jsonRead():
    releasePath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/schedule.json'
    devPath = './schedule.json'
    json = dict()
    if path.exists(devPath):
        with open(devPath, 'r', encoding = 'UTF-8') as f:
            json = loads(f.read())
    elif path.exists(releasePath):
        with open(releasePath, 'r', encoding = 'UTF-8') as f:
            json = loads(f.read())
    return json
    