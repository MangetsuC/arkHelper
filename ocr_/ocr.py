from subprocess import Popen, PIPE
from cv2 import imdecode, imencode
from base64 import b64encode

from os import getcwd
from sys import path

app_path = getcwd()

path.append(app_path)
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


if __name__ == '__main__':
    pass



