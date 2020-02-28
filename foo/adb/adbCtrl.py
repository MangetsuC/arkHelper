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
        if 'already' in self.cmdText:
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
                self.screenX = tempImg.size[0]
                self.screenY = tempImg.size[1]
                out = tempImg.resize((1440,810),Image.ANTIALIAS)
            except:
                continue
            else:
                break
        else:
            return False

        out.save(self.adbPath + '/' + pngName +'.png', 'png')
        return True

    def click(self, x, y):
        x = (x / 1440) * self.screenX
        y = (y / 810) * self.screenY
        popen('{0}&&cd {1}&&adb -s {device} shell input tap {2} {3}'\
            .format(self.adbPath[0:2], self.adbPath, x, y, device = self.ip))

    def swipeD(self):
        popen('{0}&&cd {1}&&adb -s {device} shell input swipe 800 300 800 100'.format(self.adbPath[0:2], self.adbPath, device = self.ip))

    def swipe(self, startXY, endXY):
        popen('{0}&&cd {1}&&adb -s {device} shell input swipe {2} {3} {4} {5}'.format(self.adbPath[0:2], self.adbPath, startXY[0], startXY[1], endXY[0], endXY[1], device = self.ip))
        #popen('{0}&&cd {1}&&adb shell input swipe {2} {3} {4} {5}'.format(self.adbPath[0:2], self.adbPath, startXY[0], startXY[1], endXY[0], endXY[1]))
        

if __name__ == "__main__":
    ad = adb('E:\\workSpace\\CodeRelease\\arknightHelper\\arkHelper\\bin\\adb', port="5555")
    ad.connectSwitch = True
    ad.connect()
    while True:
        ad.screenShot("source")
        command = input("输入exit以退出：")
        if command == "exit":
            break
