from ctypes import c_long, pythonapi, py_object
 
def forceThreadStop(thread):
    tid = c_long(thread.ident)
    res = pythonapi.PyThreadState_SetAsyncExc(tid, py_object(SystemExit))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
