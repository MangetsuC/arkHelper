from ast import pattern
from os import getcwd
from random import choice
from re import template
from sys import path as spath
from time import perf_counter, sleep
from tracemalloc import start
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

spath.append(getcwd())

from common import logistic_rule, recruit_data, user_data
from common2 import adb
from cv2 import (CHAIN_APPROX_SIMPLE, COLOR_BGR2GRAY, COLOR_GRAY2BGRA,
                 COLOR_RGB2BGRA, COLOR_RGB2GRAY, FLOODFILL_FIXED_RANGE,
                 MORPH_RECT, RETR_EXTERNAL, RETR_TREE, THRESH_BINARY,
                 THRESH_BINARY_INV, TM_CCOEFF_NORMED, Canny, Mat, boundingRect,
                 connectedComponentsWithStats, contourArea, copyTo, cvtColor,
                 dilate, drawContours, erode, fillConvexPoly, findContours,
                 floodFill, getStructuringElement, imdecode, imshow,
                 matchTemplate, minMaxLoc, mixChannels, resize, waitKey)
from image_.color_detect import (Rectangle, binary_rgb, find_color_block,
                                 flood_fill)
from image_.image_io import load_res
from image_.match import match_pic
from numpy import (asarray, bitwise_and, bitwise_or, dtype, mat, ones, square,
                   uint8, zeros)
from ocr_.ocr import get_text_ocr, resize_text_img
from user_res import R


def getTemplatePic_CH(words:str, fontsize:int) -> dict:
    ttf = ImageFont.truetype("./fonts/SourceHanSansCN-Medium.otf", fontsize) #字体选用思源黑体
    wordsPic = Image.new('RGB', ttf.getsize(words))
    wordsDraw = ImageDraw.Draw(wordsPic)
    wordsDraw.text((0, 0), words, font=ttf, fill=(255,255,255)) #创建对应的模板
    return dict(pattern = cvtColor(asarray(wordsPic), COLOR_RGB2BGRA),
                    bgremove = False, res_name = words)

def check_op_exist(op_name:str, capture:Optional[Mat] = None) -> list:
    if capture == None:
        capture = adb.getScreen_std()
    template = getTemplatePic_CH(op_name, 21)
    ans = match_pic(capture, template)
    chosen_square = get_chosen_squares()
    for i in chosen_square:
        if i.check_inside(ans[0], ans[1]):
            ans[0] = -1
    return ans

def choose_ops(rule:list, vacancy_num:int, room_limit:Optional[list] = []) -> list:
    delete_line = []
    checked_line = []
    for i in range(len(rule)):
        if rule[i] in checked_line: #避免配置中出现重复内容
            continue
        checked_line.append(rule[i])

        limit = rule[i]['limit']
        ops = rule[i]['names']

        is_suit_limit = True
        for l in limit:
            if not l in room_limit:
                is_suit_limit = False
                break

        if is_suit_limit and len(ops) <= vacancy_num:
            is_ops_avaliable = True
            ops_pos = []
            for j in ops:
                ans = check_op_exist(j)
                ops_pos.append(ans)
                if ans[0] < 0:
                    is_ops_avaliable = False
                    break
            if is_ops_avaliable:
                for j in range(len(ops_pos)):
                    for _ in range(3):
                        adb.click(ops_pos[j][0], ops_pos[j][1])
                        #检查是否选中
                        ans = check_op_exist(ops[j])
                        if ans[0] < 0:
                            vacancy_num -= 1
                            break
                delete_line.append(i)
            else:
                continue
    while len(delete_line) != 0:
        rule.pop(delete_line.pop()) #删除已选择的干员
    
    return rule

def get_chosen_squares() -> list:
    capture = adb.getScreen_std()
    square = binary_rgb(capture, [-1, 1], [0, 255], [0, 255])
    flood_fill(square)

    temp, _ = findContours(square, RETR_TREE, CHAIN_APPROX_SIMPLE)
    contours = []
    for i in temp:
        area = contourArea(i)
        if area > 100*250 and area < adb.screenX * adb.screenY / 4:
            contours.append(i)

    ans = []
    for i in contours:
        x, y, w, h = boundingRect(i)
        ans.append(Rectangle(x, y, w, h))
    return ans


if __name__ == '__main__':
    t = perf_counter()
    #ans = match_pic(pic, target)
    #adb.connect()
    #ans = check_op_exist('伊芙利特')
    #print(ans)
    rule = logistic_rule.get_rule()['发电站']
    #print(len(rule))
    rule = choose_ops(rule, 1, [])
    #print(len(rule))
    
    #get_chosen_pos()
    #names = get_names_location()
    #print(names)
    print(f'cost:{perf_counter()-t}')


















