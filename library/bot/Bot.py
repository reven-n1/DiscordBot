from random import randint, choice, randrange
from json import loads, load
from os.path import abspath
import sqlite3
    
db = sqlite3.connect(abspath("library/data/Bot_DB.db"))
cursor = db.cursor()


class Bot:
    def __init__(self):
        try:
            with open(abspath("library/config/config.json"),"rb") as json_config_file:
                data = load(json_config_file)["default_settings"]

                self.bot_channels = data["allowed_channels"]

                self.ger_self_chance = int(data["ger"]["self_ger_chance"])
                self.ger_phrases = data["ger"]["phrase_variants"]
                self.ger_self_phrases = data["ger"]["phrase_variants"]
        
                self.six_star_chance = int(data["ark"]["chance"]["six_star"])
                self.five_star_chance = int(data["ark"]["chance"]["five_star"])
                self.four_star_chance = int(data["ark"]["chance"]["four_star"])
                self.three_star_chance = int(data["ark"]["chance"]["three_star"])

        except Exception as e:
            print("'config.json' is damaged or lost")
            print(e)

        self.name = "Amia(bot)"
        self.delete_quantity = 100       
        self.stars_0_5 = "<:star:801095671720968203>"
        self.stars_6 = "<:star2:801105195958140928>"
        self.bot_info = {"info": ' хуйня никому не нужная(бот тупой, но перспективный(нет))',
                         'commands': {'!ger или !пук': 'Смачный пердеж кому-нибудь куда-нибудь..',
                                      '!myark или !майарк': 'Все полученые персонажи',
                                      '!ark или !арк': 'Рол персонажа',
                                      '!clear': 'Удаляет последние 100 сообщений(или число указанное после команды)'}}
        self.bot_commands = ['!ger', '!пук', '!арк', '!ark', '!clear', '!members', '!commands']


    def get_info(self):
        """
        Returns info list
        """

        info_list = []
        count = 0
        for line in self.bot_info["commands"].keys():
            info_list.append(f'{line} - ')
        for line in self.bot_info["commands"].values():
            info_list[count] += line
            count += 1

        return info_list


    @property
    async def server_delete_quantity(self):
        """
        Default message delete quantity getter 

        Returns:
            int: quantity
        """
        return self.delete_quantity


    def get_commands(self):
        """
        Print all bot commands
        """
        out_str = ""
        for key, values in self.bot_info["commands"].items():
            out_str += f'{key} - {values}\n'
        return out_str


    def get_ark_collection(self, collection_owner_id):
        """
        This function returns all ark collection

        Args:
            collection_owner_id (message.autthor.id): requestor id

        Returns:
            list: requestor characters collection 
        """
        cursor.execute(f"SELECT rarity, operator_name, operator_count FROM users_ark_collection "
                       f"WHERE user_id == '{collection_owner_id}'")
        res = sorted(cursor.fetchall())
        out_list = []
        prev_rar = 2
        for item in res:
            if prev_rar < item[0]:
                out_list.append("")
                out_list.append(f"{self.stars_0_5 * item[0]}")
            elif prev_rar < item[0] == 6:
                out_list.append("")
                out_list.append(f"{self.stars_6 * item[0]}")

            out_list.append(f"{item[1]} x{item[2]}")
            prev_rar = item[0]
        return out_list


    def ger_function(self, message_author, random_member):
        """
        Farts on random server member or whoever called it

        Args:
            message_author (message.author.id): requestor id
            random_member (guild.member): random guild member

        Returns:
            str: string with fart phrase
        """
        
        if randint(0, 101) >= self.ger_self_chance:  # Chance to обосраться

            return (f"{message_author.mention} "
                    f"{choice(self.ger_phrases)} {random_member.mention}")
        else:
            return f"{message_author.mention} {choice(self.ger_self_phrases)}"  # Самообсер



    @staticmethod
    def get_barter_list(author_id):
        """
        Creates list of characters for barter

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: list that contains quantity and character stars
        """
        cursor.execute(
            f"SELECT rarity, operator_count, operator_name FROM users_ark_collection WHERE user_id == '{author_id}'"
            f" AND operator_count > 5 ")
        res = sorted(cursor.fetchall())
        barter_list = []
        for rarity, count, name in res:
            if rarity < 6:
                barter_list.append([rarity + 1, count // 5])
            new_count = count % 5
            if new_count == 0:
                cursor.execute(
                    f"DELETE FROM users_ark_collection WHERE user_id == '{author_id}' AND operator_count >= 5 ")
            else:
                cursor.execute(f"UPDATE users_ark_collection SET operator_count = '{new_count}'"
                               f"WHERE user_id ='{author_id}'AND operator_name == '{name}'")
            db.commit()
        return barter_list


    def ark_barter(self, barter_list, author_id):
        """
        Exchanges characters and calls function to add them to db

        Args:
            barter_list (list): list that contains quantity and character stars
            author_id ([type]): requestor id

        Yields:
            str: random character
        """

        for operators in barter_list:
            for _ in range(0, operators[1]):
                choice_list = self.return_choice_list(operators[0])
                random_choice = choice(list(choice_list.values()))
                self.add_ark_to_db(author_id, random_choice)
                yield random_choice


    def return_choice_list(self, rarity):
        """
        Creates list of characters

        Args:
            rarity (int): character rarity

        Returns:
            list: list that contains characters
        """
        choice_list = {}
        file = open("library/config/char_table.json", "rb")
        json_data = loads(file.read())  # Извлекаем JSON
        for line in json_data:
            tmp = json_data[str(line)]
            json_rarity = int(tmp["rarity"]) + 1
            if rarity == json_rarity and tmp["itemDesc"] is not None:  # to ignore magalan skills and other rarities
                profession = ""
                if tmp["profession"] == "CASTER":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_caster.png"
                elif tmp["profession"] == "SNIPER":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_sniper.png"
                elif tmp["profession"] == "WARRIOR":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_guard.png"
                elif tmp["profession"] == "PIONEER":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_vanguard.png"
                elif tmp["profession"] == "SUPPORT":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_supporter.png"
                elif tmp["profession"] == "MEDIC":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_medic.png"
                elif tmp["profession"] == "SPECIAL":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_specialist.png"
                elif tmp["profession"] == "TANK":
                    profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_defender.png"
                character_id = line
                name = tmp["name"].replace(" ", "_").replace("'", "")
                description_first_part = tmp["itemUsage"]
                description_sec_part = tmp["itemDesc"]
                position = tmp["position"]
                tags = ", ".join(tmp["tagList"])
                traits = tmp["description"]
                if json_rarity == 6:
                    stars = self.stars_6
                else:
                    stars = self.stars_0_5
                choice_list[name] = character_id, name, description_first_part, description_sec_part, position, tags, \
                                    traits, profession, stars, json_rarity

        file.close()
        return choice_list


    def get_ark_rarity(self):
        """
        Returns random character rarity
        """

        rarity = randrange(0, 100000)
        if rarity <= self.six_star_chance * 1000:
            return 6
        elif rarity <= self.five_star_chance * 1000:
            return 5
        elif rarity <= self.four_star_chance * 1000:
            return 4
        elif rarity <= self.three_star_chance * 1000:
            return 3


    def get_ark(self, author_id):
        """
        Calls function that adds character to db

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: list of characters
        """
        choice_list = self.return_choice_list(self.get_ark_rarity())
        rand_item_from_list = choice(list(choice_list.values()))
        self.add_ark_to_db(author_id, rand_item_from_list[1], rand_item_from_list[9])
        return rand_item_from_list


    @staticmethod
    def add_ark_to_db(author_id, character_name, character_rarity):
        """
        Adds record to db

        Args:
            author_id (message.author.id): requestor id
            character_name (str): received character name
            character_rarity (int): received chaaracter rarity
        """

        cursor.execute(
            f"SELECT operator_count FROM users_ark_collection WHERE user_id == '{author_id}' "
            f"AND operator_name == '{character_name}'")
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f"INSERT INTO users_ark_collection  VALUES (?,?,?,?)",
                           (f"{author_id}", character_name, character_rarity, 1))
        else:
            cursor.execute(f"UPDATE users_ark_collection SET operator_count = '{res[0] + 1}'"
                           f"WHERE user_id ='{author_id}'AND operator_name == '{character_name}'")
        db.commit()
