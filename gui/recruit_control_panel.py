import sys
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget,QApplication, QPushButton,QCheckBox, QDialog
from PySide6.QtCore import QMimeData,Qt
from PySide6.QtGui import QDrag,QPainter,QPixmap,QColor
from os import getcwd

sys.path.append(getcwd())

from common import user_data
from common import theme

class Label_with_pictext(QLabel):
    def __init__(self, pictext):
        super().__init__()
        self.pictext = pictext
        self.pixmap = QPixmap('./gres/{}.png'.format(pictext)).scaledToHeight(60)
        self.setPixmap(self.pixmap)

class DragIndexWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)        # 必须开启接受拖拽

        self.layout = QHBoxLayout(self)

        self.createComponent()            # 生成控件
        self.assembleComponent()        # 组装控件
 
    # 初始化内部的控件
    def createComponent(self):
        self.star_1 = Label_with_pictext('max_1')
        self.star_2 = Label_with_pictext('max_2')
        self.star_3 = Label_with_pictext('other')
        self.star_4 = Label_with_pictext('min_4')
        self.star_5 = Label_with_pictext('min_5')
        self.star_6 = Label_with_pictext('min_6')
        self.refresh = Label_with_pictext('refresh')
        self.lbs = dict(max_1 = self.star_1, max_2 = self.star_2,
                        other = self.star_3, min_4 = self.star_4,
                        min_5 = self.star_5, min_6 = self.star_6,
                        refresh = self.refresh)
        self.ans = [self.star_1, self.star_2, self.star_3, self.star_4, self.star_5, self.star_6, self.refresh]
        self.lb_store = None
 
    def assembleComponent(self):
        old_order = user_data.get('recruit.star_priority')
        for i in range(len(old_order)):
            self.layout.addWidget(self.lbs[old_order[i]])
 
    # 设定鼠标按下事件
    def mousePressEvent(self,event):
        item = self.childAt(event.position().toPoint())            # 通过位置获得控件
        self.lb_store = item
        self.lb_store.hide()
        if item == None:return                        # 如果为空则直接跳过
        index = self.layout.indexOf(item)            # 获得当前控件所处的布局中的索引位置
        self.drag = QDrag(item)                        # 创建QDrag对象
        mimedata = QMimeData()                        # 然后必须要有mimeData对象,用于传递拖拽控件的原始index信息
        mimedata.setText(str(index))                # 携带索引位置信息

        self.drag.setMimeData(mimedata)
        self.drag.setPixmap(item.pixmap)
        self.drag.setHotSpot(event.position().toPoint()-item.pos())
        self.drag.exec(Qt.MoveAction)                # 这个作为drag对象必须执行

    # 拖拽放下事件
    def dropEvent(self,event):
        point = event.pos()                    # 获得落点的坐标
        distance = float('inf')
        otherItem = None
        for i in self.lbs.keys():
            if abs(point.x() - self.lbs[i].pos().x()) < distance:
                otherItem = self.lbs[i]
                distance = abs(point.x() - self.lbs[i].pos().x())
        #otherItem = self.childAt(point)        # 获得当前落点上的控件
        if type(otherItem)==Label_with_pictext:
            if type(self.layout) == QHBoxLayout:
                self.HInsert(point,otherItem)    # 改变指定控件的位置(适用于水平布局)
            elif type(self.layout) == QVBoxLayout:
                self.VInsert(point,otherItem)    # 改变指定控件的位置(适用于垂直布局)
        self.lb_store.show()

    # 鼠标拖拽接受事件
    def dragEnterEvent(self,event):
        event.setDropAction(Qt.MoveAction)
        event.accept()
 
    # 插入模式(横向判断)
    def HInsert(self,point,otherItem):
        geometry = otherItem.geometry()
        x = geometry.x()
        x2 = geometry.x()+geometry.width()
        y = geometry.y()
        
        oldIndex = int(self.drag.mimeData().text())                # 获得原先存储在mimeData中的索引信息
        if oldIndex == self.layout.indexOf(otherItem):return    # 如果otherItem和oldItem实属同一个控件,则不做改变
        if point.x() <= x+int(geometry.width()/2):                                    # 插入在控件的左边
            oldItem = self.layout.takeAt(oldIndex).widget()
            index = self.layout.indexOf(otherItem)                # 重新获得当前控件所处的布局中的索引位置
            self.layout.insertWidget(index,oldItem)
        elif x2-int(geometry.width()/2) <= point.x():                                # 插入在控件的右边
            oldItem = self.layout.takeAt(oldIndex).widget()
            index = self.layout.indexOf(otherItem)                # 重新获得当前控件所处的布局中的索引位置
            self.layout.insertWidget(index+1,oldItem)
        else:
            pass
    
    def get_ans(self):
        self.ans.sort(key = lambda x:x.pos().x())
        star_priority = []
        for i in self.ans:
            star_priority.append(i.pictext)
        return star_priority

class RecruitControlPanel(QDialog):
    def __init__(self):
        super().__init__()
        self.top_layout = QVBoxLayout(self)
        self.setWindowTitle('公开招募控制面板')
        self.createComponent()
        self.assembleComponent()

    def createComponent(self):
        self.drag_widget = DragIndexWidget()
        self.lb_no_auto = QLabel('不自动招募')
        self.cb_min6 = QCheckBox('六星')
        self.cb_min6.setChecked(user_data.get('recruit.skip_config.min_6'))
        self.cb_min5 = QCheckBox('五星')
        self.cb_min5.setChecked(user_data.get('recruit.skip_config.min_5'))
        self.cb_min4 = QCheckBox('四星')
        self.cb_min4.setChecked(user_data.get('recruit.skip_config.min_4'))
        self.cb_other = QCheckBox('三星')
        self.cb_other.setChecked(user_data.get('recruit.skip_config.other'))
        self.cb_max2 = QCheckBox('二星')
        self.cb_max2.setChecked(user_data.get('recruit.skip_config.max_2'))
        self.cb_max1 = QCheckBox('一星')
        self.cb_max1.setChecked(user_data.get('recruit.skip_config.max_1'))
        self.lb_priority = QLabel('优先级')
        self.lb_priority_high = QLabel('高')
        self.lb_priority_low = QLabel('低')

    def assembleComponent(self):
        self.h_layout_cb = QHBoxLayout()
        self.h_layout_cb.addWidget(self.cb_min6, alignment=Qt.AlignCenter)
        self.h_layout_cb.addWidget(self.cb_min5, alignment=Qt.AlignCenter)
        self.h_layout_cb.addWidget(self.cb_min4, alignment=Qt.AlignCenter)
        self.h_layout_cb.addWidget(self.cb_other, alignment=Qt.AlignCenter)
        self.h_layout_cb.addWidget(self.cb_max2, alignment=Qt.AlignCenter)
        self.h_layout_cb.addWidget(self.cb_max1, alignment=Qt.AlignCenter)

        self.h_layout_lb = QHBoxLayout()
        self.h_layout_lb.addWidget(self.lb_priority_high, alignment=Qt.AlignLeft)
        self.h_layout_lb.addWidget(self.lb_priority_low, alignment=Qt.AlignRight)

        self.top_layout.addWidget(self.lb_no_auto, alignment=Qt.AlignCenter)
        self.top_layout.addLayout(self.h_layout_cb)
        self.top_layout.addWidget(self.lb_priority, alignment=Qt.AlignCenter)
        self.top_layout.addLayout(self.h_layout_lb)
        self.top_layout.addWidget(self.drag_widget, alignment=Qt.AlignCenter)

    def get_ans(self):
        star_priority = self.drag_widget.get_ans()
        skip_config = dict(min_6 = self.cb_min6.isChecked(),
                            min_5 = self.cb_min5.isChecked(),
                            min_4 = self.cb_min4.isChecked(),
                            other = self.cb_other.isChecked(),
                            max_2 = self.cb_max2.isChecked(),
                            max_1 = self.cb_max1.isChecked())
        ans = dict(skip_config = skip_config, star_priority = star_priority)
        return ans


def set_recruit_rule():
    temp_recruit_control_panel = RecruitControlPanel()
    temp_recruit_control_panel.exec()
    ans = temp_recruit_control_panel.get_ans()
    user_data.change('recruit', ans)
    del temp_recruit_control_panel


if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_recruit_rule()
    #sys.exit(app.exec())
























