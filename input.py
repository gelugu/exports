import os
import sys
import termios
import tty
from typing import List
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from exports import Export


def get_key():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    key_mapping = {
        127: 'backspace',
        10: 'return',
        27: 'esc',
        65: 'up',
        66: 'down',
        67: 'right',
        68: 'left'
    }

    try:
        while True:
            byte = os.read(sys.stdin.fileno(), 3).decode()
            if len(byte) == 3:
                k = ord(byte[2])
            else:
                k = ord(byte)
            if k in key_mapping.keys():
                return key_mapping.get(k, chr(k))
            return byte
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def get_char():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    key_mapping = {
        127: 'backspace',
        10: 'return',
        27: 'esc',
    }

    try:
        while True:
            byte = os.read(sys.stdin.fileno(), 3).decode()
            try:
                code = ord(byte)
            except TypeError:
                continue

            if code in key_mapping.keys():
                return key_mapping[code]
            return byte
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def handle_edit(live: Live, exports_layout: Layout, index: int, exports: List[Export], edit_key: bool):
    input_index = len(exports[index].key)
    current = exports[index].key
    if not edit_key:
        input_index = len(exports[index].value)
        current = exports[index].value

    while True:
        layout_index = f"{exports[index].file_name}_{exports[index].line_number}"
        export_index = "key"
        if not edit_key:
            export_index = "value"

        exports_layout[layout_index][export_index].update(
            Text(current[:input_index + 1], style="blue") +
            Text(" ", style="blink underline blue") +
            Text(current[input_index + 1:], style="blue")
        )
        exports_layout[layout_index][export_index].size = len(current) + 1
        live.refresh()

        key = get_char()
        if key in ["esc", "return"]:
            break
        if key == "left":
            if input_index >= 0:
                input_index -= 1
            continue
        if key == "right":
            if input_index < len(current) - 1:
                input_index += 1
            continue
        if key == "backspace":
            if input_index >= 0:
                current = f"{current[:input_index]}{current[input_index + 1:]}"
                input_index -= 1
        else:
            current = f"{current[:input_index + 1]}{key}{current[input_index + 1:]}"
            input_index += 1

        if edit_key:
            exports[index].key = current
        else:
            exports[index].value = current
