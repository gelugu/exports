from os import environ

home_dir = environ["HOME"]

default_rc_file = f"{home_dir}/.bashrc"
# rc_file_regex = r"\..*rc^"
rc_file_regex = r"temprc"
rc_export_section_start = "### Exports ###"
rc_export_section_end = "### End of exports ###"

key_regex = r".*"
value_regex = r".*"
