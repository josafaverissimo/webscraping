from .db_configs import default_config
import pymysql

class Sql:
    def _normalize_args(self, args):
        args_normalized = []

        if isinstance(args, str):
            return f"\'{args}\'"

        if isinstance(args, int):
            return args

        for arg in args:
            if isinstance(arg, str):
                args_normalized.append(f"\'{arg}\'")
            else:
                args_normalized.append(arg)

        return tuple(args_normalized)

    def open_connection(self):
        self.connection = pymysql.connect(host=default_config['host'], user=default_config['user'], passwd=default_config['password'], db=default_config['db'])
        self.cursor = self.connection.cursor()
        self.__error_log = None
    
    def close_connection(self):
        self.cursor.connection.commit()
        self.cursor.close()
        self.connection.close()
            
    def execute(self, query, args = None, callback = None):
        if args is not None:
            query = query % self._normalize_args(args)
            
        self._last_query = query

        try:
            self._affected_rows = self.cursor.execute(query)
        except pymysql.err.MySQLError as e:
            self.__error_log = f'\n[{e.args[0]}]\n\t{e.args[1]}\n\n[Last query]\n\t{query}\n'
            self.failed()
        finally:
            return self
    
    def failed(self, show_log = True):
        if self.__error_log is None:
            return False

        if show_log:
            print(self.__error_log)

        return True

    def fetchall(self):
        if(not self.failed()):
            return self.cursor.fetchall()

        return None

    def fetchone(self):
        if(not self.failed()):
            return self.cursor.fetchone()

        return None

    def last_insert_id(self):
        query = '''
            select last_insert_id()
        '''

        return self.execute(query).fetchone()[0]

    def get_affect_rows(self):
        return self._affected_rows

    def get_last_query(self):
        return self._last_query
