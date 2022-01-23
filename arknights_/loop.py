from sys import path as spath
from os import getcwd

spath.append(getcwd())

from time import sleep

from user_res import in_battle, finish_battle, start_a, start_b, auto_on, auto_switch, btn_back
from common2 import adb
from image_.match import match_pic

adb.ip = '127.0.0.1:7555'

res = [in_battle, finish_battle, start_a, start_b]

def start_once():
    is_auto_on = True
    is_finish = False
    count_in_battle = 0
    while not is_finish:
        capture = adb.getScreen_std()
        for i in res:
            pos_ = match_pic(capture, i[0], i[2])
            if pos_[0] >= 0:
                match i[1]:
                    case 'start_a':
                        count_in_battle = 0
                        if not is_auto_on:
                            pos_auto_switch = match_pic(capture, auto_switch[0])
                            adb.click(pos_auto_switch[0], pos_auto_switch[1])
                            is_auto_on = True
                    case 'start_b':
                        count_in_battle = 0
                        is_auto_on = True if match_pic(capture, auto_on[0])[0] >= 0 else False
                        if not is_auto_on:
                            pos_btn_back = match_pic(capture, btn_back[0])
                            adb.click(pos_btn_back[0], pos_btn_back[1])
                            continue
                    case 'in_battle':
                        count_in_battle += 1
                        sleep(1)
                        continue
                    case 'finish_battle':
                        is_finish = True
                        break
                    case _:
                        count_in_battle = 0
                adb.click(pos_[0], pos_[1])
        else:
            if count_in_battle > 0:
                adb.click(500, 50)





def start_loop():
    pass


if __name__ == '__main__':
    start_once()



















