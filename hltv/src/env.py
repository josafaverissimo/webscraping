from app.utils.env.env import Env
from sys import argv


def set_env(args):
    env = Env()

    env_variables = {}

    for arg in args:
        arg_splited = arg.split('=')
        variable_name = arg_splited[0]
        variable_value = arg_splited[1]

        env.set_variable(variable_name, variable_value)

        env_variables[variable_name] = variable_value

    return env_variables


def get_env(args):
    env = Env()
    variables = env.get_all_variables()

    if len(args) == 0:
        return variables

    return {
        variable_name: variables[variable_name]
        for variable_name in variables if variable_name in args
    }


args = argv[1:]

get_args = [get_arg for get_arg in args if "=" not in get_arg]
set_args = [set_arg for set_arg in args if "=" in set_arg]

env_variables = get_env(get_args)
env_variables_new_values = set_env(set_args)

for env_variable_name in env_variables:
    env_variable = env_variables[env_variable_name]
    value_changed = ""

    if env_variable_name in env_variables_new_values:
        value_changed = f" -> {env_variables_new_values[env_variable_name]}"

    print(f"{env_variable_name}: {env_variable}{value_changed}")
