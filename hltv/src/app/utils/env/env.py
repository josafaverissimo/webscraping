class Env:
    def __init__(self):
        self.__env_path = f'{"/".join(__file__.split("/")[:-1])}/.env'
        self.__variables = {}

        env_file = open(self.__env_path, 'a+')

        for line in env_file.readlines():
            line_splited = line.split('=')

            variable = {
                'name': line_splited[0],
                'value': line_splited[1]
            }

            self.__variables[variable['name']] = variable['value']

    def get_variable(self, name):
        return self.__variables[name]

    def set_variable(self, name, value):
        self.__variables[name] = value

        env_file = open(self.__env_path, 'a+')
        env_file.write(f"{name}={value}\n")
