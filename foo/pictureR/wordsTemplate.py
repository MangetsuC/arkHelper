from PIL import Image, ImageDraw, ImageFont
from numpy import asarray
from cv2 import cvtColor, COLOR_RGB2BGR, imshow, waitKey
from os import getcwd

def getFontSize_name(resolution):
    x = resolution[0]
    if x <= 1024:
        return (16, (1024,576))
    elif x <= 1280:
        return (21, (1280,720))
    elif x <= 1440:
        return (23, (1440,810))
    elif x <= 1600:
        return (26, (1600,900))
    else:
        return (31, (1920,1080))

def getTemplatePic_CH(words, fontsize):
    #字号典型值 基建干员名称23 进驻总览房屋名称28(1440*810) 基建干员名称30 进驻总览房屋名称38(1920*1080)
    ttf = ImageFont.truetype(getcwd() + "/res/fonts/SourceHanSansCN-Regular.otf", fontsize) #字体选用思源黑体
    wordsPic = Image.new('RGB', ttf.getsize(words))
    wordsDraw = ImageDraw.Draw(wordsPic)
    wordsDraw.text((0, 0), words, font=ttf, fill=(255,255,255)) #创建对应的模板
    #temp = cvtColor(asarray(wordsPic), COLOR_RGB2BGR)
    #imshow('test', temp)
    #waitKey(0)
    return cvtColor(asarray(wordsPic), COLOR_RGB2BGR)

def getTemplatePic_NUM(num, fontsize):
    #字号典型值 进驻总览干员心情28
    num = str(num)
    ttf = ImageFont.truetype(getcwd() + "/res/fonts/Bender.otf", fontsize) #字体选用bender
    wordsPic = Image.new('RGB', ttf.getsize(num), color = (255, 255, 255))
    wordsDraw = ImageDraw.Draw(wordsPic)
    wordsDraw.text((0, 0), num, font=ttf, fill=(0,0,0)) #创建对应的模板
    return cvtColor(asarray(wordsPic), COLOR_RGB2BGR)