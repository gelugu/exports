from os import environ

home_dir = environ["HOME"]

default_rc_file = f"{home_dir}/.bashrc"
rc_file_regex = r"\..*rc_"

key_regex = r".*"
value_regex = r".*"
