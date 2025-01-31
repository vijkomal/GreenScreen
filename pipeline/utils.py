import json


def load_json(file_path):
    """
    Load JSON data from a file.

    :param file_path: Path to the JSON file.
    :return: Data loaded from the JSON file.
    """
    with open(file_path, "r") as file:
        return json.load(file)


def save_json(data, file_path):
    """
    Save data to a JSON file.

    :param data: Data to be saved.
    :param file_path: Path to the JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
