import re
from os import listdir
from typing import List
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress

import cache
from config import default_rc_file, home_dir, rc_file_regex, key_regex, value_regex
from hints import use_main_hints
from styles import edit_style, hints_style, file_name_style


class Export:
    def __init__(self, line: str, file_name: str, line_number: int):
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


def get_export_layout(exports: List[Export]):
    exports_layout = Layout(name="exports")
    exports_layout.split(*[Layout(name=f"{export.file_name}_{export.line_number}", size=1) for export in exports])
    for export in exports:
        exports_layout[f"{export.file_name}_{export.line_number}"].split_row(
            Layout(name="key"),
            Layout("=", size=1),
            Layout(name="value"),
            Layout(Text(export.file_name, style=file_name_style, justify="right"))
        )

    cache.main_layout.split(
        Panel(exports_layout, title="Exports"),
        Layout(name="help", size=3),
    )
    use_main_hints()

    return exports_layout


def save_exports(exports: List[Export]):
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

    use_main_hints()


def delete_export(export: Export):
    with open(export.file_name) as file:
        lines = [line.rstrip() for line in file.readlines()]
        lines.remove(lines[export.line_number])
    with open(export.file_name, mode="w") as file:
        file.write("\n".join(lines))
