from .orm import Base

class Map(Base):
    def __init__(self, name = None):
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
