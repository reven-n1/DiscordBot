from library.my_Exceptions.validator import NonOwnedCharacter, NonExistentCharacter
from library.data.json_data import six_star_chance, five_star_chance, \
four_star_chance, three_star_chance
from random import choice, randrange
from collections import namedtuple
from os.path import abspath
from json import loads
import sqlite3
    
db = sqlite3.connect(abspath("library/data/Bot_DB.db"))
cursor = db.cursor()


class Ark_bot:
    def __init__(self):

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
        cursor.execute(f"""SELECT rarity, operator_name, operator_count FROM users_ark_collection
                           WHERE user_id == '{collection_owner_id}'""")
                           
        requestor_collection = sorted(cursor.fetchall())

        out_list = {}
        if requestor_collection is None:
            return {}
        for character in requestor_collection:
            if character[0] not in out_list.keys(): # filling  the out_list with rarity lists
                out_list[character[0]] = list()
            out_list[character[0]].append(character)

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
        cursor.execute(f"""SELECT rarity, operator_count, operator_name FROM users_ark_collection WHERE user_id == '{author_id}'
                           AND operator_count >= 6 """)

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


    def get_ark_count(self):
        count = 0
        json_data = loads(open("library/config/char_table.json", "rb").read())
        for line in json_data.values():
            if line["rarity"] >= 2  and line["itemDesc"] is not None:
                count += 1
        return count
    

    def roll_random_character(self, author_id):
        """
        Calls function that adds character to db

        Args:
            author_id (message.author.id): requestor id

        Returns:
            list: random character data
        """
        new_character = self.return_new_character(self.get_ark_rarity())
        self.add_ark_to_db(author_id, new_character.name, new_character.rarity)
        return new_character

    
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
    

    def return_new_character(self, rarity):
        """
        Creates list of characters

        Args:
            rarity (int): character rarity

        Returns:
            list: list that contains characters
        """
        choice_list = []
        character_json = open("library/config/char_table.json", "rb")
        characters_data = loads(character_json.read())  # Извлекаем JSON
        
        for character in characters_data:
            character_data = characters_data[str(character)]
            character_rarity = int(character_data["rarity"]) + 1
            if rarity == character_rarity and character_data["itemDesc"] is not None:  # to ignore summoners items and other rarities
                choice_list.append(character)

        random_character = choice(choice_list)

        return self.parse_character_json(random_character, characters_data[str(random_character)])

    
    def parse_character_json(self, character_id, character_data):
            rarity = int(character_data["rarity"]) + 1
            profession = ""
            if character_data["profession"] == "CASTER":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_caster.png"
            elif character_data["profession"] == "SNIPER":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_sniper.png"
            elif character_data["profession"] == "WARRIOR":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_guard.png"
            elif character_data["profession"] == "PIONEER":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_vanguard.png"
            elif character_data["profession"] == "SUPPORT":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_supporter.png"
            elif character_data["profession"] == "MEDIC":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_medic.png"
            elif character_data["profession"] == "SPECIAL":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_specialist.png"
            elif character_data["profession"] == "TANK":
                profession = "https://aceship.github.io/AN-EN-Tags/img/classes/class_defender.png"
            name = character_data["name"].replace(" ", "_").replace("'", "")
            description_first_part = character_data["itemUsage"]
            description_sec_part = character_data["itemDesc"]
            position = character_data["position"]
            tags = ", ".join(character_data["tagList"])
            traits = character_data["description"]
            if rarity == 6:
                stars = self.stars_6
            else:
                stars = self.stars_0_5
            
            character_data_tuple = namedtuple('character', 'character_id name description_first_part description_sec_part position tags \
                    traits profession stars rarity')
            character = character_data_tuple(character_id, name, description_first_part, description_sec_part, position, tags, \
                    traits, profession, stars, rarity)
            
            return character
    

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

    
    def show_character(self, character_name, requestor_id):
        return self.show_character_validator(character_name, requestor_id)  # Извлекаем JSON

    

    def show_character_validator(self, character_name, requestor_id):
        character_json = open("library/config/char_table.json", "rb")
        characters_data = loads(character_json.read())  # Извлекаем JSON

        is_find = False
        for char_id in characters_data:

            name = characters_data[str(char_id)]["name"]
            character_id = char_id

            if character_name == name:
                is_find = True
                break

        if not is_find:
            raise NonExistentCharacter
        
        
        cursor.execute(
            f"SELECT operator_name FROM users_ark_collection WHERE user_id == '{requestor_id}'")
        res = cursor.fetchall()

        is_find = False

        for item in res:
            if character_name in item:
                is_find = True
                break

        if not is_find:
            raise NonOwnedCharacter
        
        return self.parse_character_json(character_id, characters_data[character_id])


    