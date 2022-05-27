from subprocess import Popen, PIPE
from cv2 import imdecode, imencode
from base64 import b64encode

from os import getcwd
from sys import path

app_path = getcwd()

path.append(app_path)
from numpy import dtype, ones, uint8
from cv2 import imshow, waitKey, COLOR_GRAY2BGRA, cvtColor
from image_ import image_io

def get_text_ocr(image):
    image = imencode('.png', image)[1].tobytes()
    image_b64 = b64encode(image).decode('UTF-8')
    p = Popen('Windows.Media.Ocr.Cli.exe -b {}'.format(image_b64[0]), shell = True, stdin=PIPE, stdout = PIPE, stderr = PIPE, bufsize = -1, cwd = app_path+'\\bin\\Windows_Media_Ocr')
    p.stdin.write(bytes('{}\n'.format(image_b64[1:]), 'UTF-8'))
    p.stdin.write(b'\n') #base64输入结束
    cmdReturn = p.communicate()

    try:
        strout = cmdReturn[0].decode('gbk').replace('\r\n', '\n')
    except UnicodeDecodeError:
        strout = cmdReturn[0].decode('UTF-8').replace('\r\n', '\n')
    return strout.strip()

def resize_text_img(text_img, enlarge_rate):
    if enlarge_rate < 2:
        return text_img
    base_size = max(text_img.shape[1], text_img.shape[0])
    bg = ones((base_size*enlarge_rate, base_size*enlarge_rate), dtype = uint8)
    bg = cvtColor(bg, COLOR_GRAY2BGRA)
    bg[:,:,0] = 255
    bg[:,:,1] = 255
    bg[:,:,2] = 255
    bg[:,:,3] = 255
    y_cover = [int(text_img.shape[0]/2), int(text_img.shape[0]/2)]
    x_cover = [int(text_img.shape[1]/2), int(text_img.shape[1]/2)]
    if int(text_img.shape[0]/2)*2 != text_img.shape[0]:
        y_cover[1] = y_cover[1] + 1
    if int(text_img.shape[1]/2)*2 != text_img.shape[1]:
        x_cover[1] = x_cover[1] + 1  
    bg[int(bg.shape[0]/2)-y_cover[0]:int(bg.shape[0]/2)+y_cover[1],int(bg.shape[1]/2)-x_cover[0]:int(bg.shape[1]/2)+x_cover[1]] = text_img
    return bg


if __name__ == '__main__':
    pass



