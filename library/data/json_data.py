from json import load
import os.path as path

path_to_json = "lib/config/config.json"

if not path.isfile(path_to_json):
            exit("'config.json' not found!")

with open(path_to_json,"rb") as json_config_file:
            data = load(json_config_file)
            try:
                pass
            except KeyError:
                exit("'config.json' is damaged!")