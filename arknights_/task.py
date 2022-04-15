from sys import path as spath
from os import getcwd
from time import sleep

spath.append(getcwd())

from user_res import R
from common2 import adb
from image_.match import match_pic
from image_.color_detect import find_color_block

adb.ip = '127.0.0.1:7555' #测试时选定模拟器用
adb.screenX = 1280
adb.screenY = 720

def find_column_chosen():
    capture = adb.getScreen_std()
    ans = find_color_block(capture, [[45,50],[45,50],[45,50]])
    column_pre3 = ans[0:3]
    column_pre3.sort(key = lambda x:x['x'])
    column_chosen = column_pre3[-1]

    return column_chosen


def get_btn_pos(column_chosen):
    task_pos = dict(
                    daliy = [],
                    weekly = [],
    )

    width = adb.screenX - column_chosen['border']['left']
    column_num = int(width/column_chosen['width'] + 0.5)
    match(column_num):
        #列表内容为[坐标x, 坐标y, [左边界, 右边界]]
        case 2:
            task_pos['daily'] = [column_chosen['x'], column_chosen['y'], 
                                [column_chosen['border']['left'], column_chosen['border']['right']]]
            task_pos['weekly'] = [column_chosen['border']['left'] + int(column_chosen['width']*(3/2)), 
                                  column_chosen['y'],
                                 [column_chosen['border']['right'],
                                  column_chosen['border']['right'] + column_chosen['width']]]
        case 3:
            task_pos['daily'] = [column_chosen['x'], column_chosen['y'],
                                [column_chosen['border']['left'], column_chosen['border']['right']]]
            task_pos['weekly'] = [column_chosen['border']['left'] + int(column_chosen['width']*(3/2)), 
                                  column_chosen['y'],
                                 [column_chosen['border']['right'],
                                  column_chosen['border']['right'] + column_chosen['width']]]
        case 4:
            task_pos['daily'] = [column_chosen['border']['left'] + int(column_chosen['width']*(3/2)), 
                                  column_chosen['y'],
                                  [column_chosen['border']['right'],
                                  column_chosen['border']['right'] + column_chosen['width']]]
            task_pos['weekly'] = [column_chosen['border']['left'] + int(column_chosen['width']*(5/2)), 
                                  column_chosen['y'],
                                  [column_chosen['border']['right'] + column_chosen['width'],
                                  column_chosen['border']['right'] + column_chosen['width']*2]]
    
    return task_pos

def column_switch(task_pos, target):
    while True:
        adb.click(task_pos[target][0], task_pos[target][1])
        sleep(0.2)
        column_chosen = find_column_chosen()
        if task_pos[target][2][0] < column_chosen['x'] < task_pos[target][2][1]:
            break

def submit_task(column_chosen):
    border_top = column_chosen['border']['bottom']
    capture = adb.getScreen_std()
    
    temp = find_color_block(capture, [[-1,5],[150,155],[215,225]])
    ans = []
    for i in temp:
        if i['border']['top'] > border_top and not (abs(i['width'] - i['height']) < i['height']/8):
            ans.append(i)

    ans.sort(key = lambda x:x['y'])
    if ans == []:
        return 
    ans = ans[0]
    adb.click(ans['x'], ans['y'])
    while True:
        capture = adb.getScreen_std()
        temp = find_color_block(capture, [[210,220],[210,220],[210,220]])
        temp.sort(key = lambda x:(x['x'], x['y']))
        if temp != []:
            temp = temp[0]
            if temp['x'] < column_chosen['border']['left'] and temp['y'] < column_chosen['border']['bottom']:
                return 
        adb.click(ans['x'], ans['y'])


if __name__ == '__main__':
    column_chosen = find_column_chosen()
    task_pos = get_btn_pos(column_chosen)
    
    column_switch(task_pos, 'daily')
    submit_task(column_chosen)

    column_switch(task_pos, 'weekly')
    submit_task(column_chosen)
    
    
    










