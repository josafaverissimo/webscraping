from .orm import Orm


class Map(Orm):
    def __init__(self, name=None):
        table_name = 'maps'
        columns = {
            'id': None,
            'name': name
        }

        get_columns = {}
        set_columns = {
            'name': str
        }

        super().__init__(table_name, columns, get_columns, set_columns)
