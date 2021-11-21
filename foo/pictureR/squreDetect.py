from cv2 import (CHAIN_APPROX_SIMPLE, COLOR_BGR2GRAY, RETR_EXTERNAL, Canny,
                 GaussianBlur, approxPolyDP, arcLength, contourArea, cvtColor,
                 findContours, isContourConvex, moments, blur, HoughCircles, HOUGH_GRADIENT)
from numpy import dot
from numpy import max as npmax
from numpy import sqrt as npsqrt



def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( dot(d1, d2) / npsqrt( dot(d1, d1)*dot(d2, d2) ) )

def find_squares(img):
    squares = []
    img = GaussianBlur(img, (3, 3), 0)   
    gray = cvtColor(img, COLOR_BGR2GRAY)
    bin = Canny(gray, 30, 100, apertureSize=3)    
    contours, _hierarchy = findContours(bin, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
    #print("轮廓数量：%d" % len(contours))
    index = 0
    # 轮廓遍历
    for cnt in contours:
        cnt_len = arcLength(cnt, True) #计算轮廓周长
        cnt = approxPolyDP(cnt, 0.02*cnt_len, True) #多边形逼近
        area = contourArea(cnt) #面积
        # 条件判断逼近边的数量是否为4，轮廓面积是否大于1000，检测轮廓是否为凸的
        if len(cnt) == 4 and area > 1000 and isContourConvex(cnt):
            M = moments(cnt) #计算轮廓的矩
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])#轮廓重心
            
            cnt = cnt.reshape(-1, 2)
            max_cos = npmax([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in range(4)])
            # 只检测矩形（cos90° = 0）
            if max_cos < 0.1:
                index = index + 1
                squares.append([[cx, cy], area, cnt])
    
    squares.sort(key = lambda x:x[1], reverse = True)
    return squares

def find_circles(img):
    result = blur(img, (5,5))
    gray=cvtColor(result,COLOR_BGR2GRAY)

    #霍夫变换圆检测
    circles= HoughCircles(gray,HOUGH_GRADIENT,1,50,param1=80,param2=30,minRadius=int(img.shape[0]*15/864),maxRadius=int(img.shape[0]*30/864))
    if not circles is None:
        return list(circles[0])
    else:
        return []


