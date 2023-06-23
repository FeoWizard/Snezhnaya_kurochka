import logging
import sqlite3


class SQLiteWorker():

    def __init__(self, database_path: str, logger: logging.Logger):
        self._conn: sqlite3.Connection = sqlite3.connect(database_path)
        self._logger: logging.Logger = logger


    def db_error_catcher(self, function_to_decorate):
        def wrapper(*args, **kwargs):
            try:
                result = function_to_decorate(*args, **kwargs)
                return result

            except BaseException as err:
                self._logger.error(msg = "DB Error occured!", exc_info = err)
                return None

        return wrapper


    @db_error_catcher
    def execute(self, query: str, args: list = None):
        with self._conn.cursor() as cursor:
            cursor.execute(query, args)


    @db_error_catcher
    def executemany(self, query: str, args: list = None):
        with self._conn.cursor() as cursor:
            cursor.executemany(query, args)


    @db_error_catcher
    def executescript(self, query: str, args: list = None):
        with self._conn.cursor() as cursor:
            cursor.executescript(query, args)


    def close(self):
        self._conn.close()


