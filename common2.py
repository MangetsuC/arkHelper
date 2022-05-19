from os import getcwd

from common import simulator_data, user_data
from foo.adb.adbCtrl import Adb, Cmd

adb = Adb(simulator_data)
adb.changeSimulator(user_data)

version = Cmd(getcwd()).getVersion()
