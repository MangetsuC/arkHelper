from os import getcwd
from os import path as ospath
from subprocess import PIPE, Popen
from sys import path

from cv2 import (COLOR_BGRA2BGR, COLOR_RGBA2GRAY, INTER_AREA, INTER_CUBIC, INTER_LANCZOS4, THRESH_BINARY, THRESH_BINARY_INV,
                 bilateralFilter, convertScaleAbs, cvtColor, filter2D, imwrite,
                 resize, threshold, erode, getStructuringElement, MORPH_RECT, dilate, imshow, waitKey)
from numpy import array as npArray
from numpy import float32, uint8, ones

path.append(getcwd())
from foo.pictureR import pictureFind, wordsTemplate

def ocr_operatorMood(pic, roi = (0, 0, 0, 0)):
    ans = []
    maxMood = pictureFind.imreadCH(getcwd() + '/res/logistic/general/maxMood.png')
    if roi != (0, 0, 0, 0):
        for i in range(5):
            moodRightPart = pictureFind.matchImg_roi(pic, maxMood, 
                                                roi = (roi[0], roi[1] + (roi[3]/5)*i, roi[2], roi[3]/5),
                                                confidencevalue = 0.7)
            if moodRightPart != None:
                for mood in range(24, -1, -1):
                    if pictureFind.matchImg_roi(pic, wordsTemplate.getTemplatePic_NUM(mood, 28), 
                                            roi = (roi[0], roi[1] + (roi[3]/5)*i, moodRightPart['rectangle'][0][0], roi[3]/5),
                                            confidencevalue = 0.7) != None:
                        ans.append(mood)
                        break
                else:
                    ans.append(-1)
            else:
                ans.append(-2)
    return ans

def ocr_roomName(pic, basePoint):
    for eachRoom in ['控制中枢', '会客室', '贸易站', '制造站', '发电站', '宿舍', '加工站', '办公室', '训练室']:
        if pictureFind.matchImg_roi(pic, wordsTemplate.getTemplatePic_CH(eachRoom, 28), 
                                    roi = (basePoint[0]-884, basePoint[1]-73, 222, 53),
                                    confidencevalue = 0.7) != None:
            return eachRoom
    else:
        return ''

def _ocrAnalyse(pic, roi = (0, 0, 0, 0), resolution = (1440, 810)):
    if roi != (0, 0, 0, 0):
        roi = list(roi)
        img = pictureFind.imreadCH(pic)
        maxWidth = img.shape[1]
        maxHeight = img.shape[0]
        roi = (int(roi[0]/1440*resolution[0]), int(roi[1]/810*resolution[1]),
                int(roi[2]/1440*resolution[0]), int(roi[3]/810*resolution[1]))
        if roi[0] + roi[2] > maxWidth:
            roi[2] = maxWidth - roi[0]
        if roi[1] + roi[3] > maxHeight:
            roi[3] = maxHeight - roi[1]
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


