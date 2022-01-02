import os
from . import helpers
from .env.env import Env


class Appdata:
    def __init__(self, package_name: str):
        env = Env()

        self.__appdata_path = env.get_variable('APP_PATH') + '/data'
        self.__work_path = "/".join(package_name.split('.')[1:])
        helpers.makedirs_from_path(os.path.join(self.__appdata_path, self.__work_path))

    def __get_appdata_path(self):
        return self.__appdata_path
