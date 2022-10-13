from rich.panel import Panel
from rich.text import Text

from cache import main_layout
from styles import hints_style

hints_panel_name = "Controls"
hints_divider = " | "
main_hints = ["q - quit", "arrows - navigation", "enter - edit", "a - add new", "d - delete"]
add_hints = ["q, esc - quit", "arrows - navigation", "enter - choose"]
edit_hints = ["enter, esc - finish"]


def use_main_hints():
    main_layout["help"].update(Panel(Text(hints_divider).join([
        Text(hint, style=hints_style)
        for hint in main_hints
    ]), title=hints_panel_name))


def use_edit_hints():
    main_layout["help"].update(Panel(Text(hints_divider).join([
        Text(hint, style=hints_style)
        for hint in edit_hints
    ]), title=hints_panel_name))


def use_add_hints():
    main_layout["help"].update(Panel(Text(hints_divider).join([
        Text(hint, style=hints_style)
        for hint in add_hints
    ]), title=hints_panel_name))
