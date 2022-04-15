from os import getcwd, remove, makedirs
from os import path as ospath

from cv2 import imdecode, imencode

from numpy import fromfile
from sys import path as spath


def load_res(resPath):
    return imdecode(fromfile(resPath, dtype="uint8"),-1)

def output_image(resPath, img):
    if not ospath.exists(ospath.dirname(resPath)):
        makedirs(ospath.dirname(resPath))
    imencode('.png', img)[1].tofile(resPath)

def del_image(resPath):
    if ospath.exists(resPath):
        remove(resPath)




