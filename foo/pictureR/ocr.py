from subprocess import PIPE, Popen
from os import getcwd

def ocrAnalyse(workPath, pic, roi = (0, 0, 0, 0)):
    cmdReturn = Popen('Windows.Media.Ocr.Cli.exe -r {x} {y} {width} {height} {picName}'.format(
        x = roi[0], y = roi[1], width = roi[2], height = roi[3], picName = pic
    ), shell = True, stdout = PIPE, stderr = PIPE, bufsize = -1, cwd = workPath).communicate()
    strout = cmdReturn[0].decode('gbk').replace('\r\n', '\n')
    return strout.strip()

def checkOcr(workPath):
    if ocrAnalyse(workPath, 'ocrTest.png') == '成功':
        return True
    else:
        return False

if __name__ == '__main__':
    test = ocrAnalyse(getcwd() + '/bin/ocr', getcwd() + '/bin/adb/screenshot7.png', roi = (545, 344, 73, 54))
    test = test.split('\n')
    test = checkOcr(getcwd() + '/bin/ocr')
    print(test)

