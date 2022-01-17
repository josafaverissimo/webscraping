from datetime import datetime
from ..appdata import Appdata


class Log:
    def __init__(self, package_name):
        path = "/".join(package_name.split('.')[1:])

        self.__log_appdata = Appdata(__package__, path)

    def __get_appdata(self):
        return self.__log_appdata

    def append(self, content):
        appdata = self.__get_appdata()
        content += f" {datetime.today().isoformat()}\n"

        appdata.save(content)
