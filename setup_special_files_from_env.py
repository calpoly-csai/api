#!/usr/bin/env python3
from os import environ, chmod, listdir
import json
from utilities import yaml_utils  # noqa
import argparse

# =============================================================================
#  GET THE COMMAND LINE ARGUMENTS
# =============================================================================
parser = argparse.ArgumentParser(description="Setup Special Files From Environment.")
parser.add_argument(
    "--overwrite-all",
    action="store_true",
    help="optionally overwrite all the existing files, if exist (default: False).",
)
args = parser.parse_args()
OVERWRITE_ALL = args.overwrite_all


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
# NimbusDatabase stuff
SAMPLE_CONFIG_FILE = "config.json_SAMPLE"
CONFIG_FILE = "config.json"

# PYDRIVE stuff
SAMPLE_PYDRIVE_FILE = "settings.yaml_SAMPLE"
PYDRIVE_FILE = "settings.yaml"
PYDRIVE_FOLDER_ID_FILE = "folder_id.txt"
GOOGLE_DRIVE_FOLDER_ID_FILE = "folder_id.txt"
GOOGLE_DRIVE_FOLDER_ID_KEY = "GOOGLE_DRIVE_FOLDER_ID"
PYDRIVE_CLIENT_ID_KEY = "PYDRIVE_CLIENT_ID"
PYDRIVE_CLIENT_SECRET_KEY = "PYDRIVE_CLIENT_SECRET"
GOOGLE_DRIVE_CREDENTIALS_FILE = "credentials.json"
GOOGLE_DRIVE_CREDENTIALS_KEY = "GOOGLE_DRIVE_CREDENTIALS"
SSH_CERT_FILE = "id_rsa"

# GOOGLE CLOUD stuff
GOOGLE_CLOUD_NLP_CREDENTIALS_FILE = "auth.json"
GOOGLE_CLOUD_NLP_CREDENTIALS_KEY = "GOOGLE_CLOUD_NLP_CREDENTIALS"

SPECIAL_FILES = [
    CONFIG_FILE,
    PYDRIVE_FILE,
    PYDRIVE_FOLDER_ID_FILE,
    GOOGLE_DRIVE_FOLDER_ID_FILE,
    GOOGLE_DRIVE_CREDENTIALS_FILE,
]


# =============================================================================
# SKIP SCRIPT IF FILES EXIST, ELSE CONTINUE
# * optionally provide in `--overwrite-all` flag
# =============================================================================
if OVERWRITE_ALL:
    pass
else:
    for fname in SPECIAL_FILES:
        if fname in listdir():
            print(f"\n\nFOUND a file {fname}\n\n")
            print(
                "\nif you dont care about it, call this script again with `--overwrite-all`\n\n"
            )
            exit(1)


# =============================================================================
# ASSERTIONS
# =============================================================================
BAD_CONFIG_MSG = "uh oh, config vars not set, ask a Nimbus maintainer/admin for help."
assert environ.get("DATABASE_HOSTNAME", None) is not None, BAD_CONFIG_MSG
assert environ.get("DATABASE_PASSWORD", None) is not None, BAD_CONFIG_MSG
assert environ.get("DATABASE_USERNAME", None) is not None, BAD_CONFIG_MSG
assert environ.get("DATABASE_NAME", None) is not None, BAD_CONFIG_MSG
assert environ.get("PYDRIVE_CLIENT_ID", None) is not None, BAD_CONFIG_MSG
assert environ.get("PYDRIVE_CLIENT_SECRET", None) is not None, BAD_CONFIG_MSG
# fmt: off
assert environ.get("GOOGLE_DRIVE_CREDENTIALS", None) is not None, BAD_CONFIG_MSG  # noqa
assert environ.get("GOOGLE_DRIVE_FOLDER_ID", None) is not None, BAD_CONFIG_MSG  # noqa
assert environ.get("GOOGLE_CLOUD_NLP_CREDENTIALS", None) is not None, BAD_CONFIG_MSG  # noqa
assert environ.get("GOOGLE_CLOUD_NLP_MODEL_NAME", None) is not None, BAD_CONFIG_MSG  # noqa
# fmt: on

BAD_CONFIG_MSG_2 = "uh oh, config var is empty string, check docker"
assert environ.get("DATABASE_HOSTNAME", None) != "", BAD_CONFIG_MSG_2
assert environ.get("DATABASE_PASSWORD", None) != "", BAD_CONFIG_MSG_2
assert environ.get("DATABASE_USERNAME", None) != "", BAD_CONFIG_MSG_2
assert environ.get("DATABASE_NAME", None) != "", BAD_CONFIG_MSG_2
assert environ.get("PYDRIVE_CLIENT_ID", None) != "", BAD_CONFIG_MSG_2
assert environ.get("PYDRIVE_CLIENT_SECRET", None) != "", BAD_CONFIG_MSG_2
assert environ.get("GOOGLE_DRIVE_CREDENTIALS", None) != "", BAD_CONFIG_MSG_2
assert environ.get("GOOGLE_DRIVE_FOLDER_ID", None) != "", BAD_CONFIG_MSG_2
assert environ.get("GOOGLE_CLOUD_NLP_CREDENTIALS", None) != "", BAD_CONFIG_MSG_2  # noqa
assert environ.get("GOOGLE_CLOUD_NLP_MODEL_NAME", None) != "", BAD_CONFIG_MSG_2


# =============================================================================
# MAKE THE `config.json` dictionary
# =============================================================================
# This dictionary should look exactly like the `SAMPLE_CONFIG_FILE`
# it contains everything we could possibly neeed
config = {
    "PYDRIVE_CLIENT_ID": environ["PYDRIVE_CLIENT_ID"],
    "PYDRIVE_CLIENT_SECRET": environ["PYDRIVE_CLIENT_SECRET"],
    "GOOGLE_DRIVE_CREDENTIALS": environ["GOOGLE_DRIVE_CREDENTIALS"],
    "GOOGLE_DRIVE_FOLDER_ID": environ["GOOGLE_DRIVE_FOLDER_ID"],
    "GOOGLE_CLOUD_NLP_CREDENTIALS": environ["GOOGLE_CLOUD_NLP_CREDENTIALS"],
    "GOOGLE_CLOUD_NLP_MODEL_NAME": environ["GOOGLE_CLOUD_NLP_MODEL_NAME"],
    "mysql": {
        "host": environ["DATABASE_HOSTNAME"],
        # 3306 is the default port for mysql
        "port": "3306",
        "user": environ["DATABASE_USERNAME"],
        "password": environ["DATABASE_PASSWORD"],
        "database": environ["DATABASE_NAME"],
        "sql_dir": "sql",
        "create_file": "csai_nov_8_2019_create_script.min.sql",
    },
}


# =============================================================================
# save the CONFIG_FILE
# =============================================================================
with open(CONFIG_FILE, "w") as json_file:
    json.dump(config, json_file)


# =============================================================================
# MAKE THE pydrive_yaml dictionary
#
# TODO: consider ENV variable for pydrive's `save_credentials_file`
#       in case the name changes due to conflict with other google credentials
# =============================================================================
pydrive_yaml = {
    "client_config_backend": "settings",
    "client_config": {
        "client_id": config[PYDRIVE_CLIENT_ID_KEY],
        "client_secret": config[PYDRIVE_CLIENT_SECRET_KEY],
    },
    "save_credentials": True,
    "save_credentials_backend": "file",
    "save_credentials_file": "credentials.json",
    "get_refresh_token": True,
    "oauth_scope": [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.install",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.metadata",
    ],
}


# =============================================================================
# save the PYDRIVE_FILE
# =============================================================================
yaml_utils.dump_yaml(pydrive_yaml, PYDRIVE_FILE)


# =============================================================================
# save the GOOGLE_DRIVE_FOLDER_ID_FILE
# =============================================================================
with open(GOOGLE_DRIVE_FOLDER_ID_FILE, "w") as f:
    f.write(config[GOOGLE_DRIVE_FOLDER_ID_KEY])


# =============================================================================
# save the ssh certificates to the correct directory
# =============================================================================
if environ.get("GIT_SSH_CERT") is not None:
    with open(SSH_CERT_FILE, "w") as f:
        f.write(environ["GIT_SSH_CERT"])
        chmod(SSH_CERT_FILE, 0o0600)


# =============================================================================
# save the GOOGLE_DRIVE_CREDENTIALS_FILE
# =============================================================================
with open(GOOGLE_DRIVE_CREDENTIALS_FILE, "w") as credentials_json_file:
    # load the credentials_json from the config dict which has everything
    credentials_json = json.loads(config[GOOGLE_DRIVE_CREDENTIALS_KEY])
    # dump data to credentials_json_file
    json.dump(credentials_json, credentials_json_file)


# =============================================================================
# save the GOOGLE_CLOUD_NLP_CREDENTIALS_FILE
# =============================================================================
with open(GOOGLE_CLOUD_NLP_CREDENTIALS_FILE, "w") as auth_json_file:
    # load the auth_json from the config dict which has everything
    auth_json = json.loads(config[GOOGLE_CLOUD_NLP_CREDENTIALS_KEY])
    # dump data to auth_json_file
    json.dump(auth_json, auth_json_file)
