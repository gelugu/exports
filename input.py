import os
import sys
import termios
import tty
from rich.text import Text
from rich.layout import Layout
from rich.live import Live

import cache


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


def handle_edit(live: Live, exports_layout: Layout, index: int):
    input_index = len(cache.exports[index].line)
    current = cache.exports[index].line

    while True:
        layout_index = f"{cache.exports[index].file_name}_{cache.exports[index].line_number}"

        exports_layout[layout_index]["line"].update(
            Text(current[:input_index + 1], style="blue") +
            Text(" ", style="blink underline blue") +
            Text(current[input_index + 1:], style="blue")
        )
        exports_layout[layout_index]["line"].size = len(current) + 1
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

        cache.exports[index].line = current
