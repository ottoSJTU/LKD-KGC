import json

def save_dict_to_file(data_dict, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)

def load_dict_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

