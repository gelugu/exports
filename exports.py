import re
from os import listdir
from typing import List
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress

import cache
from config import default_rc_file, home_dir, rc_file_regex, key_regex, value_regex
from hints import use_main_hints
from styles import edit_style, hints_style, file_name_style


class Export:
    def __init__(self, line, file_name: str, line_number: int):
        self.key = re.search(rf"export\s({key_regex})=", line).group(1)
        self.value = re.search(rf"export\s{key_regex}=({value_regex})", line).group(1)
        self.file_name = file_name
        self.line_number = line_number


def get_exports() -> List[Export]:
    rc_scripts = [
        f"{home_dir}/{file_name}"
        for file_name in listdir(home_dir)
        if re.search(rc_file_regex, file_name)
    ]

    rc_exports = []
    for rc_script_path in rc_scripts:
        with open(rc_script_path) as rc_script:
            rc_script_lines = rc_script.readlines()
            rc_exports += [
                Export(rc_script_line, rc_script_path, rc_script_lines.index(rc_script_line))
                for rc_script_line in rc_script_lines
                if re.search(r"^export\s", rc_script_line)
            ]
    if len(rc_exports) == 0:
        return [Export("export NEW_ENV=NEW_VALUE", default_rc_file, 0)]

    return rc_exports


def render_exports(layout: Layout, exports: List[Export], active_index: int = 0, edit_key: bool = True):
    edit_style = "blue"
    for export in exports:
        export_layout = layout[f"{export.file_name}_{export.line_number}"]

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
    exports_layout.split(*[Layout(name=f"{export.file_name}_{export.line_number}", size=1) for export in exports])
    for export in exports:
        exports_layout[f"{export.file_name}_{export.line_number}"].split_row(
            Layout(name="key"),
            Layout("=", size=1),
            Layout(name="value"),
            Layout(Text(export.file_name, style="italic", justify="right"))
        )

    layout.split(
        Panel(exports_layout, title="Exports"),
        Layout(hints_panel, name="help", size=3),
        Layout(Layout(), name="debug", size=10),
    )

    return exports_layout


def save_exports(exports: List[Export], live: Live):
    progress = Progress()

    save_task = progress.add_task("[red]Saving...", total=len(exports))
    cache.main_layout["help"].update(Panel(progress))

    index = 0

    for export in exports:
        with open(export.file_name) as file:
            lines = [line.rstrip() for line in file.readlines()]
            lines[export.line_number] = f"export {export.key}={export.value}"
        with open(export.file_name, mode="w") as file:
            file.write("\n".join(lines))
        index += 1
        progress.update(save_task, completed=index)
        live.refresh()

    use_main_hints()
