import json


def read_config_key(key: str, file_path="config.json"):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config.get(key, None)
    except FileNotFoundError:
        print(f"Config file {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Config file {file_path} is invalid.")
        return None
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None


def update_config_file(file_path: str, key: str, value):
    try:
        try:
            with open(file_path, 'r') as file:
                config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        config[key] = value

        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Updated '{key}' in {file_path}")
    except Exception as e:
        print(f"Failed to update config file: {e}")

def get_classroom_id() -> int:
    return read_config_key(key='CLASROOM_ID', file_path='config.json')

def set_classroom(classroom_id: int):
    update_config_file(file_path='config.json', key='CLASROOM_ID', value=classroom_id)

def get_teacher_id() -> int:
    return read_config_key(key='TEACHER_ID', file_path='config.json')

def set_teacher_id(teacher_id: int):
    update_config_file(file_path='config.json', key='TEACHER_ID', value=teacher_id)

def get_start_date() -> str:
    return read_config_key(key='START_DATE', file_path='config.json')

def set_start_date(start_date: str):
    update_config_file(file_path='config.json', key='START_DATE', value=start_date)

def get_mode() -> str:
    return read_config_key(key='MODE', file_path='config.json')

def set_mode(state: str):
    update_config_file(file_path='config.json', key='MODE', value=state)
