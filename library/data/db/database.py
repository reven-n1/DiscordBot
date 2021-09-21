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
        users_roll_counter(user_id TEXT,
                           roll_count INTEGERS) 
                            """)

        self.__db_connection.commit()
    
    
    def alter(self, request:str) -> None:
        self.__cursor.execute(request)
        self.__commit()

    
    def extract(self, request:str) -> list:
        self.__cursor.execute(request)
        return self.__cursor.fetchall()


    def __commit(self) -> None:
        self.__db_connection.commit()

    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} class - responsible for connection and alteration db"


    def __del__(self):
        self.__db_connection.close()
