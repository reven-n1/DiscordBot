import sqlite3


class Database(object):
    __DB_LOCATION = "library/data/db/Bot_DB.db"

    def __init__(self) -> None:
        self.__db_connection = sqlite3.connect(self.__DB_LOCATION)
        self.__cursor = self.__db_connection.cursor()
        self.__create_tables()

    def __create_tables(self) -> None:
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS 
        users_ark_collection(user_id TEXT,
                            operator_name TEXT, 
                            rarity INT, 
                            operator_count INT)
                            """)

        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        users_statistic_counter(user_id TEXT,
                            parameter_name TEXT,
                            count INTEGERS,
                            PRIMARY KEY (user_id, parameter_name))
                            """)
        # self.__cursor.execute("""
        # CREATE TABLE IF NOT EXISTS 
        # users_hit_counter(user_id TEXT PRIMARY KEY,
        #                    hit_count INTEGERS) 
        #                     """)
        # self.__cursor.execute("""
        # CREATE TABLE IF NOT EXISTS 
        # users_ger_counter(user_id TEXT PRIMARY KEY,
        #                    ger_count INTEGERS) 
        #                     """)

        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        statistic(parameter_name TEXT PRIMARY KEY,
                           value REAL)
                            """)
        self.__db_connection.commit()

    def alter(self, request: str) -> None:
        self.__cursor.execute(request)
        self.__commit()

    def extract(self, request: str) -> list:
        self.__cursor.execute(request)
        return self.__cursor.fetchall()

    def statistic_increment(self, parameter_name: str):
        self.alter(f"""insert or replace into statistic(parameter_name, value)
        values ('{parameter_name}', ifnull((select value from statistic where parameter_name='{parameter_name}'),0)+1)
        """)

    def user_statistic_increment(self, user_id: int, parameter_name: str):
        self.alter(f"""insert or replace into users_statistic_counter(user_id, parameter_name, count)
        values ({user_id},'{parameter_name}', ifnull((select count from users_statistic_counter where parameter_name='{parameter_name}' and user_id='{user_id}'),0)+1)
        """)

    def __commit(self) -> None:
        self.__db_connection.commit()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} class - responsible for connection and alteration db"

    def __del__(self):
        self.__db_connection.close()
