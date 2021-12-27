from app.utils.env.env import Env
from sys import argv

env: Env = Env()

args = {}

for arg in argv[1:]:
    arg_splited = arg.split('=')
    variable_name = arg_splited[0]
    variable_value = arg_splited[1]

    args[variable_name] = variable_value

for variable_name in args:
    variable_value = args[variable_name]

    env.set_variable(variable_name, variable_value)
