from os import error
from library.data.json_data import six_star_chance, five_star_chance, \
four_star_chance, three_star_chance #, character_json
from random import choice, randrange
from os.path import abspath
from json import loads
import sqlite3
    
db = sqlite3.connect(abspath("library/data/Bot_DB.db"))
cursor = db.cursor()


class Ark_bot:
    def __init__(self):
        # self.characters_data = character_json
      
        self.six_star_chance = six_star_chance
        self.five_star_chance = five_star_chance
        self.four_star_chance = four_star_chance
        self.three_star_chance = three_star_chance
        
        self.stars_0_5 = "<:star:801095671720968203>"
        self.stars_6 = "<:star2:801105195958140928>"


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
        out_list = {}
        if res is None:
            return {}
        for item in res:
            if item[0] not in out_list.keys():
                out_list[item[0]] = list()
            out_list[item[0]].append(item)

        return out_list



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
            f" AND operator_count >= 6 ")
        res = sorted(cursor.fetchall())
        barter_list = []
        for rarity, count, _ in res:
            if rarity < 6 and count > 5:
                if count % 5 != 0:
                    new_char_quantity = count % 5
                elif count % 5 == 0:
                    new_char_quantity = (count // 5) - 1
                else:
                    pass
                
                barter_list.append([rarity + 1, new_char_quantity])

                cursor.execute(f"""UPDATE users_ark_collection SET operator_count = 
                                CASE 
                                    WHEN operator_count % 5 != 0  THEN operator_count % 5 
                                    WHEN operator_count  % 5 == 0 THEN 5
                                    ELSE operator_count
                                END
                                WHERE rarity < 6 AND operator_count > 5 AND user_id ='{author_id}'""")
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
                self.add_ark_to_db(author_id, random_choice[1], random_choice[9])
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
        character_json = open("library/config/char_table.json", "rb")
        json_data = loads(character_json.read())  # Извлекаем JSON
        
        #for line in self.characters_data:
        for line in json_data:
            # tmp = self.characters_data[str(line)]
            tmp = json_data[str(line)]
            json_rarity = int(tmp["rarity"]) + 1
            if rarity == json_rarity and tmp["itemDesc"] is not None:  # to ignore magalan skills and other rarities
                character = self.parse_character_json(line, tmp)
                choice_list[character[1]] = character

        return choice_list


    def parse_character_json(self, character_id, character):
            json_rarity = int(character["rarity"]) + 1
            profession = ""
            if character["profession"] == "CASTER":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_caster.png"
            elif character["profession"] == "SNIPER":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_sniper.png"
            elif character["profession"] == "WARRIOR":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_guard.png"
            elif character["profession"] == "PIONEER":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_vanguard.png"
            elif character["profession"] == "SUPPORT":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_supporter.png"
            elif character["profession"] == "MEDIC":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_medic.png"
            elif character["profession"] == "SPECIAL":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_specialist.png"
            elif character["profession"] == "TANK":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_defender.png"
            character_id = character_id
            name = character["name"].replace(" ", "_").replace("'", "")
            description_first_part = character["itemUsage"]
            description_sec_part = character["itemDesc"]
            position = character["position"]
            tags = ", ".join(character["tagList"])
            traits = character["description"]
            if json_rarity == 6:
                stars = self.stars_6
            else:
                stars = self.stars_0_5
            return [character_id, name, description_first_part, description_sec_part, position, tags, \
                    traits, profession, stars, json_rarity]


    def get_ark_count(self):
        count = 0
        json_data = loads(open("library/config/char_table.json", "rb").read())
        for line in json_data.values():
            if line["rarity"] >= 2  and line["itemDesc"] is not None:
                count += 1
        return count
        # character_json = open("library/config/char_table.json", "rb")
        # json_data = loads(character_json.read())  # Извлекаем JSON
        # return len(json_data)

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


    def roll_random_character(self, author_id):
        """
        Calls function that adds character to db

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: random character data
        """
        choice_list = self.return_choice_list(self.get_ark_rarity())
        rand_item_from_list = choice(list(choice_list.values()))
        self.add_ark_to_db(author_id, rand_item_from_list[1], rand_item_from_list[9])
        return rand_item_from_list
    
    def get_character_data(self, character_name : str):
        """
        Get character data from DB by it's name

        Args:
            character_name: character name to look for

        Returns:
            list: random character data
        """
        character_json = open("library/config/char_table.json", "rb")
        json_data = loads(character_json.read())
        for char_data in json_data.values():
            if char_data["name"].lower() == character_name.lower():
                return char_data
        raise KeyError("Selected character not found in list")


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