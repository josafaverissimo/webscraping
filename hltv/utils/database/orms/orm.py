from ..connection import Sql
from ...helpers import has_none_value

class Base:
    def __init__(self, table_name, columns, get_columns, set_columns):
        self.__sql = Sql()
        self.__columns = columns
        self.__get_columns = get_columns
        self.__set_columns = set_columns
        self.__table_name = table_name
    
    def get_column(self, column):
        if column not in self.__columns:
            return None

        return self.__columns[column] if column not in self.__get_columns else self.__get_columns[column]()

    def get_columns(self, sub_columns = None):
        if sub_columns is not None:
            return {column: self.get_column(column) for column in sub_columns if column in self.__columns}
            
        return {column: self.get_column(column) for column in self.__columns if column in self.__columns}

    def set_column(self, column, value):
        if(column in self.__set_columns):
            self.__columns[column] = self.__set_columns[column](value)

    def get_all(self, columns_filtered = None):
        columns_filtered = "*" if columns_filtered is None else ', '.join(columns_filtered)

        try:
            self.__sql.open_connection()

            return self.__sql.execute(f'select {columns_filtered} from {self.__table_name}').fetchall()
        finally:
            self.__sql.close_connection()

    def get_by_column(self, column, value, columns_filtered = None):
        columns_filtered = "*" if columns_filtered is None else ', '.join(columns_filtered)

        try:
            self.__sql.open_connection()
            condition = f'{column} = %s'

            return self.__sql.execute(f'select {columns_filtered} from {self.__table_name} where {condition}', value).fetchone()
        finally:
            self.__sql.close_connection()


    def create(self):
        columns_to_save = self.get_columns(self.__set_columns)

        if not has_none_value(columns_to_save):
            columns_to_save_name = ', '.join(list(columns_to_save))
            columns_to_save_values = list(columns_to_save.values())
            params = "%s," * (len(columns_to_save) - 1) + "%s"
            team_id = None
            query = f'insert into {self.__table_name} ({columns_to_save_name}) values ({params})'

            
            try:
                self.__sql.open_connection()

                result = self.__sql.execute(query, columns_to_save_values)

                if not result.failed():
                    team_id = result.last_insert_id()

            finally:
                self.__sql.close_connection()

            if team_id is not None:
                return self.get_by_column('id', team_id)

        return None