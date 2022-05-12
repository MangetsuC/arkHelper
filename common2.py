from common import simulator_data, user_data
from foo.adb.adbCtrl import Adb

adb = Adb(simulator_data)
adb.changeSimulator(user_data)
