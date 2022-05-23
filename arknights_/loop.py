from sys import path as spath
from os import getcwd

spath.append(getcwd())

from time import sleep

from user_res import R
from common2 import adb
from image_.match import match_pic, match_pics

#adb.ip = '127.0.0.1:7555' #测试时选定模拟器用

#res = [R.in_battle, R.finish_battle, R.start_a, R.start_b, R.sanity_lack]

def start_once(res):
    is_auto_on = True
    is_finish = False
    count_in_battle = 0
    while not is_finish:
        capture = adb.getScreen_std()
        for i in res:
            pos_ = match_pic(capture, i)
            if pos_[0] >= 0:
                match i['res_name']:
                    case name if 'start_a' in name:
                        count_in_battle = 0
                        if not is_auto_on:
                            pos_auto_switch = match_pic(capture, R.auto_switch)
                            adb.click(pos_auto_switch[0], pos_auto_switch[1])
                            is_auto_on = True
                    case name if 'start_b' in name:
                        count_in_battle = 0
                        is_auto_on = True if match_pic(capture, R.auto_on)[0] >= 0 else False
                        if not is_auto_on:
                            pos_btn_back = match_pic(capture, R.btn_back)
                            adb.click(pos_btn_back[0], pos_btn_back[1])
                            continue
                    case name if 'in_battle' in name:
                        count_in_battle += 1
                        sleep(1)
                        continue
                    case name if 'finish_battle' in name:
                        is_finish = True
                        break
                    case name if 'sanity_lack' in name:
                        return pos_ + [-1]
                    case _:
                        count_in_battle = 0
                adb.click(pos_[0], pos_[1])
        else:
            if count_in_battle > 0:
                adb.click(adb.screenX - 1, 1)
                adb.click(1280 - 1, 1)
    return pos_ + [1] #返回作战结束的坐标，用于返回开始界面




def start_loop():
    res = R.get_loop_res()
    while True:
        pos_ = start_once(res['all'])
        while match_pics(adb.getScreen_std(), res['finish_battle'])[0] > 0:
            adb.click(pos_[0], pos_[1])
        while match_pics(adb.getScreen_std(), res['sanity_lack'])[0] > 0:
            adb.click(pos_[0], pos_[1])
        if pos_[3] < 0:
            break

def main():
    start_loop()

if __name__ == '__main__':
    main()



















