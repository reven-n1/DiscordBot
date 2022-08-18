from json import load
import os.path as path


class DataHandler():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataHandler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not getattr(cls, '_instance', None):
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        __path_to_json = "library/config/config.json"

        if not path.isfile(__path_to_json):
            exit("'config.json' not found!")

        if not path.isfile("library/config/character_table.json"):
            exit("'character_table.json' not found!")

        if not path.isfile("library/config/skin_table.json"):
            exit("'skin_table.json' not found!")

        with open(__path_to_json, "rb") as json_config_file:
            try:
                self.__data = load(json_config_file)["default_settings"]
                self.__database_config = self.__data['database']
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
                self.__chat_misc_cooldown = int(self.__data["chat_misc_cooldown"])
                self.__chat_misc_cooldown_sec = self.__chat_misc_cooldown/10

                # command prefix
                self.__prefix = self.__data["prefix"]

            except KeyError:
                exit("'config.json' is damaged!")

    @property
    def get_database_config(self) -> dict:
        return self.__database_config

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

    @property
    def get_prefix(self):
        return self.__prefix

    @property
    def get_chat_misc_cooldown(self):
        return self.__chat_misc_cooldown

    @property
    def get_chat_misc_cooldown_sec(self):
        return self.__chat_misc_cooldown_sec

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} class - responsible for loading data and it issuance"