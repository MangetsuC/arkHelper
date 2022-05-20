import sys
import string
from os import getcwd

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QColor, QDrag, QPainter, QPixmap, QCursor
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                               QPushButton, QTabWidget, QVBoxLayout, QWidget)

sys.path.append(getcwd())

from common import app_ico, simulator_data, theme, user_data, app
from gui.QLeftTabWidget import QLeftTabWidget


class Simulator_Editor(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(app_ico)
        self.top_layout = QVBoxLayout(self)
        self.setWindowTitle('模拟器编辑器')
        self.init_ui()
    
    def init_ui(self):
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.title = QLabel('模拟器编辑器')

        self.btn_close = QPushButton('×')
        self.btn_close.setMinimumSize(30, 30)
        self.btn_close.clicked.connect(self.close)

        self.tool_bar_layout = QHBoxLayout()
        self.tool_bar_layout.addWidget(self.title, alignment=Qt.AlignLeading)
        self.tool_bar_layout.addWidget(self.btn_close, alignment=Qt.AlignRight)

        self.top_layout.addLayout(self.tool_bar_layout)

        tab_add_simulator = self.create_tab_simulator()
        tab_add_simulator[1]['btn_confirm'].setText('新增')
        tab_add_simulator[1]['btn_delete'].hide()

        self.tab_widget = QLeftTabWidget()
        self.tab_widget.addTab(tab_add_simulator[0], '新建模拟器')

        for i in simulator_data.get_simulators():
            tab_temp_simulator = self.create_tab_simulator(i)
            tab_temp_simulator[1]['le_simulator_name'].setEnabled(False)
            temp_ip = simulator_data.get(f'{i}.ip')
            temp_adb = simulator_data.get(f'{i}.adb')
            if '127.0.0.1' in temp_ip:
                tab_temp_simulator[1]['btn_localhost'].setChecked(True)
                tab_temp_simulator[1]['btn_emulator'].setChecked(False)
                tab_temp_simulator[1]['btn_custom'].setChecked(False)
                tab_temp_simulator[1]['le_localhost'].show()
                tab_temp_simulator[1]['le_emulator'].hide()
                tab_temp_simulator[1]['le_custom'].hide()
                tab_temp_simulator[1]['le_localhost'].setText(temp_ip.split(':')[1])
            elif 'emulator' in temp_ip:
                tab_temp_simulator[1]['btn_localhost'].setChecked(False)
                tab_temp_simulator[1]['btn_emulator'].setChecked(True)
                tab_temp_simulator[1]['btn_custom'].setChecked(False)
                tab_temp_simulator[1]['le_localhost'].hide()
                tab_temp_simulator[1]['le_emulator'].show()
                tab_temp_simulator[1]['le_custom'].hide()
                tab_temp_simulator[1]['le_emulator'].setText(temp_ip.split('-')[1])
            else:
                tab_temp_simulator[1]['btn_localhost'].setChecked(False)
                tab_temp_simulator[1]['btn_emulator'].setChecked(False)
                tab_temp_simulator[1]['btn_custom'].setChecked(True)
                tab_temp_simulator[1]['le_localhost'].hide()
                tab_temp_simulator[1]['le_emulator'].hide()
                tab_temp_simulator[1]['le_custom'].show()
                tab_temp_simulator[1]['le_custom'].setText(temp_ip)
            if temp_adb == 'internal':
                tab_temp_simulator[1]['btn_adb_internal'].setChecked(True)
                tab_temp_simulator[1]['btn_adb_external'].setChecked(False)
            else:
                tab_temp_simulator[1]['btn_adb_internal'].setChecked(False)
                tab_temp_simulator[1]['btn_adb_external'].setChecked(True)

            self.tab_widget.addTab(tab_temp_simulator[0], i)

        self.tab_widget.finish_add()
        
        #self.tab_widget.addTab(tab_add_simulator1[0], '新增1')

        self.top_layout.addWidget(self.tab_widget, alignment=Qt.AlignCenter)

        self.set_style_sheet()


    def create_tab_simulator(self, simulator_name = '新建模拟器'):
        tab_simulator = QWidget()

        label_simulator_name = QLabel('名称')
        le_simulator_name = QLineEdit(simulator_name)
        le_simulator_name.setAlignment(Qt.AlignCenter)
        le_simulator_name.setMinimumHeight(40)
        le_simulator_name.setFixedWidth(226)

        label_simulator_ip = QLabel('模拟器IP地址')
        btn_localhost = QPushButton('127.0.0.1:')
        btn_localhost.setMinimumSize(100, 40)
        btn_localhost.setCheckable(True)
        btn_localhost.setChecked(True)
        btn_emulator = QPushButton('emulator-')
        btn_emulator.setMinimumSize(100, 40)
        btn_emulator.setCheckable(True)
        btn_custom = QPushButton('其他')
        btn_custom.setMinimumSize(100, 40)
        btn_custom.setCheckable(True)
        le_localhost = QLineEdit('7555')
        le_localhost.setAlignment(Qt.AlignCenter)
        le_localhost.setMinimumHeight(40)
        le_localhost.setFixedWidth(120)
        le_emulator = QLineEdit('5554')
        le_emulator.setAlignment(Qt.AlignCenter)
        le_emulator.setMinimumHeight(40)
        le_emulator.setFixedWidth(120)
        le_emulator.hide()
        le_custom = QLineEdit()
        le_custom.setAlignment(Qt.AlignCenter)
        le_custom.setMinimumHeight(40)
        le_custom.setFixedWidth(120)
        le_custom.hide()

        def reset_btn_ip_checked_and_hide_le_ip():
            sender = self.childAt(QCursor().pos()-self.pos())
            le_localhost.show()
            le_emulator.show()
            le_custom.show()
            if sender != btn_localhost:
                btn_localhost.setChecked(False)
                le_localhost.hide()
            if sender != btn_emulator:
                btn_emulator.setChecked(False)
                le_emulator.hide()
            if sender != btn_custom:
                btn_custom.setChecked(False)
                le_custom.hide()
            if not (btn_localhost.isChecked() or btn_emulator.isChecked() or btn_custom.isChecked()):
                btn_localhost.setChecked(True)
                le_localhost.show()
                le_emulator.hide()
                le_custom.hide()

        btn_localhost.clicked.connect(reset_btn_ip_checked_and_hide_le_ip)
        btn_emulator.clicked.connect(reset_btn_ip_checked_and_hide_le_ip)
        btn_custom.clicked.connect(reset_btn_ip_checked_and_hide_le_ip)

        label_adb_path = QLabel('使用')
        btn_adb_internal = QPushButton('内部adb')
        btn_adb_internal.setMinimumSize(100, 40)
        btn_adb_internal.setCheckable(True)
        btn_adb_internal.setChecked(True)
        btn_adb_external = QPushButton('外部adb')
        btn_adb_external.setMinimumSize(100, 40)
        btn_adb_external.setCheckable(True)

        def reset_btn_adb():
            sender = self.childAt(QCursor().pos()-self.pos())
            if sender != btn_adb_internal:
                btn_adb_internal.setChecked(False)
            if sender != btn_adb_external:
                btn_adb_external.setChecked(False)
            if not (btn_adb_internal.isChecked() or btn_adb_external.isChecked()):
                btn_adb_internal.setChecked(True)

        btn_adb_internal.clicked.connect(reset_btn_adb)
        btn_adb_external.clicked.connect(reset_btn_adb)

        btn_confirm = QPushButton('确认')
        btn_confirm.setMinimumSize(120, 40)
        btn_delete = QPushButton('删除')
        btn_delete.setMinimumSize(120, 40)

        def confirm_or_add():
            name = le_simulator_name.text()
            if name in simulator_data.get_simulators() and btn_confirm.text() == '新增':
                name = name.strip(string.digits)
                for i in range(1, 100):
                    temp_name = name + str(i)
                    if not temp_name in simulator_data.get_simulators():
                        name = temp_name
                        break

            if btn_localhost.isChecked():
                temp_ip = '127.0.0.1:' + le_localhost.text().strip()
            elif btn_emulator.isChecked():
                temp_ip = 'emulator-' + le_emulator.text().strip()
            else:
                temp_ip = le_custom.text().strip()
            simulator_data.change(f'{name}.ip', temp_ip)

            if btn_adb_internal.isChecked():
                simulator_data.change(f'{name}.adb', 'internal')
            else:
                simulator_data.change(f'{name}.adb', 'external')
            self.close()

        def delete_simulator():
            if le_simulator_name.text() in simulator_data.get_simulators():
                simulator_data.delete(f'{le_simulator_name.text()}')
            self.close()

        btn_confirm.clicked.connect(confirm_or_add)
        btn_delete.clicked.connect(delete_simulator)

        components_dict = dict(label_simulator_name = label_simulator_name,
                               le_simulator_name = le_simulator_name,
                               label_simulator_ip = label_simulator_ip,
                               btn_localhost = btn_localhost,
                               btn_emulator = btn_emulator,
                               btn_custom = btn_custom,
                               le_localhost = le_localhost,
                               le_emulator = le_emulator,
                               le_custom = le_custom,
                               label_adb_path = label_adb_path,
                               btn_adb_internal = btn_adb_internal,
                               btn_adb_external = btn_adb_external,
                               btn_confirm = btn_confirm,
                               btn_delete = btn_delete)

        layout_tab_simulator = QGridLayout(tab_simulator)

        layout_tab_simulator.addWidget(label_simulator_name, 0, 0, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(le_simulator_name, 0, 1, 1, 2, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(label_simulator_ip, 1, 0, 3, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_localhost, 1, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_emulator, 2, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_custom, 3, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(le_localhost, 1, 2, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(le_emulator, 2, 2, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(le_custom, 3, 2, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(label_adb_path, 4, 0, 2, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_adb_internal, 4, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_adb_external, 5, 1, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_delete, 4, 2, alignment=Qt.AlignCenter)
        layout_tab_simulator.addWidget(btn_confirm, 5, 2, alignment=Qt.AlignCenter)

        return [tab_simulator, components_dict]

    def mousePressEvent(self, event):
        self.mousePos = event.globalPosition().toPoint() - self.pos() #获取鼠标相对窗口的位置
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            event.accept()
            
    def mouseMoveEvent(self, QMouseEvent):
        if self.moveFlag:  
            self.move(QMouseEvent.globalPosition().toPoint() - self.mousePos) #更改窗口位置
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        #停止窗口移动
        self.moveFlag = False

    def set_style_sheet(self):
        self.setStyleSheet(f'''QWidget{{background:{theme.getBgColor()}}}
                                QLabel{{color:{theme.getFontColor()};font-family:"Microsoft YaHei", SimHei, SimSun;font:12pt;}}
                                QPushButton{{border:0px;background:{theme.getFgColor()};
                                color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:12pt;}}
                                QPushButton:hover{{border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                QPushButton:pressed{{background:{theme.getPressedColor()};font:11pt;}}
                                QPushButton:checked{{background:{theme.getThemeColor()};color:{theme.getCheckedFontColor()}}}
                                QInputDialog{{background-color:{theme.getBgColor()};}}
                                QLineEdit{{color:{theme.getFontColor()};font-family: "Microsoft YaHei", SimHei, SimSun;font:12pt;
                                       border-style:solid;border-width:1px;border-color:{theme.getBorderColor()};}}
                                QToolTip{{font-family:"Microsoft YaHei", SimHei, SimSun; font-size:10pt; 
                                        color:{theme.getFontColor()};
                                        padding:5px;
                                        border-style:solid; border-width:1px; border-color:gray;
                                        background-color:{theme.getBgColor()};}}
                            ''')
        self.btn_close.setStyleSheet(f'''QPushButton{{background:{theme.getBgColor()};font-family:SimHei, SimSun;font:20pt;}}
                                        QPushButton:pressed{{background:{theme.getBgColor()};font:16pt;}}
                                        ''')
        
def edit_simulator():
    simulator_editor = Simulator_Editor()
    simulator_editor.exec()
    del simulator_editor



if __name__ == "__main__":
    #app = QApplication(sys.argv)
    temp = Simulator_Editor()
    temp.show()
    sys.exit(app.exec())
    


















