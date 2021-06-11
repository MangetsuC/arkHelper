from os import getcwd
from sys import path

path.append(getcwd())
from foo.pictureR import pictureFind, wordsTemplate

#实际上并没有真正用到ocr技术
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
                    if pictureFind.matchImg_roi(pic, wordsTemplate.getTemplatePic_NUM(mood, 38), 
                                        roi = (roi[0]*1920/1440, (roi[1] + (roi[3]/5)*i)*1920/1440, 
                                        moodRightPart['rectangle'][0][0]*1920/1440, roi[3]/5*1920/1440),
                                            confidencevalue = 0.7, targetSize = (1920, 1080)) != None:
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



