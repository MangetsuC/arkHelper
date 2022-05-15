from sys import path as spath
from os import getcwd
from time import sleep
from random import choice
from tracemalloc import start
from turtle import distance

spath.append(getcwd())

from numpy import dtype, mat, ones, uint8
from cv2 import imshow, waitKey, COLOR_GRAY2BGRA, cvtColor
from user_res import R
from common import recruit_data, user_data
from common2 import adb
from image_.match import match_pic
from image_.color_detect import find_color_block
from ocr_.ocr import get_text_ocr, resize_text_img

#adb.ip = '127.0.0.1:7555' #测试时选定模拟器用

def locate_tags_block():
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[46,52],[46,52],[46,52]])
    temp = []
    lasty = -1
    for i in blocks:
        if i['y'] != lasty:
            temp.append([])
            temp[-1].append(i)
            lasty = i['y']
        else:
            temp[-1].append(i)
    ans = []
    for i in range(len(temp) - 1): #最后一次3 2排序即为标签
        if len(temp[i]) == 3 and len(temp[i+1]) == 2:
            ans = temp[i] + temp[i+1]
    #print(ans)
    return ans

def locate_time_block(tags_location):
    for i in range(5):
        capture = adb.getScreen_std()
        blocks = find_color_block(capture, [[46,52],[46,52],[46,52]], dilated_iter = 9)
        temp = []
        lasty = -1
        for i in blocks:
            if i['x'] < tags_location[0]['border']['left']:
                continue
            if i['y'] != lasty:
                temp.append([])
                temp[-1].append(i)
                lasty = i['y']
            else:
                temp[-1].append(i)
        ans = []
        for i in range(len(temp) - 3): #第一次2 3 2 2排序即为时间
            if len(temp[i]) == 2 and len(temp[i+1]) == 3 and len(temp[i+2]) == 2 and len(temp[i+3]) == 2:
                ans = temp[i] + temp[i+1] + temp[i+3]
                break
        if ans != []:
            break
    #print(ans)
    return ans

def check_tags_chosen(tags_location, chosen_nums):
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[48,50],[48,50],[48,50]])
    temp = []
    ans = []
    for i in blocks:
        if tags_location[0]['border']['top'] < i['y'] <tags_location[-1]['border']['bottom']:
            temp.append(i)
    for num in chosen_nums:
        for i in temp:
            if (i['x'] - tags_location[num]['x'])**2 + (i['y'] - tags_location[num]['y'])**2 < 4:
                ans.append(num)
                break
    return ans

def get_name(location):
    capture = adb.getScreen_std()
    ans = []
    for i in location:
        for j in range(3,8):
            temp = capture[i['border']['top']:i['border']['bottom'], i['border']['left']:i['border']['right']]
            tag_name = get_text_ocr(resize_text_img(temp, j))
            if tag_name != '':
                ans.append(tag_name)
                break
    return ans

def get_tags_to_chose(tags_on_screen, tags_location, rule = dict()):
    default_rule = dict(skip_config = dict(min_6 = False, min_5 = False, min_4 = False, max_2 = False, max_1 = False, other = False),
                        star_priority = ['min_6', 'min_5', 'min_4', 'refresh', 'other', 'max_1', 'max_2'],
                        unique_time = dict(max_2 = ['07', '30', '00'], max_1 = ['03', '50', '00']))
    default_rule.update(rule)
    ans = recruit_data.get_tags_ops(tags_on_screen)
    for i in default_rule['star_priority']:
        if i == 'refresh':
            resfresh_able = refresh(tags_location)
            if resfresh_able == 1:
                return [[-2], default_rule['unique_time'].get(i, ['09', '00', '00'])]
            continue
        if ans[i][0] != []:
            if default_rule['skip_config'][i]:
                break
            return [choice(ans[i][0]), default_rule['unique_time'].get(i, ['09', '00', '00'])]
    return [[-1], default_rule['unique_time'].get(i, ['09', '00', '00'])]
    
def chose_tags(tags_to_chose, tags_location):
    if tags_to_chose[0] < 0:
        return tags_to_chose[0]

    for i in range(5):
        unchosen = check_tags_chosen(tags_location, tags_to_chose)
        if unchosen == []:
            return 1
        else:
            for j in unchosen:
                adb.click(tags_location[j]['x'], tags_location[j]['y'])
    return -1

def refresh(tags_location):
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[-1,1],[151,153],[219,221]])
    refresh_btn = None
    for i in blocks:
        if tags_location[0]['border']['top'] < i['y'] <tags_location[-1]['border']['bottom']:
            refresh_btn = i
            break
    if refresh_btn != None:
        for i in range(3):
            adb.click(refresh_btn['x'], refresh_btn['y'])
        #capture = adb.getScreen_std() #点了三次，认为肯定点出来了，略过检测
        #blocks = find_color_block(capture, [[114,120],[14,20],[14,20]])
        confirm_btn = dict(x = tags_location[2]['x'], y = tags_location[4]['y']) #公招第六个格子的位置恰为确认位置
        for i in range(3):
            adb.click(confirm_btn['x'], confirm_btn['y'])
        return 1
    else:
        return -1

def locate_confirm_btn(tags_location):
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[-1,1],[151,153],[219,221]])
    confirm_btn = None
    for i in range(-1, -len(blocks)-1, -1):
        if blocks[i]['x'] > tags_location[2]['x'] and blocks[i]['y'] > tags_location[2]['y']:
            confirm_btn = blocks[i]
            break
    return confirm_btn

def locate_cancel_btn(confirm_btn):
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[46,52],[46,52],[46,52]])
    cancel_btn = None
    distance2 = float('inf')
    for i in blocks:
        if (i['x']-confirm_btn['x'])**2 + (i['y']-confirm_btn['y'])**2 < distance2:
            cancel_btn = i
            distance2 = (i['x']-confirm_btn['x'])**2 + (i['y']-confirm_btn['y'])**2
    return cancel_btn

def enter_recruit():
    while match_pic(adb.getScreen_std(), R.tips_icon)[0] < 0:
        capture = adb.getScreen_std()
        entrance_btn = match_pic(capture, R.recruit_entrance)
        if entrance_btn[0] > 0:
            adb.click(entrance_btn[0], entrance_btn[1])

def start_recruit(skip_btn = []):
    capture = adb.getScreen_std()
    for i in skip_btn: #将已被跳过的公招位置涂黑避免检测
        capture[i[2]['rectangle'][0][1]:i[2]['rectangle'][1][1], i[2]['rectangle'][0][0]:i[2]['rectangle'][1][0]] = (0, 0, 0, 1)

    start_btn = match_pic(capture, R.recruit_start)
    if start_btn[0] > 0:
        for i in range(5):
            adb.click(start_btn[0], start_btn[1])
            if match_pic(adb.getScreen_std(), R.recruit_start)[0] < 0:
                return [1,start_btn]
    return [-1,start_btn]

#adb.screenX = 1280
#adb.screenY = 720
def employ_recruit():
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[-1,10],[145,160],[210,225]])
    ans = []
    for i in blocks:
        if i['y'] > adb.screenY/3:
            ans.append(i)
    for i in ans:
        for j in range(5):
            adb.click(i['x'], i['y'])
            if match_pic(adb.getScreen_std(), R.tips_icon)[0] < 0:
                break
        while match_pic(adb.getScreen_std(), R.tips_icon)[0] < 0:
            #adb.click(adb.screenX - 10, 10)
            adb.click(1280 - 10, 10)

def confirm_single_recruit(recruit_rule:dict):
    time_to_chose = ['09', '00', '00']
    for i in range(5): #某一公招槽位选取标签
        tags_location = locate_tags_block()
        tags_name = get_name(tags_location)
        if len(tags_name) != 5:
            chose_result = -3 #错误：标签数目不足5
            break
        print(tags_name)
        tags_to_chose, time_to_chose = get_tags_to_chose(tags_name, tags_location, recruit_rule)
        chose_result = chose_tags(tags_to_chose, tags_location)
        if chose_result == -2: #-2代表刷新
            continue
        else:
            break
    if chose_result > 0: #-1代表跳过
        for i in range(50): #调整时间
            time_location = locate_time_block(tags_location)
            time_name = get_name(time_location[2:5])
            print(time_name)
            if time_to_chose[0] != time_name[0]:
                if abs(int(time_to_chose[0]) - int(time_name[0])) < 4:
                    adb.click(time_location[0]['x'], time_location[0]['y'])
                else:
                    adb.click(time_location[5]['x'], time_location[5]['y'])
            elif time_to_chose[1] != time_name[1]:
                if abs(int(time_to_chose[1]) - int(time_name[1])) < 4:
                    adb.click(time_location[1]['x'], time_location[1]['y'])
                else:
                    adb.click(time_location[6]['x'], time_location[6]['y'])
            else:
                break
    confirm_btn = locate_confirm_btn(tags_location)
    if chose_result > 0:
        adb.click(confirm_btn['x'], confirm_btn['y'])
    else:
        cancel_btn = locate_cancel_btn(confirm_btn)
        adb.click(cancel_btn['x'], cancel_btn['y'])
    return chose_result

def main():
    recruit_rule = user_data.get('recruit')
    enter_recruit()
    employ_recruit()
    skip_btn = []
    while True:
        temp = start_recruit(skip_btn)
        if temp[0] < 0: break

        chose_result = confirm_single_recruit(recruit_rule)
        if chose_result < 0:
            skip_btn.append(temp[1]) #记录被跳过的公招位置

if __name__ == '__main__':
    #print(get_tags_to_chose(['医疗干员', '术师干员','特种干员','支援','快速复活']))
    main()
    
    #input()
    #print(check_tags_chosen(tags_location, [2,4]))
    #time_location = locate_block('time')
    #time_name = get_name(time_location[0:3])
    #print(time_name)
    pass
