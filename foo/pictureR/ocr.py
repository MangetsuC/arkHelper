from os import getcwd
from sys import path

path.append(getcwd())
from foo.pictureR import pictureFind, wordsTemplate

#实际上并没有真正用到ocr技术
def ocr_operatorMood(pic, roi = (0, 0, 0, 0), isDorm = False):
    ans = []
    maxMood = pictureFind.imreadCH(getcwd() + '/res/logistic/general/maxMood.png')
    if roi != (0, 0, 0, 0):
        for i in range(5):
            moodRightPart = pictureFind.matchImg_roi(pic, maxMood, 
                                                roi = (roi[0], roi[1] + (roi[3]/5)*i, roi[2], roi[3]/5),
                                                confidencevalue = 0.7)
            if moodRightPart != None:
                moodPerDigit = []
                for num in range(10):
                    if len(moodPerDigit) == 2:
                        break
                    numCoor = pictureFind.matchMultiImg_roi(pic, num0_9[num], 
                                        roi = (roi[0]*1920/1440, (roi[1] + (roi[3]/5)*i)*1920/1440, 
                                        moodRightPart['rectangle'][0][0]*1920/1440, roi[3]/5*1920/1440),
                                        targetSize = (1920, 1080), confidencevalue = 0.8)
                    if numCoor != None:
                        for eachNum in numCoor:
                            moodPerDigit.append([num, eachNum])
                moodPerDigit.sort(key = lambda x:x[1][0])
                numLen = len(moodPerDigit)
                if numLen == 0:
                    ans.append(-1)
                else:
                    realMood = 0
                    for num in range(numLen):
                        realMood += moodPerDigit[num][0]*(10**(numLen - num - 1))
                    if isDorm: #避免识别错误
                        if realMood > 24:
                            realMood = 0
                    else:
                        if realMood > 24:
                            realMood = 24
                    ans.append(realMood)
            else:
                ans.append(-2)
    return ans

def ocr_roomName(ocrResult):
    for eachRoom in ['控制中枢', '会客室', '贸易站', '制造站', '发电站', '宿舍', '加工站', '办公室', '训练室']:
        if eachRoom in ocrResult:
            return eachRoom
    else:
        return ''

num0 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/0.png')
num1 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/1.png')
num2 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/2.png')
num3 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/3.png')
num4 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/4.png')
num5 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/5.png')
num6 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/6.png')
num7 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/7.png')
num8 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/8.png')
num9 = pictureFind.picRead(getcwd() + '/res/logistic/moodNum/9.png')
num0_9 = [num0, num1, num2, num3, num4, num5, num6, num7, num8, num9]


