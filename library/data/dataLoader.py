from json import load
import os.path as path
from random import choice


class dataHandler():
    def __init__(self) -> None:
        __path_to_json = "library/config/config.json"

        if not path.isfile(__path_to_json):
                    exit("'config.json' not found!")

        if not path.isfile("library/config/char_table.json"):
                    exit("'char_table.json' not found!")


        with open(__path_to_json,"rb") as json_config_file:  
            try:
                self.__data = load(json_config_file)["default_settings"]

                # bot work channels
                self.__bot_channels = self.__data["allowed_channels"]

                # bot statuses
                self.__bot_statuses = self.__data["bot_statuses"]

                # ger chance and phrases, cooldown
                self.__ger_self_chance = int(self.__data["ger"]["self_ger_chance"])
                self.__ger_phrases = self.__data["ger"]["phrase_variants"]
                self.__ger_self_phrases = self.__data["ger"]["self_phrase_variants"]
                self.__ger_cooldown = int(self.__data["ger"]["ger_cooldown"])

                # arknights drop chances and cooldown
                self.__six_star_chance = int(self.__data["ark"]["chance"]["six_star"])
                self.__five_star_chance = int(self.__data["ark"]["chance"]["five_star"])
                self.__four_star_chance = int(self.__data["ark"]["chance"]["four_star"])
                self.__three_star_chance = int(self.__data["ark"]["chance"]["three_star"])
                self.__ark_cooldown = int(self.__data["ark"]["ark_cooldown"])

                # arknights professions
                self.__ark_professions = {
                    "CASTER": "https://aceship.github.io/AN-EN-Tags/img/classes/class_caster.png",
                    "SNIPER": "https://aceship.github.io/AN-EN-Tags/img/classes/class_sniper.png",
                    "WARRIOR": "https://aceship.github.io/AN-EN-Tags/img/classes/class_guard.png",
                    "PIONEER": "https://aceship.github.io/AN-EN-Tags/img/classes/class_vanguard.png",
                    "SUPPORT": "https://aceship.github.io/AN-EN-Tags/img/classes/class_supporter.png",
                    "MEDIC": "https://aceship.github.io/AN-EN-Tags/img/classes/class_medic.png",
                    "SPECIAL": "https://aceship.github.io/AN-EN-Tags/img/classes/class_specialist.png",
                    "TANK": "https://aceship.github.io/AN-EN-Tags/img/classes/class_defender.png",
                }

                # embed color
                self.__embed_color = int(self.__data["embed_color"], 16)

                # for cog load
                self.__cog_list = self.__data["cog_list"]

                # delete mess delay / delete after
                self.__delete_delay = self.__data["delete_delay"]
                self.__delete_after = self.__data["delete_after"]

                # command prefix
                self.__prefix = self.__data["prefix"]

            except KeyError:
                exit("'config.json' is damaged!")
    
    
    @property
    def get_available_channels(self):
        return self.__bot_channels
    

    @property
    def get_self_ger_chanse(self):
        return self.__ger_self_chance


    @property
    def get_ger_phrases(self):
        return self.__ger_phrases

    
    @property
    def get_ger_self_phrases(self):
        return self.__ger_self_phrases


    @property
    def get_ger_cooldown(self):
        return self.__ger_cooldown


    @property
    def get_ark_cooldown(self):
        return self.__ark_cooldown


    @property
    def get_embed_color(self):
        return self.__embed_color


    @property
    def get_cog_list(self):
        return self.__cog_list
    

    def get_ark_profession(self, prof):
        return self.__ark_professions[prof]
    

    @property
    def get_ark_chances(self):
        return self.__six_star_chance, self.__five_star_chance, self.__four_star_chance, self.__three_star_chance
    

    @property
    def get_del_delay(self):
        return self.__delete_delay
    

    @property
    def get_del_after(self):
        return self.__delete_after
    

    def get_bot_status(self, category):
        return choice(self.__bot_statuses[f"{category}"])
    
    @property
    def get_prefix(self):
        return self.__prefix


    def __repr__(self) -> str:
        return f"{self.__class__.__name__} class - responsible for loading data and it issuance"