from win10toast import ToastNotifier

toast = ToastNotifier()

def broadcastMsg(title = "This is title.", text = "This is message.", iconPath = False, lastTime = 10, threaded = True):
    toast.show_toast(title, text, iconPath, lastTime, threaded)