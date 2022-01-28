from os import getcwd, listdir, path, remove
from re import split as resplit

from cv2 import (COLOR_BGR2GRAY, TM_CCOEFF_NORMED, Canny, copyTo, cvtColor,
                 fillConvexPoly, imdecode, imshow, matchTemplate, minMaxLoc, resize, imshow, waitKey)
from cv2 import split as cvsplit
from cv2 import SIFT_create, BFMatcher
from numpy import array, fromfile, zeros, ndarray, sqrt, mat, power, random, shape, nonzero, mean, inf, where
from sys import path as spath

spath.append(getcwd())
from foo.pictureR.colorDetect import binary_rgb

def load_res(resPath):
    return imdecode(fromfile(resPath, dtype="uint8"),-1)


def find_template(im_source, im_search, threshold=0.5, rgb=False, bgremove=True):
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
        '''imshow('s_gray', s_gray)
        imshow('i_gray', i_gray)
        waitKey(0)'''

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

def match_pic(source, target:dict):
    target_pattern = target.get('pattern', None)
    bgremove = target.get('bgremove', True)
    rgb = target.get('rgb', False)
    binary = target.get('thresholds', [])

    if binary != []:
        source = binary_rgb(source, binary[0], binary[1], binary[2], is_single_channel = False)
    temp = find_template(source, target_pattern, 0.8, rgb, bgremove)
    if temp == None:
        ans = [-1, -1]
    else:
        ans = [int(temp['result'][0]), int(temp['result'][1])]
    return ans

if __name__ == '__main__':
    from user_res import in_battle, finish_battle, start_a, sanity_lack
    picname = '0'
    temp = match_pic(load_res(f'C:\\Users\\deman\\Documents\\MuMu共享文件夹\\{picname}.png'), 
                        sanity_lack)
    print(temp)
    pass

