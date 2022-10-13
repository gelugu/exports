import re
from os import listdir
from typing import List, Tuple
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress

import cache
from classes.Export import Export
from config import default_rc_file, home_dir, rc_file_regex
from hints import use_main_hints, use_add_hints
from input import get_key
from styles import edit_style, file_name_style


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
                if re.search(r"^export\s.*", rc_script_line)
            ]
    if len(rc_exports) == 0:
        return [Export("export NEW_ENV=NEW_VALUE", default_rc_file, 0)]

    return rc_exports


def render_exports(layout: Layout, active_index: int = 0):
    for export in cache.exports:
        export_layout = layout[f"{export.file_name}_{export.line_number}"]

        export_layout["line"].update(Text(export.line))
        if active_index == cache.exports.index(export):
            export_layout["line"].update(Text(export.line, style=edit_style))

        export_layout["line"].size = len(export.line)


def get_export_layout():
    exports_layout = Layout(name="exports")
    exports_layout.split(*[Layout(name=f"{export.file_name}_{export.line_number}", size=1) for export in cache.exports])
    for export in cache.exports:
        exports_layout[f"{export.file_name}_{export.line_number}"].split_row(
            Layout(name="line"),
            Layout(Text(export.file_name, style=file_name_style, justify="right"))
        )

    cache.main_layout.split(
        Panel(exports_layout, title="Exports"),
        Layout(name="new", size=3, visible=False),
        Layout(name="help", size=3),
    )
    use_main_hints()

    return exports_layout


def save_exports(live: Live):
    progress = Progress()

    save_task = progress.add_task("[red]Saving...", total=len(cache.exports))
    cache.main_layout["help"].update(Panel(progress))

    index = 0

    for export in cache.exports:
        with open(export.file_name) as file:
            lines = [line.rstrip() for line in file.readlines()]
            lines[export.line_number] = f"export {export.line}"
        with open(export.file_name, mode="w") as file:
            file.write("\n".join(lines))
        index += 1
        progress.update(save_task, completed=index)
        live.refresh()

    use_main_hints()


def delete_export(export: Export):
    with open(export.file_name) as file:
        lines = [line.rstrip() for line in file.readlines()]
        lines.remove(lines[export.line_number])
    with open(export.file_name, mode="w") as file:
        file.write("\n".join(lines))


def choose_file(exports: List[Export], live: Live) -> str:
    files = list(set([e.file_name for e in exports]))

    choose_file_layout = Layout()

    cache.main_layout["new"].size = len(files) + 2
    cache.main_layout["new"].update(Panel(choose_file_layout, title="Choose file to add"))
    cache.main_layout["new"].visible = True
    use_add_hints()

    index = 0
    while True:
        choose_file_layout.split(*[Layout(Text(file), name=file, size=1) for file in files])
        choose_file_layout[files[index]].update(Text(files[index], style=edit_style))
        live.refresh()

        key = get_key()
        if key.lower() == "q" or key == "esc":
            break

        if key == "up":
            if index <= 0:
                index = len(files) - 1
            else:
                index -= 1
        if key == "down":
            if index >= (len(files) - 1):
                index = 0
            else:
                index += 1
        if key == "return":
            return files[index]

    cache.main_layout["new"].visible = False
    use_main_hints()


def add_export(live: Live) -> Tuple[List[Export], int]:
    file_name = choose_file(cache.exports, live)

    with open(file_name, mode="a") as file:
        file.writelines("\nexport KEY=VALUE")

    with open(file_name) as file:
        line = len(file.readlines())

    new_exports = get_exports()
    return new_exports, new_exports.index(
        [e for e in new_exports if e.line_number == (line - 1) and e.file_name == file_name][0]
    )
