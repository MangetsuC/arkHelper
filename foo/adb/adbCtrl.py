from os import path, popen, remove, system
from time import sleep, perf_counter

from PIL import Image

def delImg(dir):
    if path.exists(dir):
        remove(dir)

class adb:
    def __init__(self, adbPath, ip = "127.0.0.1", port = "7555"):
        self.adbPath = adbPath
        self.ip = ip + ':' + port
        self.screenX = 1440
        self.screenY = 810

    def connect(self):
        self.cmdText = popen('{0}&&cd {1}&&adb connect {2}'.format(self.adbPath[0:2], self.adbPath, self.ip), 'r').read()
        print(self.cmdText)
        if ('connected to' in self.cmdText) and ('nable' not in self.cmdText):
            screenMsg = popen('{0}&&cd {1}&&adb -s {device} shell wm size'.format(self.adbPath[0:2], self.adbPath, device = self.ip)).read()
            screenMsg = screenMsg.replace(' ', '')
            screenMsg = screenMsg.replace('\n', '')
            #print(screenMsg)
            temp = screenMsg.partition("size:")
            temp = temp[2].split('x')
            self.screenX = int(temp[0])
            self.screenY = int(temp[1])
            #print(temp, self.screenX, self.screenY)
            return True
        else:
            return False

    def screenShot(self, pngName = 'arktemp'):
        delImg("{0}/{1}.png".format(self.adbPath, pngName))

        popen('{0}&&cd {1}&&adb -s {device} shell screencap -p /sdcard/arktemp.png&&adb -s {device} pull /sdcard/arktemp.png {2}/{3}.png'\
            .format(self.adbPath[0:2], self.adbPath, self.adbPath, pngName, device = self.ip))

        start = perf_counter()
        while (not path.exists("{0}/{1}.png".format(self.adbPath, pngName))) and (perf_counter() - start < 20):
            continue
        
        #sleep(1)
        while perf_counter() - start < 20:
            try:
                tempImg = Image.open(self.adbPath + '/' + pngName +'.png')
                out = tempImg.resize((1440,810),Image.ANTIALIAS)
            except:
                continue
            else:
                break
        else:
            return False

        out.save(self.adbPath + '/' + pngName +'.png', 'png')
        return True

    def click(self, x, y, isSleep = True):
        x = (x / 1440) * self.screenX
        y = (int(y) / 810) * self.screenY
        popen('{0}&&cd {1}&&adb -s {device} shell input tap {2} {3}'\
            .format(self.adbPath[0:2], self.adbPath, x, y, device = self.ip))
        if isSleep:
            sleep(1)

    def swipeD(self):
        popen('{0}&&cd {1}&&adb -s {device} shell input swipe 800 300 800 100'.format(self.adbPath[0:2], self.adbPath, device = self.ip))

    def swipeL(self):
        '向左划'
        popen('{0}&&cd {1}&&adb -s {device} shell input swipe {4} {3} {2} {5} 1000'.\
            format(self.adbPath[0:2], self.adbPath, 0, int(self.screenY)/2, \
                int(self.screenX)/4, int(self.screenY)/2, device = self.ip))
        sleep(1.5)
    def swipeR(self):
        '向右划'
        popen('{0}&&cd {1}&&adb -s {device} shell input swipe {2} {3} {4} {5} 1000'.\
            format(self.adbPath[0:2], self.adbPath, 0, int(self.screenY)/2, \
                int(self.screenX)/4, int(self.screenY)/2, device = self.ip))
        sleep(1.5)
        

if __name__ == "__main__":
    ad = adb('E:\\workSpace\\CodeRelease\\arknightHelper\\arkHelper\\bin\\adb', port="5555")
    ad.connectSwitch = True
    ad.connect()
    '''ad.swipeL()
    ad.swipeR()'''
    i = 0
    while True:
        ad.screenShot("screenshot" + str(i))
        command = input("输入exit以退出：")
        if command == "exit":
            break
        i += 1