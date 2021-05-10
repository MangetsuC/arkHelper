from os import path, remove, getcwd
from time import sleep, perf_counter
from subprocess import Popen, PIPE, call
from re import split as resplit
from foo.win import toast

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
        self.p = Popen(code, shell = True, stdout = PIPE, stderr = PIPE, bufsize = -1, cwd = self.path)
        cmdReturn = self.p.communicate()
        strout = cmdReturn[0].decode('gbk').replace('\r\n', '\n')
        strerr = cmdReturn[1].decode('gbk').replace('\r\n', '\n')
        if len(strerr) > 0:
            print(strerr)
        #self.p.wait(timeout = waitTime)
        return strout
        
    def blockRun(self, code):
        return call(code, cwd = self.path ,timeout = 60)

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
    def __init__(self, ico, adbPath, config = None):
        self.adbPath = adbPath
        self.cmd = Cmd(self.adbPath)
        self.ip = None
        self.simulator = None
        self.changeConfig(config)
        self.screenX = 1440
        self.screenY = 810
        self.ico = ico

    def getTagConfidence(self):
        if (self.screenX/ self.screenY) == (16/ 9):
            if self.screenX <= 1080:
                return 0.75
            elif self.screenX > 1920:
                return 0.75
            else:
                return 0.8
        else:
            return 0.8

    def startAdb(self):
        adbstr = self.cmd.run('adb start-server')
        print(adbstr)
        if 'daemon started successfully' in adbstr:
            print('start adb successfully')
            return True
        elif adbstr == '':
            print('already strat adb')
            return True
        else:
            print('start adb failed')
            return False
    
    def changeConfig(self, config):
        if config == None:
            self.ip = '127.0.0.1:5555'
        else:
            self.simulator = config.get('connect', 'simulator')
            if self.simulator == 'yeshen':
                if config.has_option('connect', 'noxpath'):
                    self.cmd = Cmd(config.get('connect', 'noxpath'))
                else:
                    print('夜神模拟器未给出模拟器路径')
            else:
                self.cmd = Cmd(self.adbPath)
            self.ip = config.get('connect', 'ip') + ':' + config.get('connect', 'port')
        print(self.ip)


    def connect(self):
        self.cmd.run('adb start-server')
        if self.simulator == 'leidian':
            self.cmdText = 'connected to leidian' #雷电模拟器不需要连接，做特殊处理
        else:
            self.cmdText = self.cmd.run('adb connect {0}'.format(self.ip))
            print(self.cmdText)
        if ('connected to' in self.cmdText) and ('nable' not in self.cmdText):
            while True:
                if self.simulator == 'leidian':
                    screenMsg = self.cmd.run('adb shell wm size')
                else:
                    screenMsg = self.cmd.run('adb -s {device} shell wm size'.format(device = self.ip))
                if screenMsg != None:
                    break
            screenMsg = screenMsg.replace(' ', '')
            screenMsg = screenMsg.replace('\n', '')
            print(screenMsg)
            temp = screenMsg.partition('size:')
            temp = temp[2].split('x')
            self.screenX = int(temp[0])
            self.screenY = int(temp[1])
            if (self.screenX / self.screenY) != (16/9):
                toast.broadcastMsg('ArkHelper', '检测到模拟器分辨率非16:9或为竖屏，请检查分辨率', self.ico)
            else:
                if self.screenX > 1920:
                    toast.broadcastMsg('ArkHelper', '模拟器分辨率设置较高，可能出现无法正常工作的问题，发现请及时反馈。', self.ico)
            #print(temp, self.screenX, self.screenY)
            return True
        else:
            self.killAdb()
            return False

    def killAdb(self):
        #self.cmd.run('adb kill-server')
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
            
        if self.simulator == 'yeshen':
            self.cmd.run('adb -s {device} shell screencap -p /sdcard/arktemp.png'\
                .format(device = self.ip))#这两段拷贝到文件，夜神处理
            self.cmd.run('adb -s {device} pull \"/sdcard/arktemp.png\" \"{0}/{1}.png\"'\
                .format(self.adbPath, pngName, device = self.ip))
        elif self.simulator == 'leidian':
            self.cmd.run('adb exec-out screencap -p > {0}/{1}.png'\
                .format(self.adbPath, pngName))
        else:
            self.cmd.run('adb -s {device} exec-out screencap -p > \"{0}/{1}.png\"'\
                .format(self.adbPath, pngName, device = self.ip))

        if self.simulator != 'yeshen':
            pic0 = open(self.adbPath + '/' + pngName +'.png', 'br')
            bys = pic0.read().replace(b'\r\n', b'\n')
            pic0.close()
            
            pic1 = open(self.adbPath + '/' + pngName +'.png', 'bw')   
            pic1.write(bys)
            pic1.close()

        '''tempImg = Image.open(self.adbPath + '/' + pngName +'.png')
        out = tempImg.resize((1440,810),Image.ANTIALIAS)
        out.save(self.adbPath + '/' + pngName +'.png', 'png')'''
        return True

    def click(self, x, y, isSleep = True):
        x = (x / 1440) * self.screenX
        y = (int(y) / 810) * self.screenY
        if self.simulator == 'leidian':
            self.cmd.run('adb shell input tap {0} {1}'.format(x, y))
        else:
            self.cmd.run('adb -s {device} shell input tap {0} {1}'.format(x, y, device = self.ip))
        if isSleep:
            sleep(1)
    
    def swipe(self,x0, y0, x1, y1, lastTime = 1000):
        x0 = (x0 / 1440) * self.screenX
        y0 = (int(y0) / 810) * self.screenY
        x1 = (x1 / 1440) * self.screenX
        y1 = (int(y1) / 810) * self.screenY
        if self.simulator == 'leidian':
            self.cmd.run('adb shell input swipe {x0_start} {y0_start} {x1_end} {y1_end} {time}'.\
                    format(x0_start = x0, y0_start = y0, x1_end = x1, y1_end = y1, time = lastTime))
        else:
            self.cmd.run('adb -s {device} shell input swipe {x0_start} {y0_start} {x1_end} {y1_end} {time}'.\
                    format(device = self.ip, x0_start = x0, y0_start = y0, x1_end = x1, y1_end = y1, time = lastTime))
        pass

    def speedToLeft(self):
        self.swipe(0,405,1440,405,100)
        sleep(1)
        self.swipe(0,405,1440,405,100)
        sleep(1)

    def onePageRight(self):
        self.swipe(450,405,0,405,1000)
        sleep(1)

    def mainToPreChap(self):
        self.swipe(650, 400, 1050, 400, 500)

    def mainToNextChap(self):
        self.swipe(1050, 400, 650, 400, 500)