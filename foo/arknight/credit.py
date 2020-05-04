from os import getcwd, listdir
from sys import path
#from time import sleep

path.append(getcwd())
from foo.pictureR import pictureFind
from foo.win import toast

class Task:
    def __init__(self, adb, cwd):
        self.adb = adb
        self.cwd = cwd
        self.switch = False
        self.icon = self.cwd + "/res/ico.ico"
        self.home = self.cwd + "/res/panel/other/home.png"
        self.mainpage = self.cwd + "/res/panel/other/mainpage.png"
        self.screenShot = self.cwd + '/bin/adb/arktemp.png'
        self.mainpageMark = self.cwd + "/res/panel/other/act.png"


    def goToMainpage(self):
        listGoToTemp = self.listGoTo.copy()
        tryCount = 0
        while self.switch:
            self.adb.screenShot()
            for eachStep in listGoToTemp:
                bInfo = pictureFind.matchImg(self.screenShot, eachStep)
                if bInfo != None:
                    listGoToTemp.remove(eachStep)
                    break
            else:
                listGoToTemp = self.listGoTo.copy()
                tryCount += 1
                if tryCount > 5:
                    return False

            if bInfo != None:
                if bInfo['obj'] == 'act.png':
                    return True
                else:
                    self.adb.click(bInfo['result'][0], bInfo['result'][1])