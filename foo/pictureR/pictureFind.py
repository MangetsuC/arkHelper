from aircv import imread, find_template
from PIL import Image
from os import remove, path

'''def delImg(dir):
    if path.exists(dir):
        remove(dir)'''


def matchImg(imgsrc,imgobj,confidencevalue=0.8):  #imgsrc=原始图像，imgobj=待查找的图片
    '用于查找原始图片中的单一目标图片，如果原始图片中可找到多个目标图片，则随机返回一个匹配的结果，返回值为一个字典'
    try:
        imsrc = imread(imgsrc)
    except RuntimeError:
        return None
    imobj = imread(imgobj)

    match_result = find_template(imsrc,imobj,confidencevalue) 
    if match_result != None:
        match_result['shape']=(imsrc.shape[1],imsrc.shape[0])  #0为长，1为宽

    #delImg(imgsrc)
    return match_result


def matchMultiImg(imgsrc, imgobj, tempDir, confidencevalue=0.8, maxReturn=-1):
    '用于查找原始图片中的多个目标图片，若不存在图片则返回None，否则返回一个目标图片坐标构成的元组；imgsrc为原始图片路径，imgobj为目标图片路径，tempDir为临时存放处理中的图片的目录，[confidencevalue为置信度，maxReturn在非负的情况下只会返回相应数值的坐标，为0则永远返回None]'
    maxReturn = int(maxReturn)
    try:
        imsrc = imread(imgsrc)
    except RuntimeError:
        return None
    imobj = imread(imgobj)
    imgTemp = Image.open(imgsrc)
    matchPositionXY = []
    while True:
        match_result = find_template(imsrc,imobj,confidencevalue) 
        if match_result != None and maxReturn != 0:
            matchPositionXY.append(match_result['result'])
            maxReturn -= 1
            x1, y2 = match_result['rectangle'][0], match_result['rectangle'][3] #获取左上，右下坐标
            for x in range(y2[0]-x1[0]):
                for y in range(y2[1]-x1[1]):
                    imgTemp.putpixel((x1[0]+ x,x1[1]+ y), (0,0,0))
            imgTemp.save(tempDir + '/temp.png')
        else:
            break
        imsrc = imread(tempDir + '/temp.png')
        imgTemp = Image.open(tempDir + '/temp.png')

    #delImg(imgsrc)
    #delImg(tempDir + '/temp.png')
    return tuple(matchPositionXY) if matchPositionXY != [] else None
    
def matchForWork(imgsrc, imgobj, tempDir):
    '只用于换班'
    peoHaveTalentXY = matchMultiImg(imgsrc, imgobj, tempDir, 0.9)
    onWork = matchMultiImg(imgsrc, 'E:\\Code\\arkHelper\\res\\construction\\onWork.png', tempDir,0.9)
    if peoHaveTalentXY == None:
        return None
    elif onWork == None:
        return peoHaveTalentXY[0]
    else:
        for i1 in range(len(peoHaveTalentXY)):
            for i2 in onWork:
                if abs(peoHaveTalentXY[i1][0]-i2[0])< 80 and abs(peoHaveTalentXY[i1][1]-i2[1])< 90:
                    peoHaveTalentXY = list(peoHaveTalentXY)
                    peoHaveTalentXY [i1] = None
                    peoHaveTalentXY = tuple(peoHaveTalentXY)
                    break

        for eachXY in peoHaveTalentXY:
            if eachXY != None:
                return eachXY
        else:
            return None

if __name__ == "__main__":
    from os import listdir
    x = 'E:\\Code\\arkHelper\\res\\construction\\onWork.png'
    talentTrade = ['E:/Code/arkHelper/res/construction/talentTrade/' + each for each in \
            listdir('E:/Code/arkHelper/res/construction/talentTrade')]
    print(talentTrade)
    #for i in talentTrade:
    b = matchMultiImg('E:/Code/arkHelper/bin/adb/arktemp.png', talentTrade[0], 'E:/Code/arkHelper/bin/adb',0.9)
    a = matchMultiImg('E:/Code/arkHelper/bin/adb/arktemp.png', x, 'E:/Code/arkHelper/bin/adb',0.9)
    for i1 in range(len(b)):
        for i2 in a:
            if abs(b[i1][0]-i2[0])< 80 and abs(b[i1][1]-i2[1])< 90:
                b = list(b)
                b [i1] = None
                b = tuple(b)

    print(b)