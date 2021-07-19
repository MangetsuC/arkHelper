from platform import platform
from winreg import OpenKey, CloseKey, QueryValueEx, HKEY_CURRENT_USER
from PyQt5.QtGui import QIcon
from os import getcwd
#FileNotFoundError

class Theme:
    def __init__(self, config, isShowSystem = False):
        self.themeColor = '#70bbe4'
        self.fontColor = '#ffffff'
        self.checkedFontColor = '#ffffff'
        self.borderColor = '#ffffff'
        self.fgColor = '#4d4d4d'
        self.bgColor = '#272626'
        self.pressedColor = '#606162'
        self.selectedIcon = QIcon(getcwd() + '/res/gui/selected.png')
        if isShowSystem:
            print(f'操作系统：{platform()}')
        if 'Windows-10' in platform():
            try:
                keyDwm = OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\DWM')
                keyPersonalize = OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize')

                try:
                    themeColor = QueryValueEx(keyDwm, 'ColorizationColor')[0]
                    themeColor = hex(themeColor)
                    self.themeColor = '#' + themeColor[4:]
                except:
                    self.themeColor = '#70bbe4'
                CloseKey(keyDwm)
                try:
                    systemColor = QueryValueEx(keyPersonalize, 'SystemUsesLightTheme')[0] #0为深色，1为浅色SystemUsesLightTheme
                except FileNotFoundError:
                    systemColor = QueryValueEx(keyPersonalize, 'AppsUseLightTheme')[0] #0为深色，1为浅色
                if systemColor:
                    #系统为浅色
                    self.fontColor = '#000000'
                    self.checkedFontColor = '#ffffff'
                    self.borderColor = '#949495'
                    self.fgColor = '#D1D1D5'
                    self.bgColor = '#BFBFC3'
                    self.pressedColor = '#D8D8D9'
                    self.selectedIcon = QIcon(getcwd() + '/res/gui/selectedLightMode.png')
                else:
                    #系统为深色
                    self.fontColor = '#ffffff'
                    self.checkedFontColor = '#ffffff'
                    self.borderColor = '#ffffff'
                    self.fgColor = '#4d4d4d'
                    self.bgColor = '#272626'
                    self.pressedColor = '#606162'
                    self.selectedIcon = QIcon(getcwd() + '/res/gui/selected.png')

                CloseKey(keyPersonalize)
            except Exception:
                pass
        #此处用配置文件的设置覆盖自动设置
        if config.get('theme', 'themecolor') != 'auto':
            self.themeColor = config.get('theme', 'themecolor')
        if config.get('theme', 'fontcolor') != 'auto':
            self.fontColor = config.get('theme', 'fontcolor')
        if config.get('theme', 'checkedfontcolor') != 'auto':
            self.checkedFontColor = config.get('theme', 'checkedfontcolor')
        if config.get('theme', 'bordercolor') != 'auto':
            self.borderColor = config.get('theme', 'bordercolor')
        if config.get('theme', 'fgcolor') != 'auto':
            self.fgColor = config.get('theme', 'fgcolor')
        if config.get('theme', 'bgcolor') != 'auto':
            self.bgColor = config.get('theme', 'bgcolor')
        if config.get('theme', 'pressedcolor') != 'auto':
            self.pressedColor = config.get('theme', 'pressedcolor')

        selectedColor = config.get('theme', 'selectedcolor')
        if selectedColor == 'dark':
            #设置勾为深色，实际上用于浅色模式
            self.selectedIcon = QIcon(getcwd() + '/res/gui/selectedLightMode.png')
        elif selectedColor == 'light':
            self.selectedIcon = QIcon(getcwd() + '/res/gui/selected.png')

    def getThemeColor(self):
        return self.themeColor

    def getFontColor(self):
        return self.fontColor

    def getCheckedFontColor(self):
        return self.checkedFontColor
    
    def getBorderColor(self):
        return self.borderColor

    def getFgColor(self):
        return self.fgColor

    def getBgColor(self):
        return self.bgColor

    def getPressedColor(self):
        return self.pressedColor

    def getSelectedIcon(self):
        return self.selectedIcon