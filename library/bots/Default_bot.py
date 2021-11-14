from collections import namedtuple

class Default_bot:
    def __init__(self, db):
        self.name = "Amia(bot)"
        self.__delete_quantity = 100       
        self.__db = db
       
    def __exec_stmts(self, stmts:list):
        results = []
        for stmt in stmts:
            result = self.__db.extract(stmt)
            result = int(result[0][0]) if result else 0
            results.append(result)
        return results

    def get_ark_stats(self):
        ark_stat = namedtuple('ark_stat', ['total', 'total_chars', 'best_dolboeb', 'dolboeb_count'])
        return ark_stat._make(self.__exec_stmts([
            "select value from statistic where parameter_name='ark'",
            "select count(*) from users_ark_collection",
            "select user_id from users_ark_collection where rarity=6 group by user_id order by sum(operator_count) desc limit 1",
            "select sum(operator_count) from users_ark_collection where rarity=6 group by user_id order by sum(operator_count) desc limit 1"
        ]))

    def get_ger_stats(self):
        ger_stat = namedtuple('ger_stat', ['total', 'total_self', 'total_bot', 'total_me'])
        return ger_stat._make(self.__exec_stmts([
            "select value from statistic where parameter_name='ger'",
            "select value from statistic where parameter_name='self_ger'",
            "select value from statistic where parameter_name='ger_bot'",
            "select value from statistic where parameter_name='ger_me'",
        ]))


    @property
    async def server_delete_quantity(self):
        """
        Default message delete quantity getter 

        Returns:
            int: quantity
        """
        return self.__delete_quantity


      