from rich.live import Live

from hints import use_edit_hints
from input import get_key, handle_edit
from exports import get_exports, render_exports, get_export_layout, save_exports, delete_export
from cache import main_layout


def main():
    exports = get_exports()

    index = 0
    edit_key = True

    with Live(main_layout, screen=True, redirect_stderr=False, auto_refresh=False) as live:
        while True:
            exports_layout = get_export_layout(exports)
            render_exports(exports_layout, exports, index, edit_key)
            live.refresh()

            key = get_key()
            if key.lower() == "q":
                break

            # handle navigation
            if key == "up":
                if index <= 0:
                    index = len(exports) - 1
                else:
                    index -= 1
            if key == "down":
                if index >= (len(exports) - 1):
                    index = 0
                else:
                    index += 1
            if key == "left":
                edit_key = True
            if key == "right":
                edit_key = False
            if key.lower() == "d":
                delete_export(exports[index])
                exports.remove(exports[index])
            if key == "return":
                use_edit_hints()
                handle_edit(live, exports_layout, index, exports, edit_key)
                save_exports(exports)


if __name__ == "__main__":
    main()
