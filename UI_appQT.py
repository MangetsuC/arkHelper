import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QIcon, QScreen, QAction
from PySide6.QtWidgets import (QApplication,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QInputDialog, QLabel, QMenu, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget)

from common import user_data, simulator_data, config_path, theme, app_ico, app
from common2 import version

class UI_Arkhelper(QWidget):
    def __init__(self):
        super().__init__()
        self.moveFlag = False

        self.initUI()
        self.applyStyleSheet()

    def initUI(self): 

        self.setWindowIcon(app_ico)
        self.setWindowTitle('明日方舟小助手')

        self.resize(420, 150)

        self.line = QAction(self)
        self.line.setSeparator(True)

        self.setWindowFlag(Qt.FramelessWindowHint) #隐藏边框

        self.rightClickMenu = QMenu()#右键菜单
        
        self.topLayout = QVBoxLayout(self)

        self.init_toolbar()
        self.init_control_panel()
        self.init_adb_connect()

        self.init_act_set_default()
        self.init_simulator_choices()
        self.init_simulator_selected()

        #self.control_panel_widget.hide()

    def init_toolbar(self):
        self.lTitle = QLabel('明日方舟小助手')
        
        self.lVer = QLabel(f'v{version}')
        

        self.btnExit = QPushButton('×',self)
        self.btnExit.setMinimumSize(30, 30)

        self.btnExit.setToolTip('关闭')

        self.btnMinimize = QPushButton('-',self)
        self.btnMinimize.setMinimumSize(30, 30)
        
        self.btnMinimize.setToolTip('最小化')

        self.btnSetting = QPushButton('≡',self)
        self.btnSetting.setMinimumSize(30, 30)
        
        self.btnSetting.setToolTip('设置')

        self.settingMenu = QMenu() #创建设置按钮菜单
        
        self.actSimulator = QMenu('模拟器', parent=self.settingMenu) #模拟器二级菜单
        self.actSimulator_list = []
        self.actSimulator_del = QMenu('删除', parent=self.actSimulator) #删除模拟器三级菜单
        self.actSimulator_del_list = []

        self.actTheme = QAction('主题设置', parent=self.settingMenu)
        self.actConsole = QAction('控制台', parent=self.settingMenu)
        self.actCheckUpdate = QAction('前往下载', parent=self.settingMenu)
        self.actIndex = QAction('访问主页', parent=self.settingMenu)

        self.settingMenu.addMenu(self.actSimulator) #模拟器二级菜单

        self.settingMenu.addAction(self.actConsole) #控制台

        self.settingMenu.addAction(self.actTheme) 

        self.settingMenu.addAction(self.actCheckUpdate) #蓝奏云地址

        self.settingMenu.addAction(self.actIndex) #主页

        self.btnSetting.setMenu(self.settingMenu)

        self.btnUpdate = QPushButton('∧',self)
        self.btnUpdate.setMinimumSize(30, 30)
        
        self.btnUpdate.setToolTip('自动更新')
        self.btnUpdate.hide()

        self.btnShowMsg = QPushButton('!',self)
        self.btnShowMsg.setMinimumSize(30, 30)
        
        self.btnShowMsg.setToolTip('查看公告')
        #self.btnShowMsg.hide()

        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.addWidget(self.lTitle)
        self.toolbar_layout.addWidget(self.lVer)
        self.toolbar_layout.addStretch(1)
        self.toolbar_layout.addWidget(self.btnShowMsg)
        self.toolbar_layout.addWidget(self.btnUpdate)
        self.toolbar_layout.addWidget(self.btnSetting)
        self.toolbar_layout.addWidget(self.btnMinimize)
        self.toolbar_layout.addWidget(self.btnExit)

        self.topLayout.addLayout(self.toolbar_layout)
        pass

    def init_control_panel(self):
        self.btn_start_or_stop = QPushButton('启动虚拟博士', self) #启动/停止按钮
        self.btn_start_or_stop.setMinimumSize(180, 131)
        self.btn_start_or_stop.setEnabled(False)
        

        self.btn_loop = QPushButton('战斗:无限', self) #战斗可选按钮
        self.btn_loop.setCheckable(True)
        self.btn_loop.setMinimumSize(75, 40)

        self.btn_loop.setToolTip('从你目前处在的关卡开始循环作战，直到理智不足')

        self.menu_loop = QMenu()
        self.right_click_menu_setstylesheet(self.menu_loop)
        self.act_default_loop = QAction('默认开启')
        self.menu_loop.addAction(self.act_default_loop)



        self.btn_auto_recruit = QPushButton('自动公招', self) #自动公招可选按钮
        self.btn_auto_recruit.setCheckable(True)
        self.btn_auto_recruit.setMinimumSize(75, 40)
        self.btn_auto_recruit.setToolTip('自动进行公开招募，在右键菜单中进行配置')

        self.menu_auto_recruit = QMenu()
        self.right_click_menu_setstylesheet(self.menu_auto_recruit)
        self.act_default_recruit = QAction('默认开启')
        self.act_set_recruit_rule = QAction('配置公招')
        self.menu_auto_recruit.addAction(self.act_default_recruit)
        self.menu_auto_recruit.addAction(self.act_set_recruit_rule)

        self.btn_res_manager = QPushButton('资源管理器', self)
        self.btn_res_manager.setMinimumSize(75, 40)

        self.btn_res_scope = QPushButton('资源状态观测器', self)
        self.btn_res_scope.setMinimumSize(155, 40)

        self.btn_submit_task = QPushButton('任务交付', self) #任务交付可选按钮
        self.btn_submit_task.setCheckable(True)
        self.btn_submit_task.setMinimumSize(75, 40)
        self.btn_submit_task.setToolTip('自动交付任务')

        self.menu_submit_task = QMenu()
        self.right_click_menu_setstylesheet(self.menu_submit_task)
        self.act_default_task = QAction('默认开启')
        self.menu_submit_task.addAction(self.act_default_task)

        self.btn_credit = QPushButton('获取信用', self)
        self.btn_credit.setCheckable(True)
        self.btn_credit.setMinimumSize(75, 40)
        self.btn_credit.setToolTip('自动拜访好友的基建以获取信用点')

        self.menu_credit = QMenu()
        self.right_click_menu_setstylesheet(self.menu_credit)
        self.act_default_credit = QAction('默认开启')
        self.menu_credit.addAction(self.act_default_credit)

        self.btn_shutdown = QPushButton('完成后关机', self)
        self.btn_shutdown.setCheckable(True)
        self.btn_shutdown.setMinimumSize(155, 40)

        self.control_panel_widget = QWidget()
        self.grid = QGridLayout(self.control_panel_widget)
        self.grid.setVerticalSpacing(5)
        self.grid.setHorizontalSpacing(5)
        
        self.grid.addWidget(self.btn_start_or_stop, 0, 0, 3, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_loop, 0, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_res_manager, 1, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_res_scope, 1, 2, 1, 2, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_submit_task, 0, 2, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_credit, 0, 3, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_auto_recruit, 2, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid.addWidget(self.btn_shutdown, 2, 2, 1, 2)

        self.topLayout.addWidget(self.control_panel_widget)

    def init_adb_connect(self):
        self.connect_widget = QWidget()
        self.connect_layout = QGridLayout(self.connect_widget)
        self.label_chosen_sim = QLabel('当前:{}'.format(user_data.get('simulator')))
        self.label_size = QLabel('分辨率:?*?')
        self.btn_adb_connect = QPushButton('连接')
        self.btn_adb_connect.setMinimumSize(75, 40)
        self.label_issucceed = QLabel('状态：尚未连接')
        self.connect_layout.addWidget(self.label_chosen_sim, 0, 0)
        self.connect_layout.addWidget(self.label_size, 1, 0)
        self.connect_layout.addWidget(self.btn_adb_connect, 0, 1)
        self.connect_layout.addWidget(self.label_issucceed, 1, 1)

        self.menu_adb_connect = QMenu()
        self.right_click_menu_setstylesheet(self.menu_adb_connect)
        self.act_skip_connect = QAction('跳过连接')
        self.menu_adb_connect.addAction(self.act_skip_connect)

        self.topLayout.addWidget(self.connect_widget)

        
        self.label_chosen_sim.setStyleSheet(f'''
                                    QLabel{{color:{theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')
        
        self.label_size.setStyleSheet(f'''
                                    QLabel{{color:{theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')
        self.btn_adb_connect.setStyleSheet(f'''QPushButton{{border:0px;background:{theme.getFgColor()};
                                        color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:15pt;}}
                                        QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                        QPushButton:pressed{{background:{theme.getPressedColor()};font:13pt;}}
                                        QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()}}}
                                            ''')
        self.label_issucceed.setStyleSheet(f'''
                                    QLabel{{color:{theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')

    def applyStyleSheet(self):
        self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}
                                QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:9pt;}}
                                QPushButton{{border:0px;background:{theme.getFgColor()};
                                color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                QPushButton:pressed{{background:{theme.getPressedColor()};font:9pt;}}
                                QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()}}}
                                QInputDialog{{background-color:{theme.getBgColor()};}}
                                QLineEdit{{color:{theme.getFontColor()};}}
                                QMessageBox{{background-color:{theme.getFgColor()};}}
                                QToolTip {{font-family:"Microsoft YaHei", SimHei, SimSun; font-size:10pt; 
                                        color:{theme.getFontColor()};
                                        padding:5px;
                                        border-style:solid; border-width:1px; border-color:gray;
                                        background-color:{theme.getBgColor()};}}
                            ''')
        self.lTitle.setStyleSheet(f'''
                                    QLabel{{color:{theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')
        self.lVer.setStyleSheet(f'''
                                    QLabel{{color:{theme.getFontColor()};
                                    font-family:"Microsoft YaHei", SimHei, SimSun;font:11pt;
                                    padding-left:5px; padding-top:0px; padding-bottom:5px;}}
                                    ''')
        self.btnExit.setStyleSheet(f'''QPushButton{{background:{theme.getBgColor()};font-family:SimHei, SimSun;font:20pt;}}
                                            QPushButton:pressed{{background:{theme.getBgColor()};font:16pt;}}
                                            ''')
        self.btnMinimize.setStyleSheet(f'''QPushButton{{background:{theme.getBgColor()};font-family:SimSun;font:normal 28pt;}}
                                            QPushButton:pressed{{background:{theme.getBgColor()};
                                            font-family:SimSun;font:20pt;}}
                                            ''')
        self.btnSetting.setStyleSheet(f'''QPushButton{{background:{theme.getBgColor()};font-family:SimHei, SimSun;font:16pt;}}
                                            QPushButton:pressed{{background:{theme.getBgColor()};
                                            font-family:SimHei, SimSun;font:14pt;}}
                                            QPushButton:menu-indicator{{image:none;width:0px;}}
                                            ''')
        self.btnUpdate.setStyleSheet(f'''QPushButton{{background:{theme.getBgColor()};font-family:SimHei, SimSun;font:14pt;}}
                                            QPushButton:pressed{{background:{theme.getBgColor()};
                                            font-family:SimHei, SimSun;font:12pt;}}
                                            ''')
        self.btnShowMsg.setStyleSheet(f'''QPushButton{{background:{theme.getBgColor()};font-family:SimHei, SimSun;font:14pt;}}
                                            QPushButton:pressed{{background:{theme.getBgColor()};
                                            font-family:SimHei, SimSun;font:12pt;}}
                                            ''')
        self.btn_start_or_stop.setStyleSheet('''QPushButton{font:13pt;}''')
        self.settingMenu.setStyleSheet(f'''QMenu {{color:{theme.getFontColor()};
                                                font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                                background-color:{theme.getBgColor()}; margin:3px;}}
                                                QMenu:item {{padding:8px 32px;}}
                                                QMenu:item:selected {{background-color: {theme.getFgColor()};}}
                                                QMenu:icon{{padding: 8px 20px;}}
                                                QMenu:separator{{background-color: {theme.getFontColor()}; 
                                                        height:1px; margin-left:2px; margin-right:2px;}}''')

    def right_click_menu_setstylesheet(self, menu_item):
        menu_item.setStyleSheet(f'''QMenu {{color:{theme.getFontColor()};
                                                    font-family: "Microsoft YaHei", SimHei, SimSun;font:10pt;
                                                    background-color:{theme.getBgColor()}; margin:3px;}}
                                                QMenu:item {{padding:8px 32px;}}
                                                QMenu:item:selected {{ background-color: {theme.getFgColor()};}}
                                                QMenu:icon{{padding: 8px 20px;}}
                                                QMenu:separator{{background-color: {theme.getFontColor()}; 
                                                    height:1px; margin-left:2px; margin-right:2px;}}''')

    def init_act_set_default(self):
        if user_data.get('loop.default'):
            self.act_default_loop.setIcon(QIcon(theme.getSelectedIcon()))
        else:
            self.act_default_loop.setIcon(QIcon('./gres/unSelected.png'))

        if user_data.get('task.default'):
            self.act_default_task.setIcon(QIcon(theme.getSelectedIcon()))
        else:
            self.act_default_task.setIcon(QIcon('./gres/unSelected.png'))
        
        if user_data.get('credit.default'):
            self.act_default_credit.setIcon(QIcon(theme.getSelectedIcon()))
        else:
            self.act_default_credit.setIcon(QIcon('./gres/unSelected.png'))
        
        if user_data.get('recruit.default'):
            self.act_default_recruit.setIcon(QIcon(theme.getSelectedIcon()))
        else:
            self.act_default_recruit.setIcon(QIcon('./gres/unSelected.png'))

    def init_simulator_choices(self):
        '添加模拟器菜单中的选项'
        self.actSimulator_add = QAction('添加/修改')

        self.actSimulator.clear()
        self.actSimulator_del.clear()
        self.actSimulator_list.clear()
        self.actSimulator_del_list.clear()
        for i in simulator_data.get_simulators():
            temp_act = QAction(i)
            self.actSimulator_list.append(temp_act)
            self.actSimulator.addAction(temp_act)

            temp_act_del = QAction(i)
            self.actSimulator_del_list.append(temp_act_del)
            self.actSimulator_del.addAction(temp_act_del)
            
        self.actSimulator.addSeparator()
        self.actSimulator.addAction(self.actSimulator_add)
        self.actSimulator.addMenu(self.actSimulator_del)

    def init_simulator_selected(self):
        '初始化模拟器选择'
        slrName = user_data.get('simulator')
        self.label_chosen_sim.setText('当前:{}'.format(slrName))

        for i in self.actSimulator_list:
            if i.text() == slrName:
                i.setIcon(QIcon(theme.getSelectedIcon()))
            else:
                i.setIcon(QIcon('./gres/unSelected.png'))

    def mousePressEvent(self, event):
        self.mousePos = event.globalPosition().toPoint() - self.pos() #获取鼠标相对窗口的位置
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            event.accept()
        elif event.button() == Qt.RightButton:
            pos = event.position().toPoint()
            item = self.childAt(pos)
            menu = None
            match item:
                case self.btn_auto_recruit:
                    menu = self.menu_auto_recruit
                case self.btn_loop:
                    menu = self.menu_loop
                case self.btn_credit:
                    menu = self.menu_credit
                case self.btn_submit_task:
                    menu = self.menu_submit_task
                case self.btn_adb_connect:
                    menu = self.menu_adb_connect
                case _:
                    return
            menu.exec(QCursor.pos())
            event.ignore()
            
            
    def mouseMoveEvent(self, QMouseEvent):
        if self.moveFlag:  
            self.move(QMouseEvent.globalPosition().toPoint() - self.mousePos) #更改窗口位置
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        #停止窗口移动
        self.moveFlag = False


if __name__ == '__main__':
    app.processEvents()
    ui = UI_Arkhelper()
    ui.show()
    sys.exit(app.exec())
















