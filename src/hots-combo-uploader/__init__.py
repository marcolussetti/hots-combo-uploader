import configparser

from appdirs import *
from gui import main_window


def main():
    # Load config!
    app_path = user_config_dir("hots-combo-uploader")

    try:
        with open(f"{app_path}/config.ini", "r") as f:
            config = configparser.ConfigParser()
            config.read_file(f)

            for section in ["HOTS"]:
                if section not in config:
                    config[section] = {}
    except:
        config = configparser.ConfigParser()
        config["HOTS"] = {}

    main_window(config, app_path)


if __name__ == "__main__":
    main()
