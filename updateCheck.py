from hashlib import md5
from os import walk, path
from json import loads
import requests

class Md5Analyse:
    def __init__(self, targetPath, onlinePath, exceptionFiles = ''):
        self.targetPath = targetPath
        self.onlinePath = onlinePath
        self.exceptionFiles = exceptionFiles.split(',')
    
    def getAllFiles(self):
        fileList = []
        for root, dirs, files in walk(self.targetPath):
            if files != []:
                for eachFile in files:
                    fileList.append(path.join(root, eachFile))
        return fileList

    def getFileMd5(self, fileName):
        m = md5()   #创建md5对象
        with open(fileName,'rb') as fobj:
            while True:
                data = fobj.read(4096)
                if not data:
                    break
                m.update(data)  #更新md5对象

        return m.hexdigest()    #返回md5对象

    def getFileMd5Dict(self):
        num = self.targetPath.count('\\')
        md5Dict = dict()
        fileList = self.getAllFiles()
        for i in fileList:
            fileDir = '/'.join(i.split('\\')[num + 1:])
            if (fileDir not in self.exceptionFiles) and ('.manifest' not in fileDir):
                md5Dict[fileDir] = self.getFileMd5(i)
        if md5Dict != dict():
            return md5Dict
        else:
            return False

    def compareMd5(self):
        r = requests.get(self.onlinePath + '/md5.txt')
        print(r.status_code)
        if r.status_code == 200:
            onlineData = loads(r.text)
            localData = self.getFileMd5Dict()
            filesToAdd = [x for x in onlineData.keys() if x not in localData.keys()]
            filesToDel = [y for y in localData.keys() if y not in onlineData.keys()]
            filesToUpdate = [z for z in localData.keys() if z in onlineData.keys() and localData[z] != onlineData[z]]
            newFileNum = len(filesToAdd) + len(filesToDel) + len(filesToUpdate)
            return True if newFileNum > 0 else False
        else:
            return False