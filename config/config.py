import os

from configloader import ConfigLoader


ENVIRONMENT = os.environ['ENVIRONMENT'].upper()
CONFIG_FILE_PATH: str = f'./config/{ENVIRONMENT.lower()}.yml'

app_config = ConfigLoader()
app_config.update_from_yaml_file(file_path_or_obj=CONFIG_FILE_PATH)

