from rich.layout import Layout
from rich.live import Live
from input import get_key, handle_edit
from exports import get_exports, render_exports, get_export_layout, main_hints


def main():
    exports = get_exports()

    index = 0
    edit_key = True

    main_layout = Layout()
    exports_layout = get_export_layout(main_layout, exports)

    with Live(main_layout, screen=True, redirect_stderr=False, auto_refresh=False) as live:
        while True:
            render_exports(exports_layout, exports, index, edit_key)
            live.refresh()

            key = get_key()
            if key.lower() == "q":
                break

            # handle navigation
            if key == "up" and index > 0:
                index -= 1
            if key == "down" and index < (len(exports) - 1):
                index += 1
            if key == "left":
                edit_key = True
            if key == "right":
                edit_key = False
            if key == "return":
                handle_edit(live, exports_layout, index, exports, edit_key)


if __name__ == "__main__":
    main()
