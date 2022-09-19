import re
from os import listdir
from typing import List
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from config import default_rc_file, key_regex, value_regex, home_dir, rc_file_regex


class Export:
    def __init__(self, line, file_name: str):
        self.key = re.search(rf"export\s({key_regex})=", line).group(1)
        self.value = re.search(rf"export\s{key_regex}=({value_regex})", line).group(1)
        self.file_name = file_name


def get_exports() -> List[Export]:
    rc_scripts = [
        f"{home_dir}/{file_name}"
        for file_name in listdir(home_dir)
        if re.search(rc_file_regex, file_name)
    ]

    rc_exports = []
    for rc_script_path in rc_scripts:
        with open(rc_script_path) as rc_script:
            rc_exports += [
                Export(rc_script_line, rc_script_path)
                for rc_script_line in rc_script.readlines()
                if re.search(r"^export\s", rc_script_line)
            ]
    if len(rc_exports) == 0:
        return [Export("export NEW_ENV=NEW_VALUE", default_rc_file)]

    return rc_exports


def render_exports(layout: Layout, exports: List[Export], active_index: int = 0, edit_key: bool = True):
    edit_style = "blue"
    for export in exports:
        export_layout = layout[f"{exports.index(export)}_{export.key}"]

        export_layout["key"].update(Text(export.key))
        export_layout["value"].update(Text(export.value))
        if active_index == exports.index(export):
            if edit_key:
                export_layout["key"].update(Text(export.key, style=edit_style))
                export_layout["value"].update(Text(export.value))
            else:
                export_layout["key"].update(Text(export.key))
                export_layout["value"].update(Text(export.value, style=edit_style))

        export_layout["key"].size = len(export.key)
        export_layout["value"].size = len(export.value)


def get_export_layout(layout: Layout, exports: List[Export]):
    hints = ["q - quit", "arrows - navigation", "enter - edit"]
    hints_panel = Panel(Text(" | ").join([
        Text(hint, style="on blue")
        for hint in hints
    ]), title="Controls")

    exports_layout = Layout(name="exports")
    exports_layout.split(*[Layout(name=f"{exports.index(export)}_{export.key}", size=1) for export in exports])
    for export in exports:
        exports_layout[f"{exports.index(export)}_{export.key}"].split_row(
            Layout(name="key"),
            Layout("=", size=1),
            Layout(name="value"),
            Layout(Text(export.file_name, style="italic", justify="right"))
        )

    layout.split(
        Panel(exports_layout, title="Exports"),
        Layout(hints_panel, name="help", size=3),
    )

    return exports_layout


def save_exports(exports: List[Export]):
    pass
