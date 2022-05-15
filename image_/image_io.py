import imp
from os import getcwd, remove, makedirs
from os import path as ospath

from cv2 import imdecode, imencode, cvtColor, COLOR_BGR2RGB
from PySide6.QtGui import QImage, QPixmap

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

def cvimg_qimage_trans(cvimg):

    height, width, depth = cvimg.shape
    cvimg = cvtColor(cvimg, COLOR_BGR2RGB)
    qimage = QImage(cvimg.data, width, height, width * depth, QImage.Format_RGB888)

    return qimage

def cvimg_qpixmap_trans(cvimg):
    return QPixmap(cvimg_qimage_trans(cvimg))

