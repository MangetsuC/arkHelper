from os import getcwd, listdir, path, remove
from re import split as resplit

from cv2 import (COLOR_BGR2GRAY, TM_CCOEFF_NORMED, Canny, copyTo, cvtColor,
                 fillConvexPoly, imdecode, imshow, matchTemplate, minMaxLoc, resize, imshow, waitKey)
from cv2 import split as cvsplit
from cv2 import SIFT_create, BFMatcher
from numpy import array, fromfile, zeros, ndarray, sqrt, mat, power, random, shape, nonzero, mean, inf, where
from numpy import sum as np_sum
from numpy import int as np_int

MODE = 'TEMPLATE'


def imreadCH(filename):
    if isinstance(filename, str):
        return imdecode(fromfile(filename,dtype="uint8"),-1)
    elif isinstance(filename, ndarray):
        return filename

def sift_match(img1, img2):
    # Initiate SIFT detector
    sift = SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # BFMatcher with default params
    bf = BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    # Apply ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.5*n.distance:
            good.append([m])

    pts = []
    for i in good:
        pts.append(kp1[i[0].queryIdx].pt)

    if len(pts) > 20:
        return pts
    else:
        return None

def dist(a, b): 
    m = a.shape[0]
    n = b.shape[0]
    res = zeros((m, n))
    for i in range(m):
        res[i] = sqrt(np_sum((a[i] - b) ** 2, axis=1))
    return res

def dbscan(data, eps, minpts):
    if data is None:
        return None
    dis = dist(data, data)  # 求两两之间距离
    n = data.shape[0]  # 样本数
    k = 0  # 类编号
    visit = zeros(n)  # 是否被访问过
    res = zeros(n).astype(np_int)  # 聚类结果
    random_id = random.permutation(n)  # 随机排列
    for s in random_id:
        if visit[s] == 0:
            visit[s] = 1
            neps = list(where(dis[s] <= eps)[0])  # 找到 eps 范围邻域内所有点(包括了自己)
            if len(neps)-1 < minpts:  # 数量不足 minpts 暂时设为噪声点
                res[s] = -1
            else:  
                k += 1
                res[s] = k  # 数量达到 minpts 归为 k 类
                while len(neps) > 0:
                    j = random.choice(neps)
                    neps.remove(j)
                    if res[j] == -1:  # 如果之前被标为噪声点，则归为该类, 也可以归为边界点
                        res[j] = k
                    if visit[j] == 0:  # 没有被访问过
                        visit[j] = 1
                        j_neps = list(where(dis[j] <= eps)[0])  # 找邻域
                        if len(j_neps)-1 < minpts:
                            res[j] = k  # 非核心点，可归为该类, 也可以归为边界点
                        else:
                            res[j] = k  # 核心点，加入集合
                            neps = list(set(neps + j_neps))
    ans = []
    if k == 0:
        return None
    for i in range(k):
        tempx = 0
        tempy = 0
        length = 0
        i += 1
        for j in range(len(res)):
            if res[j] == i:
                tempx += data[j][0]
                tempy += data[j][1]
                length += 1
        ans.append((int(tempx/length), int(tempy/length)))

    return ans

def find_sift(im_source, im_search):
    temp = sift_match(im_source, im_search)
    if temp != None:
        temp = array(temp)
        return dbscan(temp, 20, 5)
    else:
        return None


def find_template(im_source, im_search, threshold=0.5, rgb=False, bgremove=False):
    '''
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        im_source(string): 图像、素材
        im_search(string): 需要查找的图片
        threshold: 阈值，当相识度小于该阈值的时候，就忽略掉

    Returns:
        A tuple of found [(point, score), ...]

    Raises:
        IOError: when file read error
    '''
    #本函数来自于 https://github.com/NetEaseGame/aircv ，做了一定修改

    method = TM_CCOEFF_NORMED

    if rgb:
        s_bgr = cvsplit(im_search) # Blue Green Red
        i_bgr = cvsplit(im_source)
        weight = (0.3, 0.3, 0.4)
        resbgr = [0, 0, 0]
        for i in range(3): # bgr
            resbgr[i] = matchTemplate(i_bgr[i], s_bgr[i], method)
        res = resbgr[0]*weight[0] + resbgr[1]*weight[1] + resbgr[2]*weight[2]
    else:
        s_gray = cvtColor(im_search, COLOR_BGR2GRAY)
        i_gray = cvtColor(im_source, COLOR_BGR2GRAY)
        # 边界提取(来实现背景去除的功能)
        if bgremove:
            s_gray = Canny(s_gray, 100, 200)
            i_gray = Canny(i_gray, 100, 200)

        res = matchTemplate(i_gray, s_gray, method)
    w, h = im_search.shape[1], im_search.shape[0]

    min_val, max_val, min_loc, max_loc = minMaxLoc(res)
    top_left = max_loc
    if max_val < threshold:
        return None
    # calculator middle point
    middle_point = (top_left[0]+w/2, top_left[1]+h/2)
    result = dict(
        result=middle_point,
        rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]), (top_left[0] + w, top_left[1] + h)),
        confidence=max_val)
    return result

def picRead(pics):
    temp = []
    tempDict = dict()
    if isinstance(pics,list):
        for eachPic in pics:
            tempDict = dict()
            tempDict['pic'] = imreadCH(eachPic)
            tempDict['obj'] = resplit(r'[\\ /]', eachPic)[-1]
            temp.append(tempDict)
        return temp
    else:
        tempDict['pic'] = imreadCH(pics)
        tempDict['obj'] = resplit(r'[\\ /]', pics)[-1]
        return tempDict

def matchImg_roi(imgsrc, imgobj, roi, confidencevalue=0.8,targetSize=(1440, 810)):
    '返回roi中的位置'
    if isinstance(imgsrc,str):
        imsrc = imreadCH(imgsrc)
    else:
        imsrc = imgsrc

    if targetSize != (0,0):
        imsrc = resize(imsrc, targetSize)

    x0 = int(roi[0])
    x1 = int(roi[0] + roi[2])
    y0 = int(roi[1])
    y1 = int(roi[1] + roi[3])

    if x0 > imsrc.shape[1] or y0 > imsrc.shape[0]:
        return None
    if x1 > imsrc.shape[1]:
        x1 = imsrc.shape[1]
    if y1 > imsrc.shape[0]:
        y1 = imsrc.shape[0]

    imsrc = imsrc[y0:y1, x0:x1]
    return matchImg(imsrc, imgobj, confidencevalue, targetSize = (0, 0))

def matchMultiImg_roi(imgsrc, imgobj, roi, confidencevalue=0.8, targetSize=(1440, 810)):
    '返回真实位置'
    if isinstance(imgsrc,str):
        imsrc = imreadCH(imgsrc)
    else:
        imsrc = imgsrc

    if targetSize != (0,0):
        imsrc = resize(imsrc, targetSize)

    x0 = int(roi[0])
    x1 = int(roi[0] + roi[2])
    y0 = int(roi[1])
    y1 = int(roi[1] + roi[3])

    if x0 > imsrc.shape[1] or y0 > imsrc.shape[0]:
        return None
    if x1 > imsrc.shape[1]:
        x1 = imsrc.shape[1]
    if y1 > imsrc.shape[0]:
        y1 = imsrc.shape[0]

    imsrc = imsrc[y0:y1, x0:x1]
    ans = matchMultiImg(imsrc, imgobj, confidencevalue = confidencevalue, isResize = False)
    ansReal = None
    if ans != None:
        ans = ans[0]
        if ans != None:
            ansReal = []
            for eachPos in ans:
                ansReal.append([eachPos[0] + x0, eachPos[1] + y0])
    return ansReal

def matchImg(imgsrc,imgobj,confidencevalue=0.8,targetSize=(1440, 810)):  #imgsrc=原始图像，imgobj=待查找的图片
    '用于查找原始图片中的单一目标图片，如果原始图片中可找到多个目标图片，则随机返回一个匹配的结果，返回值为一个字典'
    try:
        if isinstance(imgsrc,str):
            imsrc = imreadCH(imgsrc)
        else:
            imsrc = imgsrc
    except RuntimeError:
        return None
    #imobj = imread(imgobj)
    if isinstance(imgobj,str):
        imobj = imreadCH(imgobj)
    elif isinstance(imgobj, dict):
        imobj = imgobj['pic']    #现在此情况传入的一定是字典
    else:
        imobj = imgobj

    if targetSize != (0,0):
        imsrc = resize(imsrc, targetSize)

    if isinstance(confidencevalue, list):
        for i in confidencevalue:
            if MODE == 'TEMPLATE':
                match_result = find_template(imsrc,imobj,i)
            else:
                match_result = find_sift(imsrc, imobj)
                if match_result != None:
                    match_result = {'result': match_result[0]}
            if match_result != None:
                break
    else:
        if MODE == 'TEMPLATE':
            match_result = find_template(imsrc,imobj,confidencevalue)
        else:
            match_result = find_sift(imsrc, imobj)
            if match_result != None:
                match_result = {'result': match_result[0]}
    #match_result = None
    if match_result != None:
        if isinstance(imgobj, str):
            match_result['obj'] = resplit(r'[\\ /]', imgobj)[-1]
        elif isinstance(imgobj, dict):
            match_result['obj'] = imgobj['obj']
        else:
            match_result['obj'] = 'numpy'

    return match_result


def matchMultiImg(imgsrc, imgobj, confidencevalue=0.8, targetSize = (1440, 810), maxReturn=-1, isResize = True, colorSpace = (0,0,0), debugMode = False):
    '用于查找原始图片中的多个目标图片，若不存在图片则返回None，否则返回一个目标图片坐标构成的元组；imgsrc为原始图片路径，imgobj为目标图片路径，confidencevalue为置信度，maxReturn在非负的情况下只会返回相应数值的坐标，为0则永远返回None]'
    maxReturn = int(maxReturn)
    if isinstance(imgsrc,str):
        try:
            imsrc = imreadCH(imgsrc)
        except RuntimeError:
            return None
    else:
        imsrc = imgsrc
    if isResize:
        imsrc = resize(imsrc, targetSize)
    if isinstance(imgobj,str):
        imobj = imreadCH(imgobj)
    elif isinstance(imgobj, dict):
        imobj = imgobj['pic']    #现在此情况传入的一定是字典
    else:
        imobj = imgobj
    matchRect = []
    matchPositionXY = []
    while True:
        match_result = find_template(imsrc,imobj,confidencevalue) 
        #match_result = None
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
    nowLevel = imreadCH(imgsrc)
    nowLevel = resize(nowLevel, (1440, 810))
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
