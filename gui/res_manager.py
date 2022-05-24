import sys
from os import getcwd, getlogin, path, system
from ast import literal_eval

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QIcon, QTextCursor, QPixmap
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
                               QPushButton, QTextBrowser, QVBoxLayout, QWidget, QScrollArea, QLabel, QTextEdit)

sys.path.append(getcwd())
from common import res_config, app_ico, app
from common2 import adb
from image_.image_io import del_image, output_image
from foo.ui.messageBox import AMessageBox
from user_res import R

#adb.ip = '127.0.0.1:7555' #测试时选定模拟器用


class Res_manager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('资源管理器')
        self.setWindowIcon(app_ico)

        self.res_selected = 'start_a'


        self.init_ui()


        #self.show()

    def init_ui(self):
        self.mainLayout = QVBoxLayout(self)
        self.topLayout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QGridLayout()

        #左侧资源列表加载
        self.scroll = QScrollArea()
        self.scroll.setMinimumHeight(100)
        self.scroll.setFixedWidth(200)
        self.btn_widget = QWidget()
        self.btn_widget.setFixedWidth(180)

        self.btns = []
        
        self.btn_add_new_res = QPushButton('新增素材')
        self.btn_add_new_res.setMinimumHeight(40)
        self.btn_add_new_res.setMinimumWidth(160)
        self.btn_add_new_res.clicked.connect(self.add_user_res)
        self.leftLayout.addWidget(self.btn_add_new_res)

        self.add_left_res_btn()
        self.scroll.setWidget(self.btn_widget)
        #左侧资源列表加载完成

        self.lable_example = QLabel('示例')
        self.label_user_res = QLabel('您的配置')
        self.pic_example = QLabel()
        self.tempPic_example = QPixmap()

        self.pic_user_res = QLabel()
        self.tempPic_user_res = QPixmap()

        self.label_advanced = QLabel('高级设置(请查阅wiki后再修改)')
        self.label_ad_op_common = QLabel('common')
        self.label_ad_op_self = QLabel('self')

        self.advanced_option_editor_common = QTextEdit()
        self.advanced_option_editor_common.setMaximumHeight(80)
        self.advanced_option_editor_self = QTextEdit()
        self.advanced_option_editor_self.setMaximumHeight(80)

        self.refresh_right()

        self.btn_del = QPushButton('删除')
        self.btn_del.clicked.connect(self.del_user_res)
        self.btn_get = QPushButton('截取')
        self.btn_get.clicked.connect(self.get_user_res)

        self.btn_apply = QPushButton('应用')
        self.btn_apply.clicked.connect(self.apply_advanced_options)
        self.btn_discard = QPushButton('重置')
        self.btn_discard.clicked.connect(self.discard_advanced_options)

        self.rightLayout.addWidget(self.lable_example, 0, 0, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.label_user_res, 0, 1, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.pic_example, 1, 0, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.pic_user_res, 1, 1, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.btn_del, 2, 0, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.btn_get, 2, 1, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.label_advanced, 3, 0, 1, 2, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.label_ad_op_common, 4, 0, 1, 2, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.advanced_option_editor_common, 5, 0, 1, 2, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.label_ad_op_self, 6, 0, 1, 2, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.advanced_option_editor_self, 7, 0, 1, 2, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.btn_apply, 8, 0, alignment = Qt.AlignCenter)
        self.rightLayout.addWidget(self.btn_discard, 8, 1, alignment = Qt.AlignCenter)

        self.label_readme = QLabel(f'{self.res_selected}-{res_config.get_res_readme(self.res_selected)}')

        self.topLayout.addWidget(self.scroll)
        self.topLayout.addLayout(self.rightLayout)
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(self.label_readme, alignment = Qt.AlignCenter)

    def add_left_res_btn(self):
        #删除原有的所有按钮
        item_list = list(range(1, self.leftLayout.count()))
        item_list.reverse()

        for i in item_list: #从布局中移除
            item = self.leftLayout.itemAt(i)
            self.leftLayout.removeItem(item)

        while self.btns != []: #释放内存
            temp = self.btns.pop()
            temp.deleteLater()
            del temp

        #生成新按钮
        for i in res_config.get_res_list():
            if not path.exists(f'./nres/{i}.png'): #判断是否为用户自添加素材
                i = i+'*' #自添加素材在按钮文字上后缀*号作为提醒
            temp = QPushButton(text=i)
            temp.clicked.connect(self.change_res_name)
            temp.setMinimumHeight(40)
            temp.setMinimumWidth(160)
            self.leftLayout.addWidget(temp, alignment = Qt.AlignCenter)
            self.btns.append(temp)

        self.btn_widget.setLayout(self.leftLayout)
        self.leftLayout.setSpacing(10)
        self.btn_widget.setFixedHeight(50*len(self.btns)+1)

    def change_res_name(self):
        self.res_selected = self.sender().text()
        self.res_selected = self.res_selected.strip('*') #*号代表为用户自添加素材，但只在GUI界面上作提醒，此处删除
        self.label_readme.setText(f'{self.res_selected}-{res_config.get_res_readme(self.res_selected)}')
        self.refresh_right()

    def add_user_res(self):
        res_name = AMessageBox.input(self, '新建素材','请输入素材名称:')
        
        if res_name[1]: #if True
            res_name = res_name[0]
        else:
            return 

        temp_ress = res_config.get('ress')
        if res_name in temp_ress or '*' in res_name: #重复名称或名称中有*号则直接忽略
            return 

        temp_ress.append(res_name)
        res_config.change('ress', temp_ress)
        self.add_left_res_btn()
        #R.init() #刚新增的素材没有实际设定，故可以不刷新R

    def del_user_res(self):
        ans = False
        if path.exists(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png'):
            ans = AMessageBox.question(self, '您确定吗', '已存在自定资源，确定要删除吗？')
            if ans:
                del_image(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png')
                self.refresh_right()

        if not path.exists(f'./nres/{self.res_selected}.png'): #用于判断是否为用户自添加资源
            ans = AMessageBox.question(self, '您确定吗', f'确定删除自添加资源{self.res_selected}吗？')
            if ans:
                del_image(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png')
                temp_ress = res_config.get('ress')
                del temp_ress[temp_ress.index(self.res_selected)]
                res_config.change('ress', temp_ress)

                #重新生成左侧列表，其余界面恢复默认(start_a)
                self.add_left_res_btn()
                self.res_selected = 'start_a'
                self.label_readme.setText(f'{self.res_selected}-{res_config.get_res_readme(self.res_selected)}')
                self.refresh_right()

    def get_user_res(self):
        ans = True
        if path.exists(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png'):
            ans = AMessageBox.question(self, '您确定吗', '已存在自定资源，是否重新获取？')
        if ans:
            capture = adb.getScreen_std()
            output_image(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png', capture)
            respath = f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png'
            respath = respath.replace('/','\\\\')
            system('mspaint "{}"'.format(respath))
            self.refresh_right()

    def apply_advanced_options(self):
        common_options = self.advanced_option_editor_common.toPlainText()
        self_options = self.advanced_option_editor_self.toPlainText()

        if common_options == '{}' or common_options.strip() == '':
            res_config.delete(f'{self.res_selected}.common')
        else:
            try:
                common_options = literal_eval(common_options)
            except ValueError:
                common_options = dict()
            res_config.change(f'{self.res_selected}.common', common_options)

        if self_options == '{}' or self_options.strip() == '':
            res_config.delete(f'{self.res_selected}.self')
        else:
            try:
                self_options = literal_eval(self_options)
            except ValueError:
                self_options = dict()
            res_config.change(f'{self.res_selected}.self', self_options)

        self.refresh_right()

    def discard_advanced_options(self):
        self.refresh_right()

    def refresh_right(self):
        if (path.exists(f'./nres/{self.res_selected}.png')):
            self.tempPic_example.load(f'./nres/{self.res_selected}.png')
        else:
            self.tempPic_example.load('./gres/unknown.png')
        self.pic_example.setPixmap(self.tempPic_example.scaledToWidth(120, Qt.FastTransformation))

        if (path.exists(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png')):
            self.tempPic_user_res.load(f'C:/Users/{getlogin()}/AppData/Roaming/arkhelper/ures/{self.res_selected}.png')
        else:
            self.tempPic_user_res.load('./gres/unknown.png')
        self.pic_user_res.setPixmap(self.tempPic_user_res.scaledToWidth(120, Qt.FastTransformation))

        self.advanced_option_editor_common.setText(str(res_config.get_res_config(self.res_selected, 'common')))
        self.advanced_option_editor_self.setText(str(res_config.get_res_config(self.res_selected, 'self')))

        R.init()
        

if __name__ == '__main__':
    #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    #app = QApplication(sys.argv)
    res_manager = Res_manager()
    res_manager.show()
    sys.exit(app.exec())








