import os
from . import helpers
from .env.env import Env


class Appdata:
    def __init__(self, package_name: str, sub_path: str = None):
        env = Env()
        default_filename = None

        if sub_path is not None:
            default_filename = "_".join(sub_path.split("/"))
            sub_path = f"/{sub_path}"
        else:
            sub_path = ""
            default_filename = "_".join(package_name.split('.')[1:])

        self.__appdata_path = env.get_variable('APP_PATH') + '/data'
        self.__work_partial_path = "/".join(package_name.split('.')[1:]) + sub_path
        self.__default_filename = default_filename

        helpers.makedirs_from_path(os.path.join(self.__appdata_path, self.__work_partial_path))

    def __get_work_path(self):
        work_path = self.__appdata_path + "/" + self.__work_partial_path

        return work_path

    def save(self, content, filename: str = None):
        if filename is None:
            filename = self.__default_filename

        work_path = self.__get_work_path()

        file = open(f"{work_path}/{filename}.log", 'a+')
        file.write(content)
        file.write('\n')
