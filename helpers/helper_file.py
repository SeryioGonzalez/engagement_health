from os import listdir
from os.path import isfile, join
import json

def read_json_file(json_file):
    with open(json_file, 'r') as input_json_file:
        json_data = json.load(input_json_file)
        return json_data

def write_list_to_file_in_json(list_to_write, destination_file):
    with open(destination_file, 'w') as f:
        json.dump(list_to_write, f)

def write_list_to_file(list_to_write, destination_file):
    with open(destination_file, 'w') as f:
        f.writelines("%s\n" % item for item in list_to_write)

def read_lines_as_list_from_json_file(source_file):
    with open(source_file) as f:
        parsed_lines_json = json.load(f)
        
        return parsed_lines_json

def read_lines_as_list_from_file(source_file):
    with open(source_file) as f:
        parsed_lines = f.readlines()
        
        return parsed_lines

def get_file_paths_in_folder(folder):
    file_paths = [join(folder, one_file) for one_file in listdir(folder) if isfile(join(folder, one_file))]
    file_paths.sort()
    return file_paths