from sys import path as spath
from os import getcwd

spath.append(getcwd())

from user_res import in_battle, finish_battle, start_a, start_b, auto_on, auto_switch, btn_back
from common2 import adb
from image_.match import match_pic

adb.ip = '127.0.0.1:7555'

res = [in_battle, finish_battle, start_a, start_b, auto_on, auto_switch]

def start_once():
    is_auto_on = True
    step_finish = 0
    while not (step_finish == 2):
        capture = adb.getScreen_std()
        for i in res:
            pos_ = match_pic(capture, i[0])
            if pos_[0] >= 0:
                match i[1]:
                    case 'start_a':
                        if step_finish == 1:
                            step_finish = 2
                            continue
                        if not is_auto_on:
                            pos_auto_switch = match_pic(capture, auto_switch[0])
                            adb.click(pos_auto_switch[0], pos_auto_switch[1])
                            is_auto_on = True
                    case 'start_b':
                        is_auto_on = True if match_pic(capture, auto_on[0])[0] >= 0 else False
                        if not is_auto_on:
                            pos_btn_back = match_pic(capture, btn_back[0])
                            adb.click(pos_btn_back[0], pos_btn_back[1])
                            continue
                    case 'in_battle':
                        continue
                    case 'finish_battle':
                        step_finish = 1 
                    case _:
                        pass
                adb.click(pos_[0], pos_[1])




def start_loop():
    pass


if __name__ == '__main__':
    start_once()



















