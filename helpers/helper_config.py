
from configparser import RawConfigParser

parser = RawConfigParser()
parser.read("config.ini")

def get_config_item(category, item):
    config_item=parser[category][item].strip("'").strip('"')
    return config_item
