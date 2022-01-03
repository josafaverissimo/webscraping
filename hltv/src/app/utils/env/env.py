import os


class Env:
    def __init__(self):
        self.__env_path = os.path.dirname(__file__) + '/.env'
        self.__variables = {}
        env_file = None

        if not os.path.isfile(self.__env_path):
            env_file = open(self.__env_path, 'w+')
        else:
            env_file = open(self.__env_path, 'r')

        for line in env_file.readlines():
            line_splited = line.split('=')

            name = line_splited[0].replace('\n', '')
            value = line_splited[1].replace('\n', '')

            self.__variables[name] = value

    def get_variable(self, name):
        return self.__variables[name]

    def get_all_variables(self):
        return self.__variables

    def set_variable(self, name, value):
        has_variable = name in self.__variables
        self.__variables[name] = value

        if has_variable:
            env_file = open(self.__env_path, 'w')
            env_variables = "\n".join([
                f"{env_variable_name}={self.__variables[env_variable_name]}"
                for env_variable_name in self.__variables
            ]) + "\n"

            env_file.writelines(env_variables)

        else:
            env_file = open(self.__env_path, 'a+')
            env_file.write(f"{name}={value}\n")
