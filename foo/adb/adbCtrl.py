from os import getcwd
from sys import path as syspath
from os import path, remove
from re import findall as refind
from re import split as resplit
from subprocess import PIPE, Popen, call
from time import sleep
from PyQt5.QtWidgets import QFileDialog

from cv2 import imdecode, merge
from foo.win import toast
from numpy import frombuffer, zeros, ones
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QWidget

syspath.append(getcwd())
from foo.pictureR import pictureFind
from foo.ui.messageBox import AMessageBox


def delImg(dir):
    if path.exists(dir):
        try:    
            remove(dir)
        except PermissionError:
            return False

    return True



class Cmd:
    def __init__(self, path):
        self.path = path

    def run(self, code, needDecode = True):
        p = Popen(code, shell = True, stdout = PIPE, stderr = PIPE, bufsize = -1, cwd = self.path)
        cmdReturn = p.communicate()
        if needDecode:
            try:
                strout = cmdReturn[0].decode('gbk').replace('\r\n', '\n')
                strerr = cmdReturn[1].decode('gbk').replace('\r\n', '\n')
            except UnicodeDecodeError:
                strout = cmdReturn[0].decode('UTF-8').replace('\r\n', '\n')
                strerr = cmdReturn[1].decode('UTF-8').replace('\r\n', '\n')
        else:
            strout = cmdReturn[0]
            strerr = cmdReturn[1]
        if len(strerr) > 0:
            print(strerr)
        return strout

    def getVersion(self):
        exePath = self.path.replace('/', '\\\\') + '\\\\arkhelper.exe'
        if path.exists(exePath):
            ans = self.run('wmic datafile where \"name=\'{dir}\'\" get version'.format(dir = exePath))
            ans = refind('[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*', ans)
            if len(ans) == 1:
                ans = ans[0]
                if ans[-1] == '0':
                    ans = '.'.join(ans.split('.')[0:3])
            else:
                ans = 'ERR'
        else:
            ans = 'DEV'
        return ans

        
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
        

class Adb(QObject):
    adbErr = pyqtSignal(bool)
    adbNotice = pyqtSignal(str)
    def __init__(self, simulator_data):
        super(Adb, self).__init__()
        self.cmd = Cmd('./bin/adb')
        self.ip = None
        self.simulator = None
        self.screenX = 1440
        self.screenY = 810
        self.simulator_data = simulator_data

        self.backPos = None
        self.homePos = None

        self.submitting = pictureFind.picRead(getcwd() + '/res/logistic/general/submitting.png')

    def getResolution(self):
        return (self.screenX, self.screenY)

    def getTagConfidence(self):
        if (self.screenX/ self.screenY) == (16/ 9):
            if self.screenX <= 1024:
                return 0.7
            elif self.screenX <= 1280:
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
    
    def changeSimulator(self, config):
        choosed_simulator = config.get('simulator') #读取模拟器数据
        try:
            simulator_data = self.simulator_data.get(choosed_simulator)
        except KeyError:
            if choosed_simulator == 'unknow':
                print('无可用模拟器配置！使用默认！')
            else:
                print('模拟器数据读取错误！')
            simulator_data = {'ip': '127.0.0.1:5555', 'adb': 'internal'} #给一组默认配置，防止后续出错
        
        #由adb路径实例化Cmd类便于操作adb
        if simulator_data['adb'] == 'external':
            #要求用户选择adb路径
            AMessageBox.warning(None, '通知', '您选择的模拟器需要手动选取adb路径！')
            adb_dir = QFileDialog.getOpenFileName(None, '选取adb.exe', './', 'adb.exe')[0]
            if adb_dir == '': #用户选择取消
                AMessageBox.warning(None, '警告', '已取消！将使用自带的adb！')
                self.cmd = Cmd('./bin/adb') #使用自带的adb，但并不修改配置文件上的adb路径
            else:
                self.simulator_data.change(f'{choosed_simulator}.adb', adb_dir)
                self.cmd = Cmd(path.dirname(adb_dir))
        elif simulator_data['adb'] == 'internal':
            self.cmd = Cmd('./bin/adb')
        else:
            #已经存储了adb路径
            self.cmd = Cmd(path.dirname(simulator_data['adb'])) #将路径转化为所在目录

        #确定模拟器ip地址
        if simulator_data['ip'] == '*req*':
            #需求用户输入ip
            ip = AMessageBox.input(None, 'IP地址', '请输入模拟器IP地址(如127.0.0.1:7555或emulator-5554):')[0]
            self.simulator_data.change(f'{choosed_simulator}.ip', ip)
            self.ip = ip
        else:
            self.ip = simulator_data['ip']
        
        #adb设置完成

    def autoGetPort(self):
        #针对夜神的自动获取ip地址
        self.cmd.run('adb start-server')
        devicesText = self.cmd.run('adb devices')
        ports = refind(r':[0-9]*' ,devicesText)
        if len(ports) == 1:
            return ports[0][1:]
        else:
            return False

    def connect(self):
        self.cmd.run('adb start-server')
        if 'emulator' in self.ip:
            cmdText = f'connected to {self.ip}' #雷电模拟器不需要连接，做特殊处理
        else:
            cmdText = self.cmd.run('adb connect {0}'.format(self.ip))
            print(cmdText)
        if ('connected to' in cmdText) and ('nable' not in cmdText):
            while True:
                screenMsg = self.cmd.run(f'adb -s {self.ip} shell wm size')
                if screenMsg != '':
                    break
            screenMsg = screenMsg.replace(' ', '')
            screenMsg = screenMsg.replace('\n', '')
            print(screenMsg)
            temp = screenMsg.partition('size:')
            temp = temp[2].split('x')
            self.screenX = int(temp[0])
            self.screenY = int(temp[1])
            if (self.screenX / self.screenY) != (16/9):
                self.adbNotice.emit('检测到模拟器分辨率非16:9或为竖屏，请检查分辨率')
                #toast.broadcastMsg('ArkHelper', '检测到模拟器分辨率非16:9或为竖屏，请检查分辨率', self.ico)
            else:
                if self.screenX > 1920:
                    self.adbNotice.emit('模拟器分辨率设置较高，可能出现无法正常工作的问题，发现请及时反馈。')
                    #toast.broadcastMsg('ArkHelper', '模拟器分辨率设置较高，可能出现无法正常工作的问题，发现请及时反馈。', self.ico)
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

    def getScreen_std(self, isForOcr = False):
        submitCount = 0
        while True:
            tryCount = 0
            for i in range (5):
                pic = self.cmd.run(f'adb -s {self.ip} shell screencap -p', needDecode = False)
                try:
                    if pic[6] == 10:#LF
                        pic = pic.replace(b'\r\n', b'\n')
                    elif pic[6] == 13:#CR
                        pic = pic.replace(b'\r\r\n', b'\n')
                    if isForOcr:
                        return pic

                except IndexError:
                    tryCount += 1
                    if tryCount > 3:
                        self.adbErr.emit(True)
                        print('截取屏幕失败：无法获取到标准输入流，请重启后再试')
                        return zeros((810, 1440, 3), dtype='uint8')
                try:
                    pic = imdecode(frombuffer(pic, dtype="uint8"), -1)
                    if pic is None:
                        raise AdbError
                    break
                except Exception as e:
                    self.adbErr.emit(True)
                    print('截取屏幕失败：截图解码失败')
                    print(e)
                    return zeros((810, 1440, 3), dtype='uint8') #返回一张纯黑图片，便于后续程序执行，正常退出
            else:
                self.adbErr.emit(True)
                print('截取屏幕失败：未知原因')
                return zeros((810, 1440, 3), dtype='uint8')
            if pictureFind.matchImg_roi(pic, self.submitting, (0, 700, 1440, 110), confidencevalue = 0.7) == None:
                return pic
            else:
                submitCount += 1
                sleep(1)
                if submitCount > 10:
                    self.adbErr.emit(True)
                    print('长时间提示正在连接至神经网络，请检查网络连接')
                    return zeros((810, 1440, 3), dtype='uint8')

    def click(self, x, y, isSleep = True):
        x = int(x)#int((x / 1440) * self.screenX)
        y = int(y)#int((y / 810) * self.screenY)
        self.cmd.run('adb -s {device} shell input tap {0} {1}'.format(x, y, device = self.ip))
        if isSleep:
            sleep(1)
    
    def swipe(self,x0, y0, x1, y1, lastTime = 1000):
        x0 = (x0 / 1440) * self.screenX
        y0 = (int(y0) / 810) * self.screenY
        x1 = (x1 / 1440) * self.screenX
        y1 = (int(y1) / 810) * self.screenY
        #if self.simulator == 'leidian':
        #    self.cmd.run('adb shell input swipe {x0_start} {y0_start} {x1_end} {y1_end} {time}'.\
        #            format(x0_start = x0, y0_start = y0, x1_end = x1, y1_end = y1, time = lastTime))
        #else:
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

    def clickBack(self):
        if self.backPos == None:
            ans = pictureFind.matchImg(self.getScreen_std(), './res/panel/other/home.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                self.backPos = [int(ans['result'][0]/3), int(ans['result'][1])]
                self.homePos = [int(ans['result'][0]), int(ans['result'][1])]
        self.click(self.backPos[0], self.backPos[1])
        
    def clickHome(self):
        if self.homePos == None:
            ans = pictureFind.matchImg(self.getScreen_std(), './res/panel/other/home.png', confidencevalue=0.3, targetSize=(0,0))
            if ans != None:
                self.backPos = [int(ans['result'][0]/3), int(ans['result'][1])]
                self.homePos = [int(ans['result'][0]), int(ans['result'][1])]
        self.click(self.homePos[0], self.homePos[1])

class AdbError(Exception):
    pass
