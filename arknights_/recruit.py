from sys import path as spath
from os import getcwd
from time import sleep

spath.append(getcwd())

from numpy import dtype, ones, uint8
from cv2 import imshow, waitKey, COLOR_GRAY2BGRA, cvtColor
from user_res import R
from common2 import adb
from image_.match import match_pic
from image_.color_detect import find_color_block
from ocr_.ocr import get_text_ocr

adb.ip = '127.0.0.1:7555' #测试时选定模拟器用

def locate_block(target):
    capture = adb.getScreen_std()
    blocks = find_color_block(capture, [[48,50],[48,50],[48,50]])
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
            if target == 'time':
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

def resize_tag_block(tag_img, enlarge_rate):
    bg = ones((tag_img.shape[1]*enlarge_rate, tag_img.shape[1]*enlarge_rate), dtype = uint8)
    bg = cvtColor(bg, COLOR_GRAY2BGRA)
    bg[:,:,0] = 255
    bg[:,:,1] = 255
    bg[:,:,2] = 255
    bg[:,:,3] = 255
    y_cover = [int(tag_img.shape[0]/2), int(tag_img.shape[0]/2)]
    x_cover = [int(tag_img.shape[1]/2), int(tag_img.shape[1]/2)]
    if int(tag_img.shape[0]/2)*2 != tag_img.shape[0]:
        y_cover[1] = y_cover[1] + 1
    if int(tag_img.shape[1]/2)*2 != tag_img.shape[1]:
        x_cover[1] = x_cover[1] + 1  
    bg[int(bg.shape[0]/2)-y_cover[0]:int(bg.shape[0]/2)+y_cover[1],int(bg.shape[1]/2)-x_cover[0]:int(bg.shape[1]/2)+x_cover[1]] = tag_img
    return bg

def get_name(location):
    capture = adb.getScreen_std()
    ans = []
    for i in location:
        for j in range(3,8):
            temp = capture[i['border']['top']:i['border']['bottom'], i['border']['left']:i['border']['right']]
            tag_name = get_text_ocr(resize_tag_block(temp, j))
            if tag_name != '':
                ans.append(tag_name)
                break
    return ans




if __name__ == '__main__':
    #tags_location = locate_block('tags')
    #tags_name = get_name(tags_location)
    #print(tags_name)
    #input()
    #print(check_tags_chosen(tags_location, [2,4]))
    time_location = locate_block('time')
    time_name = get_name(time_location[0:3])
    print(time_name)
    pass
