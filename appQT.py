import cgitb
import sys
from threading import Thread
from webbrowser import open as openUrl

from PySide6.QtWidgets import QApplication

from foo.ui.launch import Launch, after_init, blackboard
from foo.win.exitThread import forceThreadStop

from arknights_ import loop, task, visit, recruit, common_operation
from gui.recruit_control_panel import set_recruit_rule

from common import user_data, simulator_data, config_path, theme, app
from common2 import adb, version
from common_gui import console, res_manager, res_scope, theme_editor

from UI_appQT import UI_Arkhelper

class Arkhelper(UI_Arkhelper):
    def __init__(self):
        super().__init__()
        self.thread_start = None

        self.init_checked_state()
        self.slot_connect()

        self.connect_widget.show()
        self.control_panel_widget.hide()
        self.show()

    def slot_connect(self):
        after_init.need_update.connect(self.lVer.setText) #新版本提示

        self.btnShowMsg.clicked.connect(blackboard.show) #显示公告按钮！

        self.btn_adb_connect.clicked.connect(self.adb_connect) #连接adb
        self.act_skip_connect.triggered.connect(self.show_control_panel) #跳过连接步骤

        self.btnMinimize.clicked.connect(self.showMinimized) #最小化
        self.btnExit.clicked.connect(self.exit) #关闭

        self.btn_start_or_stop.clicked.connect(self.press_btn_start_or_stop) #开始或停止

        self.btn_res_manager.clicked.connect(res_manager.show) #资源管理器
        self.btn_res_scope.clicked.connect(res_scope.show) #资源检测器

        self.actConsole.triggered.connect(console.show) #控制台
        self.actTheme.triggered.connect(theme_editor.show) #主题设置

        self.act_simulator_slot_connect() #模拟器选择
        self.actCheckUpdate.triggered.connect(self.openUpdate)
        self.actIndex.triggered.connect(self.openIndex)

        self.act_set_recruit_rule.triggered.connect(self.change_recruit_rule) #公开招募右键菜单中的设置面板

        #右键菜单中的默认开启
        self.act_default_task.triggered.connect(self.change_default)
        self.act_default_credit.triggered.connect(self.change_default)
        self.act_default_loop.triggered.connect(self.change_default)
        self.act_default_recruit.triggered.connect(self.change_default)

    def act_simulator_slot_connect(self):
        self.actSimulator_add.triggered.connect(self.add_simulator)

        for i in self.actSimulator_list:
            i.triggered.connect(self.change_simulator_selected)

        for i in self.actSimulator_del_list:
            i.triggered.connect(self.delete_simulator)
        

    def adb_connect(self):
        self.label_issucceed.setText('状态：连接中……')
        QApplication.processEvents()
        issucceed = adb.connect()
        if issucceed:
            self.label_issucceed.setText('状态：已连接')
            self.label_size.setText(f'分辨率:{adb.screenX}*{adb.screenY}')
            self.btn_start_or_stop.setEnabled(True)
            self.show_control_panel()
        else:
            self.label_issucceed.setText('状态：失败')

    def show_control_panel(self):
        self.connect_widget.hide()
        self.control_panel_widget.show()

    def change_default(self):
        sender = self.sender()
        match sender:
            case self.act_default_loop:
                user_data.change('loop.default', not user_data.get('loop.default'))
            case self.act_default_recruit:
                user_data.change('recruit.default', not user_data.get('recruit.default'))
            case self.act_default_credit:
                user_data.change('credit.default', not user_data.get('credit.default'))
            case self.act_default_task:
                user_data.change('task.default', not user_data.get('task.default'))
                
        self.init_act_set_default()

    def init_checked_state(self):
        self.btn_loop.setChecked(user_data.get('loop.default'))
        self.btn_auto_recruit.setChecked(user_data.get('recruit.default'))
        self.btn_credit.setChecked(user_data.get('credit.default'))
        self.btn_submit_task.setChecked(user_data.get('task.default'))

    def change_recruit_rule(self):
        set_recruit_rule()

    def change_simulator_selected(self):
        simulator = self.sender()
        user_data.change('simulator', simulator.text())

        self.init_simulator_selected()
        adb.changeSimulator(user_data)

    def delete_simulator(self):
        simulator = self.sender()
        simulator_data.delete(simulator.text())

        self.init_simulator_choices()
        self.init_simulator_selected()
        self.act_simulator_slot_connect()
        adb.changeSimulator(user_data)

    def add_simulator(self):
        pass

        
    def exit(self):
        '退出按钮'
        self.hide()
        self.force_stop()

        sys.exit() #为了解决Error in atexit._run_exitfuncs:的问题，实际上我完全不知道这为什么出现

    def openUpdate(self):
        openUrl('https://mangetsuc.lanzoui.com/b0d1w6v7g')

    def openIndex(self):
        openUrl('https://github.com/MangetsuC/arkHelper')

    def start(self):
        if self.btn_loop.isChecked():
            loop.main()
            common_operation.goto_mainpage()

        if self.btn_auto_recruit.isChecked():
            recruit.main()
            common_operation.goto_mainpage()

        if self.btn_credit.isChecked():
            common_operation.enter_friends()
            visit.main()
            common_operation.goto_mainpage()

        if self.btn_submit_task.isChecked():
            common_operation.enter_task()
            task.main()
            common_operation.goto_mainpage()

        if self.btn_shutdown.isChecked():
            adb.cmd.shutdown(time=120)
        
        self.thread_start = None
        self.btn_start_or_stop.setText('启动虚拟博士')

    def press_btn_start_or_stop(self):
        if '启动' in self.btn_start_or_stop.text():
            self.create_start_thread()
        else:
            self.force_stop()

    def create_start_thread(self):
        self.btn_start_or_stop.setText('停止虚拟博士')
        self.thread_start = Thread(target=self.start)
        self.thread_start.daemon = True
        self.thread_start.start()

    def force_stop(self):
        self.btn_start_or_stop.setText('启动虚拟博士')
        if self.thread_start != None:
            forceThreadStop(self.thread_start)
        self.thread_start = None

if __name__ == '__main__':
    cgitb.enable(format = 'text')
    launch = Launch()
    app.processEvents()
    ah = Arkhelper()
    launch.finish(ah)
    after_init.start()
    sys.exit(app.exec())
