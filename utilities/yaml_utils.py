import yaml


def load_yaml(filename: str) -> dict:
    """
    Returns the dictionary representation of a given yaml filename

    Args:
        filename: a "filename.yml" string

    Returns:
        dictionary that represents the yaml file

    Raises:
        yaml.YAMLError : if something bad happened
    """
    with open(filename, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise e


def dump_yaml(data: dict, filename: str) -> None:
    """
    Saves the given data into the given yaml filename

    Args:
        filename: a "filename.yml" string
        data; yaml data

    Raises:
        yaml.YAMLError : if something bad happened
    """
    with open(filename, "w") as f:
        try:
            return yaml.safe_dump(data, f)
        except yaml.YAMLError as e:
            raise e
