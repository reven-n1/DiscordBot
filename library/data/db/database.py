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
                            operator_count INT,
                            PRIMARY KEY (user_id, operator_name))
                            """)

        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        statistic_parameters(id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE)
                            """)

        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        users_statistic_counter(user_id TEXT,
                            parameter_id INTEGER,
                            count INTEGER,
                            PRIMARY KEY (user_id, parameter_id),
                            FOREIGN KEY(parameter_id) REFERENCES statistic_parameters(id)
                            )
                            """)

        self.__cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_statistic_parameter
        ON users_statistic_counter (parameter_id);
        """)

        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS
        statistic(parameter_name TEXT PRIMARY KEY,
                           value REAL)
                            """)
        self.__db_connection.commit()

    def alter(self, request: str, *args, **kwargs) -> int:
        inserted_id = self.__cursor.execute(request, args if args else kwargs).lastrowid
        self.__commit()
        return inserted_id

    def extract(self, request: str, *args, **kwargs) -> list:
        self.__cursor.execute(request, args if args else kwargs)
        return self.__cursor.fetchall()

    def statistic_increment(self, parameter_name: str):
        self.alter("""insert or replace into statistic(parameter_name, value)
        values (?, ifnull((select value from statistic where parameter_name=?),0)+1)
        """, parameter_name, parameter_name)

    def get_parameter_id(self, parameter_name: str) -> int:
        id = self.extract("select id from statistic_parameters where name=?", parameter_name)
        if not id:
            id = self.alter("INSERT OR IGNORE INTO statistic_parameters(name) VALUES(?)", parameter_name)
        else:
            id = id[0][0]
        return id

    def user_statistic_increment(self, user_id: int, parameter_name: str):
        id = self.get_parameter_id(parameter_name)
        self.alter(f"""insert or replace into users_statistic_counter(user_id, parameter_id, count)
        values (:uid,:pid, ifnull((select count from users_statistic_counter where parameter_id=:pid and user_id=:uid),0)+1)
        """, uid=user_id, pid=id)

    def get_user_statistics(self, parameter_name: str, limit=5):
        return self.extract("""select user_id, count from users_statistic_counter stats
                    join statistic_parameters params on params.id=stats.parameter_id
                    where params.name=? order by count desc limit ?""", parameter_name, limit)

    def get_user_statistic(self, user_id: int, parameter_name: str):
        return self.extract("""select count from users_statistic_counter stats
                    join statistic_parameters params on params.id=stats.parameter_id
                    where user_id=? and params.name=?""", user_id, parameter_name)

    def reset_statistic_for_user(self, user_id: int, parameter_name: str):
        id = self.get_parameter_id(parameter_name)
        self.alter("update users_statistic_counter set count=0 where user_id=? and parameter_id=?", user_id, id)

    @property
    def user_statistic_types(self) -> list[str]:
        return [str(x[0]) for x in self.extract("select name from statistic_parameters")]

    def __commit(self) -> None:
        self.__db_connection.commit()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} class - responsible for connection and alteration db"

    def __del__(self):
        self.__db_connection.close()
