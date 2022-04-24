from cv2 import (COLOR_BGR2GRAY, MORPH_RECT, THRESH_BINARY, THRESH_BINARY_INV,
                 TM_CCOEFF_NORMED, Canny, connectedComponentsWithStats, copyTo,
                 cvtColor, dilate, erode, fillConvexPoly,
                 getStructuringElement, imdecode, imshow, matchTemplate,
                 minMaxLoc, resize, mixChannels)
from cv2 import split as cvsplit
from cv2 import threshold, waitKey
from numpy import array, bitwise_and, fromfile, zeros

class Color_Point:
    def __init__(self, r, g, b) -> None:
        self.r = r
        self.g = g
        self.b = b
    
    def __sub__(self, x):
        return (self.r - x.r)**2 + (self.g - x.g)**2 + (self.b - x.b)**2

    def __str__(self) -> str:
        return 'r:{} g:{} b:{}'.format(self.r, self.g, self.b)

def binary_rgb(img, rthres, gthres, bthres, is_single_channel = True):
    #imshow('img', img)
    #waitKey(0)
    if img.shape[2] == 4:
        b, g, r, _ = cvsplit(img)
    else:
        b, g, r = cvsplit(img)
    _, binaryb = threshold(b, bthres[0], 255, THRESH_BINARY)
    _, binaryb2 = threshold(b, bthres[1], 255, THRESH_BINARY_INV)

    _, binaryg = threshold(g, gthres[0], 255, THRESH_BINARY)
    _, binaryg2 = threshold(g, gthres[1], 255, THRESH_BINARY_INV)

    _, binaryr = threshold(r, rthres[0], 255, THRESH_BINARY)
    _, binaryr2 = threshold(r, rthres[1], 255, THRESH_BINARY_INV)


    binaryb = bitwise_and(binaryb, binaryb2)
    binaryr = bitwise_and(binaryr, binaryr2)
    binaryg = bitwise_and(binaryg, binaryg2)
    binary = bitwise_and(binaryb, binaryr)
    binary = bitwise_and(binary, binaryg)
    #imshow('binary', binary)
    #waitKey(0)
    if is_single_channel:
        return binary
    else:
        temp = zeros(shape = img.shape, dtype = 'uint8')
        mixChannels([binary], [temp], [0,0,0,1,0,2]) #转为多通道
        return temp

def find_color_block(img, thresholds, eroded_iter = 1, dilated_iter = 10):
    binary = binary_rgb(img, thresholds[0], thresholds[1], thresholds[2])
    kernel = getStructuringElement(MORPH_RECT,(3, 3))
    eroded = erode(binary, kernel, iterations = eroded_iter)        #腐蚀图像
    dilated = dilate(eroded, kernel, iterations = dilated_iter)      #膨胀图像
    #imshow('dilated', dilated)
    #waitKey(0)


    temp = list(connectedComponentsWithStats(dilated)[2])
    temp.sort(key = lambda x:(x[1], x[0]))
    ans = []
    for i in temp:
        if i[0] <= 5 and i[1] <= 5:
            pass
        else:
            ans.append(dict(x = int(i[0] + i[2]/2),
                            y = int(i[1] + i[3]/2),
                            width = i[2],
                            height = i[3],
                            border = dict(left = i[0],
                                          right = i[0] + i[2],
                                          top = i[1],
                                          bottom = i[1] + i[3])
                            )
                )
    
    return ans

def get_point_color(img, x, y) -> Color_Point:
    temp = img[y, x]
    return Color_Point(temp[2], temp[1], temp[0])

def check_point_color(img, point_color_dict:dict, tolerance_e = 1) -> bool:
    tolerance_e = tolerance_e ** 2
    ans = True
    for key in point_color_dict.keys():
        pos = key.split('*')
        if get_point_color(img, int(pos[0]), int(pos[1])) - point_color_dict[key] >= tolerance_e:
            ans = False
            break
    
    return ans
















