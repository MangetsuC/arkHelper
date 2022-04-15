from sys import path as spath
from os import getcwd

spath.append(getcwd())

from time import sleep

from user_res import R, load_temp_res, load_user_res

from PIL import Image, ImageDraw, ImageFont
from numpy import asarray
from cv2 import cvtColor, COLOR_RGB2BGR, imshow, waitKey, rectangle

from common2 import adb
from image_.match import match_pic
from image_.image_io import load_res, output_image
from image_.color_detect import find_color_block

adb.ip = '127.0.0.1:7555' #测试时选定模拟器用
adb.screenX = 1280
adb.screenY = 720


def get_terminal_btn():
    '找到终端界面上8个按钮的位置'
    capture = adb.getScreen_std()
    temp = find_color_block(capture, [[60,100],[60,100],[60,100]], dilated_iter=16)
    ans = []
    for i in temp:
        if abs(i['y'] - temp[-1]['y']) < temp[-1]['height']/4:
            ans.append([i['x'], i['y']])

    ans.sort(key = lambda x:x[0])
    ans = [[1, ans[0][1]]] + ans + [[adb.screenX - 1, ans[0][1]]]
    print(ans)

def getTemplatePic_CH(words, fontsize):
    #字号典型值 基建干员名称23 进驻总览房屋名称28(1440*810) 基建干员名称30 进驻总览房屋名称38(1920*1080)
    ttf = ImageFont.truetype('./Noto_Sans_SC/NotoSansSC-Medium.otf', fontsize) #字体选用思源黑体
    wordsPic = Image.new('RGB', ttf.getsize(words), color=(255, 255, 255))
    wordsDraw = ImageDraw.Draw(wordsPic)
    wordsDraw.text((0, 0), words, font=ttf, fill=(0,0,0)) #创建对应的模板
    #temp = cvtColor(asarray(wordsPic), COLOR_RGB2BGR)
    #imshow('test', temp)
    #waitKey(0)
    return cvtColor(asarray(wordsPic), COLOR_RGB2BGR)

def level_test():
    #capture = load_res('./test.png')
    capture = adb.getScreen_std()
    output_image('E:\\workSpace\\CodeRelease\\arknightHelper\\arkHelper\\nres\\测试.png', capture)
    #ans = match_pic(capture, load_temp_res(getTemplatePic_CH('7', 25), dict(bgremove = True, confidence = 0.6)))
    ans = match_pic(capture, R.test)
    if ans[0] > -1:
        print(ans)
        rectangle(capture, ans[2]['rectangle'][0], ans[2]['rectangle'][1], (0,255,0), 4)
        imshow('capture', capture)
        waitKey(0)








if __name__ == '__main__':
    #level_test()
    get_terminal_btn()
    pass

