from json import load, loads
import os.path as path

path_to_json = "library/config/config.json"

if not path.isfile(path_to_json):
            exit("'config.json' not found!")

if not path.isfile("library/config/char_table.json"):
            exit("'char_table.json' not found!")

with open(path_to_json,"rb") as json_config_file:
    
    try:

        data = load(json_config_file)["default_settings"]

        # bot work channels
        bot_channels = data["allowed_channels"]

        # bot statuses
        bot_statuses = ["bot_statuses"]

        # ger chance and phrases, cooldown
        ger_self_chance = int(data["ger"]["self_ger_chance"])
        ger_phrases = data["ger"]["phrase_variants"]
        ger_self_phrases = data["ger"]["self_phrase_variants"]
        ger_cooldown = int(data["ger"]["ger_recoil"])

        # arknights drop chances and cooldown
        six_star_chance = int(data["ark"]["chance"]["six_star"])
        five_star_chance = int(data["ark"]["chance"]["five_star"])
        four_star_chance = int(data["ark"]["chance"]["four_star"])
        three_star_chance = int(data["ark"]["chance"]["three_star"])
        ark_cooldown = int(data["ark"]["ark_recoil"])

        # embed color
        embed_color = int(data["embed_color"],16)

        # for cog load
        cog_list = data["cog_list"]

    except KeyError:
        exit("'config.json' is damaged!")


# character_json = open("library/config/char_table.json", "rb")
# json_data = loads(character_json.read())  # Извлекаем JSON