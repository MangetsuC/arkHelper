from os import getcwd
from os import path as ospath
from subprocess import PIPE, Popen
from sys import path

from cv2 import (COLOR_BGRA2BGR, COLOR_RGBA2GRAY, INTER_AREA, INTER_CUBIC, INTER_LANCZOS4, THRESH_BINARY, THRESH_BINARY_INV,
                 bilateralFilter, convertScaleAbs, cvtColor, filter2D, imwrite,
                 resize, threshold, erode, getStructuringElement, MORPH_RECT, dilate)
from numpy import array as npArray
from numpy import float32, uint8, ones

path.append(getcwd())
from foo.pictureR import pictureFind

kernel = npArray([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], float32)

def ocrAnalyse_operatorMood(pic, roi = (0, 0, 0, 0), resolution = (1440, 810)):
    img = pictureFind.imreadCH(pic)
    if roi != (0, 0, 0, 0):
        img = img[roi[1]:roi[1] + roi[3], roi[0]:roi[0] + roi[2]]
    #缩放图片
    img = resize(img, (int(img.shape[1]*5/1440*resolution[0]), int(img.shape[0]*5/1440*resolution[0])), interpolation=INTER_LANCZOS4)
    img = cvtColor(img, COLOR_RGBA2GRAY) #转为灰度图
    img = bilateralFilter(img, 5, 50, 50)
    img = threshold(img, 200, 255, THRESH_BINARY_INV)[1]
    img = erode(img, getStructuringElement(MORPH_RECT, (6,6))) #腐蚀，将线条变细，便于使用windowsOCR，文字较粗识别率大幅下降
    imwrite(ospath.dirname(pic) + '/' + 'ocrTemp.png', img)
    ans = _ocrAnalyse(ospath.dirname(pic) + '/' + 'ocrTemp.png')
    return ans.split('\n')

def _ocrAnalyse(pic, roi = (0, 0, 0, 0), resolution = (1440, 810)):
    if roi != (0, 0, 0, 0):
        roi = (int(roi[0]/1440*resolution[0]), int(roi[1]/810*resolution[1]),
                int(roi[2]/1440*resolution[0]), int(roi[3]/810*resolution[1]))
        cmdReturn = Popen('Windows.Media.Ocr.Cli.exe -r {x} {y} {width} {height} {picName}'.
                    format(x = roi[0], y = roi[1], width = roi[2], height = roi[3], picName = pic), 
                shell = True, stdout = PIPE, stderr = PIPE, bufsize = -1, cwd = getcwd() + '/bin/ocr').communicate()
    else:
        cmdReturn = Popen('Windows.Media.Ocr.Cli.exe {picName}'.format(picName = pic), 
            shell = True, stdout = PIPE, stderr = PIPE, bufsize = -1, cwd = getcwd() + '/bin/ocr').communicate()
    strout = cmdReturn[0].decode('gbk').replace('\r\n', '\n')
    return strout.strip()

def checkOcr():
    if _ocrAnalyse('ocrTest.png') == '成功':
        return True
    else:
        return False

if __name__ == '__main__':
    print(checkOcr())
    
    for i in range(5):
        print(f'now {i}')
        path = rf'{getcwd()}\bin\adb\screenshot{i}.png'
        print(ocrAnalyse_operatorMood(path, 
                roi = (344, 574, 455 - 344, 761 - 574))) #这个即为房间详情看心情的范围
    #print(ocrAnalyse(r'E:\workSpace\CodeRelease\arknightHelper\arkHelper\bin\adb\test0.png'))

