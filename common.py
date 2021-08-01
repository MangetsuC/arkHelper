from foo.configParser.tomlParser import configToml, simulatorToml
from foo.ui.theme import Theme


user_data = configToml()
simulator_data = simulatorToml()

theme = Theme(user_data, True)