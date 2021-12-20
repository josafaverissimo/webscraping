from ..connection import Sql
from ... import helpers


class Orm:
    def __init__(
        self,
        table_name,
        columns,
        get_columns,
        set_columns,
        relationships_by_table_name=None
    ):
        self.__sql = Sql()
        self.__columns = columns
        self.__get_columns = get_columns
        self.__set_columns = set_columns
        self.__table_name = table_name
        self.__relationships_by_table_name = relationships_by_table_name

    @staticmethod
    def get_orms_by_relationships(orms_by_table_name, relationships_by_table_name):
        if orms_by_table_name is None:
            for relationship_name in relationships_by_table_name.copy():
                relationship_orm = relationships_by_table_name[relationship_name]['orm']
                relationships_by_table_name[relationship_name]['orm'] = relationship_orm(
                )

        else:
            for relationship_name in relationships_by_table_name.copy():
                if relationship_name in orms_by_table_name:
                    relationship_orm = orms_by_table_name[relationship_name]
                    relationships_by_table_name[relationship_name]['orm'] = relationship_orm
                else:
                    relationship_orm = relationships_by_table_name[relationship_name]['orm']
                    relationships_by_table_name[relationship_name]['orm'] = relationship_orm(
                    )

        return relationships_by_table_name

    def get_table_name(self):
        return self.__table_name

    def query(self, query, args=None):
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

    def __load(self, columns_values):
        self.__columns = columns_values

    def load_by_column(self, column, value=None):
        columns_values = self.get_by_column(column, value)

        if columns_values is not None:
            self.__load(columns_values)
            return self

        return None

    def get_column(self, column):
        if column not in self.__columns:
            return None

        return self.__columns[column] if column not in self.__get_columns else self.__get_columns[column]()

    def get_columns(self, sub_columns=None):
        if sub_columns is not None:
            return {column: self.get_column(column) for column in sub_columns if column in self.__columns}

        return {column: self.get_column(column) for column in self.__columns if column in self.__columns}

    def set_column(self, column, value):
        if(column in self.__set_columns):
            value = self.__set_columns[column](
                value) if value is not None else None
            self.__columns[column] = value

    def set_columns(self, columns):
        for column, value in columns.items():
            self.set_column(column, value)

    def reset_columns_values(self):
        self.__columns = {column: None for column in self.__columns.copy()}

    def get_all(self, columns_filtered=None):
        columns_filtered = "*" if columns_filtered is None else ', '.join(
            columns_filtered)

        try:
            self.__sql.open_connection()

            return self.__sql.execute(f'select {columns_filtered} from {self.get_table_name()}').fetchall()
        finally:
            self.__sql.close_connection()

    def get_by_column(self, column, value=None, columns_filtered=None):
        columns_filtered = "*" if columns_filtered is None else ', '.join(columns_filtered)
        value = value if value is not None else self.get_column(column)
        result = None

        try:
            self.__sql.open_connection()
            condition = f'{column} = %s'

            result = self.__sql.execute(
                f'select {columns_filtered} from {self.get_table_name()} where {condition}', value
            ).fetchone()
        finally:
            self.__sql.close_connection()

        return result

    def get_by_columns(self, values_by_column: dict, columns_filtered=None):
        for column in values_by_column.copy():
            value = values_by_column[column]

            if value is None:
                values_by_column[column] = self.get_column(column)

        columns_filtered = "*" if columns_filtered is None else ', '.join(columns_filtered)
        columns = [column for column in values_by_column.keys()]
        values = [value for value in values_by_column.values()]
        condition = " and ".join([f'{column} = %s' for column in columns])
        result = None

        try:
            self.__sql.open_connection()

            result = self.__sql.execute(
                f'select {columns_filtered} from {self.get_table_name()} where {condition}', values
            ).fetchone()
        finally:
            self.__sql.close_connection()

        return result

    def create(self):
        columns_to_save = dict(filter(lambda value: value[1] is not None, self.get_columns(self.__set_columns).items()))

        columns_to_save_name = ', '.join(list(columns_to_save))
        columns_to_save_values = list(columns_to_save.values())
        params = "%s," * (len(columns_to_save) - 1) + "%s"
        last_id = None
        query = f'insert into {self.get_table_name()} ({columns_to_save_name}) values ({params})'

        result = self.query(query, columns_to_save_values)

        if result is not None:
            last_id = result['last_insert_id']

            result = self.get_by_column('id', last_id)

            self.__load(result)

        return result

    def update(self, columns=None):
        if columns is not None:
            columns = [
                column for column in columns if column in self.__set_columns]
        else:
            columns = self.__set_columns

        columns_values = [self.get_column(column) for column in columns]
        columns = ' = %s, '.join(columns) + ' = %s'
        affected_rows = None

        if self.__columns['id'] is not None:
            query = f'''
                update {self.get_table_name()}
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
                delete from {self.get_table_name()}
                where id = {self.__columns['id']}
            '''

            affected_rows = None

            result = self.query(query)

            if result is not None:
                return result['affected_rows']

        return None

    def get_relationship(self, relationship_name):
        if relationship_name is not None:
            if relationship_name in self.__relationships_by_table_name:
                return self.__relationships_by_table_name[relationship_name]

        return None

    def set_foreign_key(self, relationship_name, foreign_key):
        if 'name' in foreign_key and 'value' in foreign_key:
            relationship = self.get_relationship(relationship_name)

            if relationship is not None:
                if foreign_key['name'] == relationship['foreign_key']:
                    self.set_column(foreign_key['name'], foreign_key['value'])

        return None

    def set_foreign_key_by_relationship(self, relationship_name, relationship_columns_to_save=None):
        if self.__relationships_by_table_name is not None:
            relationship = self.get_relationship(relationship_name)
            relationship_data = None
            foreign_key = None

            if relationship_columns_to_save is None:
                relationship_data = relationship['orm'].get_columns()
            else:
                relationship['orm'].set_columns(relationship_columns_to_save)

            if relationship['orm'].get_column(relationship['references_key']) is None:
                relationship_data = relationship['orm'].create()

            if relationship_data is not None:
                foreign_key = {
                    'name': relationship['foreign_key'],
                    'value': relationship_data[relationship['references_key']]
                }

                self.set_foreign_key(relationship_name, foreign_key)

            return foreign_key

        return None

    def set_all_foreign_key(self):
        foreign_keys = {}

        for relationship_name in self.__relationships_by_table_name:
            foreign_keys[relationship_name] = self.set_foreign_key_by_relationship(relationship_name)

        return foreign_keys

    def get_relationship_orm(self, relationship_name):
        relationship = self.get_relationship(relationship_name)

        if relationship is not None:
            return relationship['orm']

        return None
