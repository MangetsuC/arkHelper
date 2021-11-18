from cv2 import (COLOR_BGR2GRAY, MORPH_RECT, THRESH_BINARY, THRESH_BINARY_INV,
                 TM_CCOEFF_NORMED, Canny, connectedComponentsWithStats, copyTo,
                 cvtColor, dilate, erode, fillConvexPoly,
                 getStructuringElement, imdecode, imshow, matchTemplate,
                 minMaxLoc, resize)
from cv2 import split as cvsplit
from cv2 import threshold, waitKey
from numpy import array, bitwise_and, fromfile, zeros


def binary_rgb(img, rthres, gthres, bthres):
    b, g, r, _ = cvsplit(img)
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

    return binary

def findColorBlock(img, thresholds):
    binary = binary_rgb(img, thresholds[0], thresholds[1], thresholds[2])
    kernel = getStructuringElement(MORPH_RECT,(3, 3))
    eroded = erode(binary,kernel)        #腐蚀图像
    dilated = dilate(eroded,kernel, iterations = 10)      #膨胀图像


    ans = list(connectedComponentsWithStats(dilated)[2])
    ans.sort(key = lambda x:x[-1])
    if ans[0][0] <= 5 and ans[0][1] <= 5:
        return None
    else:
        ans = [int(ans[0][0] + ans[0][2]/2), int(ans[0][1] + ans[0][3]/2)]
        return ans
















