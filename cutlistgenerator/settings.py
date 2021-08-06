import json


DEFULT_SETTINGS = {
    "Fishbowl_MySQL":
    {
        "auth": {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "gone",
            "password": "fishing",
            "database": "qes"
        }
    },
    "CutList_MySQL":
    {
        "auth": {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "cutlist",
            "password": "Letmein2021",
            "database": "cutlistgenerator"
        }
    }
}


def load_settings(file_path: str) -> dict:
    """Read settings file and return a dictionary with the settings.
        If settings file not found, returns the default settings."""

    try:
        with open(file_path, "r") as f:
            settings = json.loads(f.read())
    except FileNotFoundError:
        settings = DEFULT_SETTINGS
    return settings

def save_settings(file_path: str, settings: dict):
    """Save settings file to disk."""

    with open(file_path, "w") as f:
        f.write(json.dumps(settings))