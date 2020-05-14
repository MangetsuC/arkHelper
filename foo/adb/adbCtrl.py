from os import path, remove
from time import sleep, perf_counter
from subprocess import Popen, PIPE

from PIL import Image

def delImg(dir):
    if path.exists(dir):
        remove(dir)

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
        
        

class Adb:
    def __init__(self, adbPath, config = None):
        self.adbPath = adbPath
        self.cmd = Cmd(self.adbPath)
        self.ip = None
        self.changeConfig(config)
        self.screenX = 1440
        self.screenY = 810

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
            screenMsg = self.cmd.run('adb -s {device} shell wm size'.format(device = self.ip))
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
            self.cmd.run('adb kill-server')
            return False

    def screenShot(self, pngName = 'arktemp'):
        delImg("{0}/{1}.png".format(self.adbPath, pngName))

        #popen('{0}&&cd {1}&&adb -s {device} shell screencap -p /sdcard/arktemp.png&&adb -s {device} pull /sdcard/arktemp.png {2}/{3}.png'\
        #    .format(self.adbPath[0:2], self.adbPath, self.adbPath, pngName, device = self.ip))
            
        self.cmd.run('adb -s {device} exec-out screencap -p > {0}/{1}.png'\
            .format(self.adbPath, pngName, device = self.ip))

        with open(self.adbPath + '/' + pngName +'.png', 'br') as pic:
            bys = pic.read().replace(b'\r\n', b'\n')
        with open(self.adbPath + '/' + pngName +'.png', 'bw') as pic:    
            pic.write(bys)

        #start = perf_counter()
        #while (not path.exists("{0}/{1}.png".format(self.adbPath, pngName))) and (perf_counter() - start < 20):
        #    continue
        
        #sleep(1)
        '''while perf_counter() - start < 20:
            try:
                tempImg = Image.open(self.adbPath + '/' + pngName +'.png')
                out = tempImg.resize((1440,810),Image.ANTIALIAS)
            except:
                continue
            else:
                break
        else:
            return False'''
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