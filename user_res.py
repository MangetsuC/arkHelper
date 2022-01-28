from cv2 import mixChannels, imshow, threshold, waitKey, bitwise_and
from sys import path as spath
from time import sleep, time
from os import getcwd, path, getlogin
from numpy import zeros, uint8

spath.append(getcwd())

from image_.match import load_res
from foo.pictureR.colorDetect import binary_rgb

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

btn_back = load_user_res('btn_back')

start_a = load_user_res('start_a', dict(bgremove = False))
start_b = load_user_res('start_b')
auto_on = load_user_res('auto_on')
auto_switch = load_user_res('auto_switch')
finish_battle = load_user_res('finish_battle')
in_battle = load_user_res('in_battle')
sanity_lack = load_user_res('sanity_lack', dict(thresholds = [(254, 255), (254, 255), (254, 255)],
                                                bgremove = False))
sanity_lack['pattern'] = binary_rgb(sanity_lack['pattern'], (254, 255), (254, 255), (254, 255), 
                                is_single_channel = False) #提取sanity_lack图样中的白色部分














