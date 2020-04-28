from aircv import imread, find_template
from PIL import Image
from PIL.ImageOps import invert
from os import remove, path, getcwd, listdir
from re import split as resplit

"""def delImg(dir):
    if path.exists(dir):
        remove(dir)"""


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
        match_result['obj']=resplit(r'[\\ /]', imgobj)[-1]

    #delImg(imgsrc)
    return match_result


def matchMultiImg(imgsrc, imgobj, tempDir, confidencevalue=0.8, maxReturn=-1, colorSpace = (0,0,0)):
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
            matchPositionXY.append(list(match_result['result']))
            maxReturn -= 1
            x1, y2 = match_result['rectangle'][0], match_result['rectangle'][3] #获取左上，右下坐标
            for x in range(y2[0]-x1[0]):
                for y in range(y2[1]-x1[1]):
                    imgTemp.putpixel((x1[0]+ x,x1[1]+ y), colorSpace)
            imgTemp.save(tempDir + '/temp.png')
        else:
            break
        imsrc = imread(tempDir + '/temp.png')
        imgTemp = Image.open(tempDir + '/temp.png')

    #delImg(imgsrc)
    #delImg(tempDir + '/temp.png')
    return matchPositionXY if matchPositionXY != [] else None
    
def levelOcr(imgsrc, tempDir):
    cwd = getcwd()
    allNumList = []
    confidence = 0.88 #调试时使用相似度

    for num in fontLibraryW:
        oneNumList = matchMultiImg(imgsrc, cwd + "/res/fontLibrary/W/" + num, tempDir,confidencevalue=confidence)
        if oneNumList == None:
            continue
        else:
            for each in oneNumList:
                each.append(path.splitext(num)[0])
            allNumList.extend(oneNumList)
            oneNumList = []

    for num in fontLibraryB:
        oneNumList = matchMultiImg(imgsrc, cwd + "/res/fontLibrary/B/" + num, tempDir, confidencevalue=confidence)
        if oneNumList == None:
            continue
        else:
            for each in oneNumList:
                each.append(path.splitext(num)[0])
            allNumList.extend(oneNumList)
            oneNumList = []

    if allNumList == []:
        return None
    
    return levelAnalyse(allNumList)
    

def levelAnalyse(levelList):
    levelList.sort(key = lambda x:x[0])

    count = 0
    totalx = 0
    totaly = 0
    totalNum = ''
    eachNum = 0
    interval = 1
    beginNum = 0
    lineList = []
    dictResult = dict()
    while eachNum <= len(levelList):
        if eachNum == len(levelList):
            dictResult[totalNum] = (int(totalx / count), int(totaly / count))
            if lineList != []:
                dictResult_temp = levelAnalyse(lineList)
                dictResult.update(dictResult_temp)
            break
        elif eachNum == beginNum:
            totalx += levelList[beginNum][0]
            totaly += levelList[beginNum][1]
            totalNum += levelList[beginNum][2]
            count += 1
            eachNum += 1
            
        else:
            if ((levelList[eachNum][0] - levelList[eachNum - interval][0]) > 50) and ((levelList[eachNum][0] - levelList[eachNum - 1][0]) < 50):
                interval += 1
                lineList.append(levelList[eachNum])
                eachNum += 1
                continue
            if (levelList[eachNum][0] - levelList[eachNum - interval][0]) < 50:
                if (abs(levelList[eachNum][1] - levelList[eachNum - interval][1])) < 50:
                    totalx += levelList[eachNum][0]
                    totaly += levelList[eachNum][1]
                    totalNum += levelList[eachNum][2]
                    interval = 1
                    count += 1
                    eachNum += 1
                else:
                    interval += 1
                    lineList.append(levelList[eachNum])
                    eachNum += 1    
            else:
                dictResult[totalNum] = (int(totalx / count), int(totaly / count))
                interval = 1
                totalx = 0
                totaly = 0
                totalNum = ''
                count = 0
                beginNum = eachNum
                continue

    return dictResult

fontLibraryB = listdir(getcwd() + "/res/fontLibrary/B")
fontLibraryW = listdir(getcwd() + "/res/fontLibrary/W")

if __name__ == "__main__":
    '''for i in range(10):
        imsrc = Image.open("E:/workSpace/CodeRelease/arknightHelper/source/after/" + str(i) + 'w.jpg')
        imsrc = invert(imsrc)
        imsrc.save("E:/workSpace/CodeRelease/arknightHelper/source/after/" + str(i) + 'b.jpg')'''

    
    
    '''a = matchMultiImg(r"E:\workSpace\CodeRelease\arknightHelper\source\screenshot35.png", \
        r"E:\workSpace\CodeRelease\arknightHelper\source\after\5b.jpg",\
             r"E:\workSpace\CodeRelease\arknightHelper\source\after", confidencevalue=0.8)'''

    #l1 = listdir(r"E:\workSpace\CodeRelease\arknightHelper\test")
    #for i in l1:
    #    a = levelOcr("E:/workSpace/CodeRelease/arknightHelper/test/{0}".format(i), "E:/workSpace/CodeRelease/arknightHelper/source/temp")
        
    #a = levelOcr("E:/workSpace/CodeRelease/arknightHelper/test/screenshot29.png", "E:/workSpace/CodeRelease/arknightHelper/source/temp")
    a = matchImg(r'E:\workSpace\CodeRelease\arknightHelper\source\test\screenshot3.png', r'E:\workSpace\CodeRelease\arknightHelper\arkHelper\res\panel\other/get.png', 1.0)
    print(a)