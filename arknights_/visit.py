from sys import path as spath
from os import getcwd
from time import sleep

spath.append(getcwd())

from user_res import R
from common2 import adb
from image_.match import match_pic
from image_.color_detect import find_color_block
from ocr_.ocr import get_text_ocr

#adb.ip = '127.0.0.1:7555' #测试时选定模拟器用

def find_tab_chosen():
    capture = adb.getScreen_std()
    ans = find_color_block(capture, [[205,245],[205,245],[205,245]], eroded_iter = 5, dilated_iter = 10)
    ans.sort(key = lambda x:x['x'])
    tab_chosen = ans[0]

    return tab_chosen

def get_btn_pos(tab_chosen):
    btn_friends_pos = dict(x = tab_chosen['x'], 
                           y = int(tab_chosen['border']['bottom'] + tab_chosen['height']/2))
    return btn_friends_pos

def visit():
    '进入他人基建'
    capture = adb.getScreen_std()
    pos = match_pic(capture, R.visit)
    text_on_screen = ''
    while (not '会客室' in text_on_screen) or (pos[0] > -1):
        adb.click(pos[0], pos[1])
        capture = adb.getScreen_std()
        text_on_screen = get_text_ocr(capture)
        pos = match_pic(capture, R.visit)

def visit_next():
    capture = adb.getScreen_std()
    btn_continue = find_color_block(capture, [[205,215],[85,95],[5,15]])
    is_need_continue = (btn_continue != [])
    if is_need_continue:
        btn_continue.sort(key = lambda x:[x['x'], x['y']])
        btn_continue = btn_continue[-1]
        adb.click(btn_continue['x'], btn_continue['y'])
        return True
    else:
        capture = adb.getScreen_std()
        is_loading = (find_color_block(capture, [[250,255],[100,105],[0,5]]) == [])
    if is_loading:
        return True
    else:
        return False

def main():
    tab_chosen = find_tab_chosen()
    target_btn = get_btn_pos(tab_chosen)
    while not (find_tab_chosen()['border']['top'] < target_btn['y'] < find_tab_chosen()['border']['bottom']):
        adb.click(target_btn['x'], target_btn['y'])
    visit()
    while visit_next(): pass

if __name__ == '__main__':
    main()


















