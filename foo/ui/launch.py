from PyQt5.QtWidgets import QSplashScreen, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from os import getcwd

class Launch(QSplashScreen):
    def __init__(self):
        super(Launch, self).__init__(QPixmap(getcwd() + '/res/gui/launchWindow.png'))
        self.show()
