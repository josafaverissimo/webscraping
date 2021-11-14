import utils.database.conf as conf
import pymysql

class Sql:
    def _normalize_args(self, args):
        args_normalized = []

        if isinstance(args, str):
            return f"\'{args}\'"

        for arg in args:
            if isinstance(arg, str):
                args_normalized.append(f"\'{arg}\'")
            else:
                args_normalized.append(arg)

        return tuple(args_normalized)

    def open_connection(self):
        self.connection = pymysql.connect(host=conf.HOST, user=conf.USER, passwd=conf.PASSWORD, db=conf.DB)
        self.cursor = self.connection.cursor()
    
    def close_connection(self):
        self.cursor.connection.commit()
        self.cursor.close()
        self.connection.close()
            
    def execute(self, query, args = None, callback = None):
        if args is not None:
            query = query % self._normalize_args(args)
            
        self._last_query = query
        self._affected_rows = self.cursor.execute(query)

        return callback(self.cursor) if callback != None else self

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def last_insert_id(self):
        query = '''
            select last_insert_id()
        '''

        return self.execute(query).fetchone()[0]

    def get_affect_rows(self):
        return self._affected_rows

    def get_last_query(self):
        return self._last_query
