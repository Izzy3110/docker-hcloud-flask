import yaml


def load_config(file_path):
    with open(file_path) as file:
        config = yaml.safe_load(file)
    return config
