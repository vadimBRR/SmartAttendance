import json


def read_config_key(file_path: str, key: str):
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