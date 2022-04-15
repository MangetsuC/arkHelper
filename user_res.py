from cv2 import mixChannels, imshow, threshold, waitKey, bitwise_and
from sys import path as spath
from time import sleep, time
from os import getcwd, path, getlogin
from numpy import zeros, uint8

spath.append(getcwd())

from image_.match import load_res
from foo.pictureR.colorDetect import binary_rgb
from common import res_config

def load_temp_res(res, extra_option = dict()):
    options = dict(
        bgremove = True, #边缘提取
        thresholds = []  #二值化
    )
    options.update(extra_option)

    res = dict(
            pattern = res,
            res_name = 'temp'
        )
    
    return {**res, **options}


def load_user_res(res_name, extra_option = dict()):
    options = dict(
        bgremove = True, #边缘提取
        thresholds = []  #二值化
    )
    options.update(extra_option)

    if (path.exists(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{res_name}.png')):
        res = dict(
            pattern = load_res(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{res_name}.png'),
            res_name = res_name
        )
    else:
        res = dict(
            pattern = load_res(f'./nres/{res_name}.png'),
            res_name = res_name
        )
    
    return {**res, **options}

def pattern_pre_treatment(pattern, extra_option = dict()):
    options = dict(
        thresholds = []  #二值化
    )
    options.update(extra_option)

    thresholds = options.get('thresholds', [])
    if thresholds != []:
        pattern = binary_rgb(pattern, thresholds[0], thresholds[1], thresholds[2], 
                                        is_single_channel = False)
    return pattern

class RES:
    '用户资源'
    def __init__(self):
        self.init()

    def init(self):
        #self.test = load_user_res('test') #指代测试的特定图片

        for i in res_config.get_res_list():
            self.__setattr__(i, load_user_res(i, res_config.get_res_config(i, 'common')))
            self.__getattribute__(i)['pattern'] = pattern_pre_treatment(self.__getattribute__(i)['pattern'], 
                                                                        res_config.get_res_config(i, 'self'))

R = RES()












