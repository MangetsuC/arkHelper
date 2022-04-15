from doctest import FAIL_FAST
from sys import path as spath
from os import getcwd
from time import sleep

from pip import main

spath.append(getcwd())

from user_res import R
from common2 import adb
from image_.match import match_pic
from image_.color_detect import find_color_block

adb.ip = '127.0.0.1:7555'

def goto_mainpage():
    capture = adb.getScreen_std()
    task_pos = match_pic(capture, R.task)
    if task_pos[0] < 0:
        btn_home_pos = match_pic(capture, R.btn_home)
        if btn_home_pos[0] > -1:
            adb.click(btn_home_pos[0], btn_home_pos[1])

            capture = adb.getScreen_std()
            mainpage_pos = match_pic(capture, R.mainpage)
            if mainpage_pos[0] > -1:
                adb.click(mainpage_pos[0], mainpage_pos[1])

        while True:
            capture = adb.getScreen_std()
            task_pos = match_pic(capture, R.task)
            if task_pos[0] >-1:
                break

def check_exit_mainpage():
    for i in range(10):
        if match_pic(adb.getScreen_std(), R.btn_back)[0] > -1:
            return True
    return False

def enter_common(pattern):
    while True:
        capture = adb.getScreen_std()
        task_pos = match_pic(capture, pattern)
        if task_pos[0] > -1:
            adb.click(task_pos[0], task_pos[1])
        if check_exit_mainpage():
            break

def enter_task():
    enter_common(R.task)

def enter_friends():
    enter_common(R.friends)


if __name__ == '__main__':
    enter_friends()
        










