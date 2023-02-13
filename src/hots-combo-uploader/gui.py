import logging
import platform
import time
from pathlib import Path

import PySimpleGUI as sg
from screeninfo import get_monitors
from upload import upload
from watchdog.events import LoggingEventHandler, PatternMatchingEventHandler
from watchdog.observers import Observer


# From https://github.com/PySimpleGUI/PySimpleGUI/issues/715#issuecomment-1249907482
# TODO: make it actually work
class CenteredWindow(sg.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_default_screen_dimensions(self):
        print(get_monitors())
        default_monitors = [monitor for monitor in get_monitors() if monitor.is_primary]
        default_monitor = default_monitors[0] if default_monitors else get_monitors()[0]
        screen_width, screen_height = default_monitor.width, default_monitor.height
        return screen_width, screen_height

    def move_to_center(self):
        if not self._is_window_created("tried Window.move_to_center"):
            return
        screen_width, screen_height = self.get_default_screen_dimensions()
        win_width, win_height = self.size
        x, y = (screen_width - win_width) // 2, (screen_height - win_height) // 2
        self.move(x, y)


def watch_for_file_changes(path, window):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Monitor for file changes?
    event_handler = Handler(window)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    while True:
        time.sleep(1)

    observer.stop()
    observer.join()


class Handler(PatternMatchingEventHandler):
    def __init__(self):
        super(Handler, self).__init__(patterns=["*.StormReplay"])
        self.window = window

    def on_created(self, event):
        if event.event_type == "created":
            print(event.src_path)
            upload(event.src_path, window)


def main_window(config, app_path, location=(25, 25)):
    path = ""
    if "path" in config["HOTS"]:
        path = config["HOTS"]["path"]
    elif platform.system() == "Windows":
        path = str(Path.home()) + "\\Documents\\Heroes of the Storm\\"
    elif platform.system() == "Darwin":
        path = (
            str(Path.home())
            + "/Library/Application Support/Blizzard/Heroes of the Storm/Accounts/"
        )

    layout = [
        [
            sg.Text("Select your Heroes of the Storm folder: "),
            sg.Input(path, key="-PATH-", change_submits=True),
            sg.FolderBrowse("Browse", key="-PATH-", initial_folder=path),
        ],
        [sg.Text("Uploaded replays:")],
        [],
    ]

    window = CenteredWindow(
        title="HOTS Combo Uploader",
        layout=layout,
        element_justification="c",
        finalize=True,
        location=location,
    )
    window.move_to_center()

    window.start_thread(
        lambda: watch_for_file_changes(path), ("-WATCHER-", "-WATCHER ENDED-")
    )

    while True:
        event, values = window.read(timeout=1 * 100)
        if event == "-PATH-":
            config["HOTS"]["path"] = values["-PATH-"]
            Path(app_path).mkdir(parents=True, exist_ok=True)
            with open(f"{app_path}/config.ini", "w") as f:
                config.write(f)
        elif event == "close_main_window" or event == sg.WIN_CLOSED:
            break

    window.close()
