from sys import path as spath
from time import sleep, time
from os import getcwd, path, getlogin

spath.append(getcwd())

from image_.match import load_res

def load_user_res(res_name):
    if (path.exists(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{res_name}.png')):
        return [load_res(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{res_name}.png'), res_name]
    else:
        return [load_res(f'./nres/{res_name}.png'), res_name]

btn_back = load_user_res('btn_back')

start_a = load_user_res('start_a')
start_b = load_user_res('start_b')
auto_on = load_user_res('auto_on')
auto_switch = load_user_res('auto_switch')
finish_battle = load_user_res('finish_battle')
in_battle = load_user_res('in_battle')














