from aircv import imread, find_template
from PIL import Image
from PIL.ImageOps import invert
from os import remove, path, getcwd, listdir
from re import split as resplit
from cv2 import imdecode,fillConvexPoly,imshow,waitKey,copyTo
from numpy import fromfile,array,zeros

def picRead(pics):
    temp = []
    tempDict = dict()
    if isinstance(pics,list):
        for eachPic in pics:
            tempDict = dict()
            tempDict['pic'] = imdecode(fromfile(eachPic,dtype="uint8"),-1)
            tempDict['obj'] = resplit(r'[\\ /]', eachPic)[-1]
            temp.append(tempDict)
        return temp
    else:
        tempDict['pic'] = imdecode(fromfile(pics,dtype="uint8"),-1)
        tempDict['obj'] = resplit(r'[\\ /]', pics)[-1]
        return tempDict

def matchImg(imgsrc,imgobj,confidencevalue=0.8):  #imgsrc=原始图像，imgobj=待查找的图片
    '用于查找原始图片中的单一目标图片，如果原始图片中可找到多个目标图片，则随机返回一个匹配的结果，返回值为一个字典'
    try:
        if isinstance(imgsrc,str):
            imsrc = imread(imgsrc)
        else:
            imsrc = imgsrc
    except RuntimeError:
        return None
    #imobj = imread(imgobj)
    if isinstance(imgobj,str):
        imobj = imdecode(fromfile(imgobj,dtype="uint8"),-1)
    else:
        imobj = imgobj['pic']    #现在此情况传入的一定是字典

    match_result = find_template(imsrc,imobj,confidencevalue)
    if match_result != None:
        if isinstance(imgobj,str):
            match_result['obj'] = resplit(r'[\\ /]', imgobj)[-1]
        else:
            match_result['obj']=imgobj['obj']

    #delImg(imgsrc)
    return match_result


def matchMultiImg(imgsrc, imgobj, confidencevalue=0.8, maxReturn=-1, colorSpace = (0,0,0), debugMode = False):
    '用于查找原始图片中的多个目标图片，若不存在图片则返回None，否则返回一个目标图片坐标构成的元组；imgsrc为原始图片路径，imgobj为目标图片路径，confidencevalue为置信度，maxReturn在非负的情况下只会返回相应数值的坐标，为0则永远返回None]'
    maxReturn = int(maxReturn)
    if isinstance(imgsrc,str):
        try:
            imsrc = imread(imgsrc)
        except RuntimeError:
            return None
    else:
        imsrc = imgsrc
    imobj = imread(imgobj)
    matchRect = []
    matchPositionXY = []
    while True:
        match_result = find_template(imsrc,imobj,confidencevalue) 
        if match_result != None and maxReturn != 0:
            matchPositionXY.append(list(match_result['result']))
            maxReturn -= 1
            matchRect.append(match_result['rectangle'])
            rect = array([match_result['rectangle'][0],match_result['rectangle'][1],match_result['rectangle'][3],match_result['rectangle'][2]])
            fillConvexPoly(imsrc,rect,0)
        else:
            break
    if debugMode:
        imshow('img', imsrc)
        waitKey(0)
    return [matchPositionXY,imsrc,matchRect] if matchPositionXY != [] else [None,imsrc,None]
    
def levelOcr(imgsrc):
    allNumList = []
    confidence = 0.88 #调试时使用相似度

    mask = zeros((810,1440),dtype = "uint8")
    nowLevel = imread(imgsrc)
    operationList = matchMultiImg(nowLevel, cwd + "/res/fontLibrary/other/OPERATION.png", colorSpace=0)
    if operationList[2] != None:
        for eachRect in operationList[2]:
            opRect = array([(eachRect[0][0]-45,eachRect[0][1]),(eachRect[0][0]+106,eachRect[0][1]),
                            (eachRect[0][0]+106,eachRect[0][1]+50),(eachRect[0][0]-45,eachRect[0][1]+50)])
            fillConvexPoly(mask,opRect,(255,255,255))
    operationWGList = matchMultiImg(nowLevel, cwd + "/res/fontLibrary/other/OPERATIONWG.png", colorSpace=0)
    if operationWGList[2] != None:
        for eachRect in operationWGList[2]:
            opRect = array([(eachRect[0][0]-45,eachRect[0][1]),(eachRect[0][0]+106,eachRect[0][1]),
                            (eachRect[0][0]+106,eachRect[0][1]+50),(eachRect[0][0]-45,eachRect[0][1]+50)])
            fillConvexPoly(mask,opRect,(255,255,255))
    #cv2.imshow('mask',mask)
    #cv2.waitKey(0)
    nowLevel = copyTo(nowLevel,mask)
    #imshow('op',nowLevel)
    #waitKey(0)
    for num in fontLibraryB:
        matchResult = matchMultiImg(nowLevel, cwd + "/res/fontLibrary/B/" + num, confidencevalue=confidence, colorSpace=0)
        oneNumList = matchResult[0]
        #nowLevel = matchResult[1]
        if oneNumList == None:
            continue
        else:
            for each in oneNumList:
                each.append(path.splitext(num)[0])
            allNumList.extend(oneNumList)
            oneNumList = []
    #cv2.imshow('B',nowLevel)
    #cv2.waitKey(0)
    for num in fontLibraryW:
        oneNumList = matchMultiImg(nowLevel, cwd + "/res/fontLibrary/W/" + num, confidencevalue=confidence, colorSpace=0, debugMode=False)[0]
        if oneNumList == None:
            continue
        else:
            for each in oneNumList:
                each.append(path.splitext(num)[0])
            allNumList.extend(oneNumList)
            oneNumList = []
    #cv2.imshow('W',nowLevel)
    #cv2.waitKey(0)
    if allNumList == []:
        return None
    
    return levelAnalyse(allNumList)
    

def levelAnalyse(levelList):
    if levelList == []:
        return dict()
    levelList.sort(key = lambda x:x[0])

    count = 0
    totalx = 0
    totaly = 0
    totalNum = ''
    eachNum = 0
    interval = 1
    beginNum = 0
    sndList = []
    dictResult = dict()
    lastx = levelList[0][0]
    lasty = levelList[0][1]

    for eachLetter in levelList:
        
        if eachLetter[0] - lastx <40:
            if abs(eachLetter[1] - lasty) < 5:
                if eachLetter[0] - lastx <25:
                    totalNum += eachLetter[2]
                else:
                    totalNum = totalNum + '-' + eachLetter[2]
                lastx = eachLetter[0]
                lasty = eachLetter[1]
            else:
                sndList.append(eachLetter)
                continue
        else:
            dictResult[totalNum] = [lastx,lasty]
            lastx = eachLetter[0]
            lasty = eachLetter[1]
            totalNum = eachLetter[2]
        
    dictResult[totalNum] = [lastx,lasty]
    sndrResult = levelAnalyse(sndList)
    dictResult.update(sndrResult)
    
    #print(dictResult)  #调试时启用
    return dictResult

cwd = getcwd()
fontLibraryB = listdir(cwd + "/res/fontLibrary/B")
fontLibraryW = listdir(cwd + "/res/fontLibrary/W")