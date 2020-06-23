from os import path, remove
from time import sleep, perf_counter
from subprocess import Popen, PIPE
from re import split as resplit

from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

def delImg(dir):
    if path.exists(dir):
        try:    
            remove(dir)
        except PermissionError:
            return False

    return True



class Cmd():
    def __init__(self, path):
        self.path = path
        self.p = None
        self.path 

    def run(self, code, waitTime = 60):
        self.p = Popen(code, shell = True, stdout = PIPE, stderr = PIPE, bufsize = 1, cwd = self.path)
        strout = self.p.communicate()[0].decode('gbk').replace('\r\n', '\n')
        strerr = self.p.communicate()[1].decode('gbk').replace('\r\n', '\n')
        if len(strerr) > 0:
            print(strerr)
        self.p.wait(timeout = waitTime)
        return strout
        
    def getTaskList(self, taskName):
        task = self.run('tasklist')
        taskList = task.split('\n')
        taskAdb = []
        for eachTask in taskList:
            if taskName in eachTask:
                taskAdb.append(eachTask)
        pidList = []
        if taskAdb != []:
            for eachAdb in taskAdb:
                pid = resplit(r'\s+', eachAdb)[1]
                pidList.append(pid)

        return pidList

    def killTask(self, pid):
        self.run(f'taskkill /PID {pid} /F')

    def shutdown(self, time = 60):
        self.run(f'shutdown /s /t {time}')
        

class Adb:
    def __init__(self, adbPath, config = None):
        self.adbPath = adbPath
        self.cmd = Cmd(self.adbPath)
        self.ip = None
        self.changeConfig(config)
        self.screenX = 1440
        self.screenY = 810

    def startAdb(self):
        self.cmd.run('adb start-server')
    
    def changeConfig(self, config):
        if config == None:
            self.ip = '127.0.0.1:5555'
        else:
            self.ip = config.get('connect', 'ip') + ':' + config.get('connect', 'port')
        print(self.ip)


    def connect(self):
        self.cmdText = self.cmd.run('adb connect {0}'.format(self.ip))
        print(self.cmdText)
        if ('connected to' in self.cmdText) and ('nable' not in self.cmdText):
            while True:
                screenMsg = self.cmd.run('adb -s {device} shell wm size'.format(device = self.ip))
                if screenMsg != None:
                    break
            screenMsg = screenMsg.replace(' ', '')
            screenMsg = screenMsg.replace('\n', '')
            print(screenMsg)
            temp = screenMsg.partition("size:")
            temp = temp[2].split('x')
            self.screenX = int(temp[0])
            self.screenY = int(temp[1])
            #print(temp, self.screenX, self.screenY)
            return True
        else:
            self.killAdb()
            return False

    def killAdb(self):
        self.cmd.run('adb kill-server')
        adbPidList = self.cmd.getTaskList('adb.exe')
        if adbPidList != []:
            for eachAdbPid in adbPidList:
                self.cmd.killTask(eachAdbPid)
    
    def screenShot(self, pngName = 'arktemp'):
        while True:
            tempFlag = delImg("{0}/{1}.png".format(self.adbPath, pngName))
            if tempFlag:
                break
            else:
                sleep(1)
            
        self.cmd.run('adb -s {device} exec-out screencap -p > {0}/{1}.png'\
            .format(self.adbPath, pngName, device = self.ip))

        pic0 = open(self.adbPath + '/' + pngName +'.png', 'br')
        bys = pic0.read().replace(b'\r\n', b'\n')
        pic0.close()
        
        pic1 = open(self.adbPath + '/' + pngName +'.png', 'bw')   
        pic1.write(bys)
        pic1.close()

        tempImg = Image.open(self.adbPath + '/' + pngName +'.png')
        out = tempImg.resize((1440,810),Image.ANTIALIAS)
        out.save(self.adbPath + '/' + pngName +'.png', 'png')
        return True

    def click(self, x, y, isSleep = True):
        x = (x / 1440) * self.screenX
        y = (int(y) / 810) * self.screenY
        self.cmd.run('adb -s {device} shell input tap {0} {1}'\
            .format(x, y, device = self.ip))
        if isSleep:
            sleep(1)