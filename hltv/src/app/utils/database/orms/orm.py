from ..connection import Sql
from ...helpers import has_none_value

class Base:
    def __init__(self, table_name, columns, get_columns, set_columns):
        self.__sql = Sql()
        self.__columns = columns
        self.__get_columns = get_columns
        self.__set_columns = set_columns
        self._table_name = table_name

    def query(self, query, args = None):
        result = None
        query_metadata = None
        
        try:
            self.__sql.open_connection()

            result = self.__sql.execute(query, args)
        finally:
            if not result.failed():
                query_metadata = {
                    'affected_rows': result.get_affect_rows(),
                    'last_insert_id': result.last_insert_id()
                }
                result.commit()
            else:
                result.rollback()

            self.__sql.close_connection()

        return query_metadata

    def load_by_column(self, column, value):
        team = self.get_by_column(column, value)

        if team is not None:
            self.__columns = team
            return self

        return None
    
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
            value = self.__set_columns[column](value) if value is not None else None
            self.__columns[column] = value

    def set_columns(self, columns):
        for column, value in columns.items():
            self.set_column(column, value)

    def reset_columns_values(self):
        columns = {column: None for column in self.__set_columns}

        self.set_columns(columns)

    def get_all(self, columns_filtered = None):
        columns_filtered = "*" if columns_filtered is None else ', '.join(columns_filtered)

        try:
            self.__sql.open_connection()

            return self.__sql.execute(f'select {columns_filtered} from {self._table_name}').fetchall()
        finally:
            self.__sql.close_connection()

    def get_by_column(self, column, value, columns_filtered = None):
        columns_filtered = "*" if columns_filtered is None else ', '.join(columns_filtered)

        try:
            self.__sql.open_connection()
            condition = f'{column} = %s'

            return self.__sql.execute(f'select {columns_filtered} from {self._table_name} where {condition}', value).fetchone()
        finally:
            self.__sql.close_connection()

    def create(self):
        columns_to_save = self.get_columns(self.__set_columns)

        if not has_none_value(columns_to_save):
            columns_to_save_name = ', '.join(list(columns_to_save))
            columns_to_save_values = list(columns_to_save.values())
            params = "%s," * (len(columns_to_save) - 1) + "%s"
            last_id = None
            query = f'insert into {self._table_name} ({columns_to_save_name}) values ({params})'

            result = self.query(query, columns_to_save_values)

            if result is not None:
                last_id = result['last_insert_id']

                return self.get_by_column('id', last_id)

    def update(self, columns = None):
        if columns is not None:
            columns = [column for column in columns if column in self.__set_columns]
        else:
            columns = self.__set_columns

        columns_values = [self.get_column(column) for column in columns]
        columns = ' = %s, '.join(columns) + ' = %s'
        affected_rows = None

        if self.__columns['id'] is not None:
            query = f'''
                update {self._table_name}
                set {columns}
                where id = {self.__columns['id']}
            '''

            result = self.query(query, columns_values)

            if result is not None:
                return result['affected_rows']

            return None

    def delete(self):
        if self.__columns['id'] is not None:
            query = f'''
                delete from {self._table_name}
                where id = {self.__columns['id']}
            '''

            affected_rows = None

            result = self.query(query)

            if result is not None:
                return result['affected_rows']


        return None

