from rich.live import Live

from hints import use_edit_hints
from input import get_key, handle_edit
from exports import get_exports, render_exports, get_export_layout, save_exports, delete_export, add_export
import cache


def main():
    cache.exports = get_exports()

    index = 0

    with Live(
            cache.main_layout,
            screen=True,
            redirect_stderr=False,
            auto_refresh=False,
            console=cache.main_console
    ) as live:
        while True:
            exports_layout = get_export_layout()
            render_exports(exports_layout, index)
            live.refresh()

            key = get_key()
            if key.lower() == "q":
                break

            # handle navigation
            if key == "up":
                if index <= 0:
                    index = len(cache.exports) - 1
                else:
                    index -= 1
            if key == "down":
                if index >= (len(cache.exports) - 1):
                    index = 0
                else:
                    index += 1
            if key.lower() == "a":
                cache.exports, add_index = add_export(live)
                exports_layout = get_export_layout()
                render_exports(exports_layout, add_index)
                live.refresh()
                handle_edit(live, exports_layout, add_index)
                save_exports(live)
            if key.lower() == "d":
                delete_export(cache.exports[index])
                cache.exports.remove(cache.exports[index])
            if key == "return":
                use_edit_hints()
                handle_edit(live, exports_layout, index)
                save_exports(live)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        cache.main_console.print_exception()
