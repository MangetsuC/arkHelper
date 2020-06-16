# simpleArknightHelper
One Simple But Not Crude Arknight Helper	一款简单但不简陋的明日方舟小助手



##### 写在前面：

> 我本人并不是一名专业的程序员，代码质量并不高，时间也不充裕。同时也是一名github的新使用者，还请大家多多指教。



##### 下载地址：

| 网盘   | 链接                                          |
| :----- | --------------------------------------------- |
| 蓝奏云 | [下载地址](https://www.lanzous.com/b0d1w6v7g) |
|Github|[release](https://github.com/MangetsuC/arkHelper/releases)|
> * 下载提供的是master分支使用pyinstaller打包后的文件，可以直接使用，而无需安装python。
>
> * 国内用户可以使用蓝奏云链接，速度较快



##### **Requirements**：

| 库         | 版本  |
| ---------- | ----- |
| aircv      | 1.4.6 |
| win10toast | 0.9   |
| Pillow     | 7.1.2|
|PyQt5|5.15.0|

> 你也可以在仓库里找到requirements.txt，并使用pip install -r requirements.txt来部署环境。
***
##### 适用场景
# 任何场景！

##### 特别适用的场景
|活动|主线|剿灭作战|
|----|----|----|
|骑兵与猎人|1-7|全部|
|火蓝之心|||
|生于黑夜|||
***
## 关于这个小助手：

### 界面
***
![mainUI.png](https://i.loli.net/2020/06/16/HaLUPhEJMuy69RK.png)
* metro风格的界面参考了windows10的菜单，简洁明了  
* 可以方便地通过主界面上的菜单来选择您的模拟器！也可以自定义  
#### 作战
* 最主要的功能！往后看你可以知道如何使用！
#### 任务交付
* 不知您有没有注意到界面上被选中的任务开关，这代表在战斗结束后小助手会帮助您交付任务！
#### 获取信用
* 自动访问你的好友来获取更多的信用点数！
#### 这些是开关
* 因此，如果您不需要这个功能，可以单击以关闭
* 使用右键菜单来设置功能的默认状态
* ![setDefault.png](https://i.loli.net/2020/06/16/trH8BGDjoxzdMPX.png)
> ~~在config.ini中，可以通过修改[function]下的值来设置默认勾选的状态
> 后续应该会增加一个配置默认功能的设置界面~~已实现
### 公开招募计算器
***
![publiccall.png](https://i.loli.net/2020/05/15/jqCLGFU25nSrOeW.png)
* 便捷的公开招募计算器，从你的模拟器屏幕上直接获取标签信息！
* 主要的作用是避免错过一些不起眼的标签组合
### 自动勾选代理指挥
***
![auto.png](https://i.loli.net/2020/05/04/NbRDLEm437xFXWQ.png)
* 如果您忘记勾选代理，小助手会帮你选上！  
### 在战斗的任何阶段都可以启动小助手
***
![start2.png](https://i.loli.net/2020/05/04/LeoNdSZYhraT9xb.png)
* 不管是刚选好关卡，还是已经开始战斗，或是在结算界面，你都可以直接启动小助手！
* 注意：如果是结束后不会保留关卡选择的关卡（如教学关），小助手将无法正常工作  
### 简单的使用方法
***
![level.png](https://i.loli.net/2020/05/04/gcGrf53Ih8tyRdp.png)
1. 选择您想要重复的关卡
2. 点下小助手的启动虚拟博士按钮！（无论您有没有勾选代理指挥）  
### 提示！
***
![notice.png](https://i.loli.net/2020/05/04/bEJzCVqj37ADLmk.png)

* 在理智耗尽或是其他一些活动完成后，会通知提示您！