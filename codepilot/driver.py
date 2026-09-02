from __future__ import annotations

import asyncio
import os
import sys
from ctypes import byref

if sys.platform == "win32":
    from textual._xterm_parser import XTermParser
    from textual.drivers import win32
    from textual.drivers._writer_thread import WriterThread
    from textual.drivers.windows_driver import WindowsDriver

    class _ImeEventMonitor(win32.EventMonitor):
        def run(self) -> None:
            exit_requested = self.exit_event.is_set
            parser = XTermParser(debug=False)

            try:
                read_count = win32.wintypes.DWORD(0)
                h_in = win32.GetStdHandle(win32.STD_INPUT_HANDLE)
                max_events = 1024
                key_event_type = 0x0001
                window_buffer_size_event = 0x0004
                input_records = (win32.INPUT_RECORD * max_events)()
                read_console_input = win32.KERNEL32.ReadConsoleInputW
                keys: list[str] = []

                while not exit_requested():
                    for event in parser.tick():
                        self.process_event(event)

                    if win32.wait_for_handles([h_in], 100) is None:
                        continue

                    read_console_input(
                        h_in, byref(input_records), max_events, byref(read_count)
                    )
                    keys.clear()
                    new_size: tuple[int, int] | None = None

                    for input_record in input_records[: read_count.value]:
                        event_type = input_record.EventType
                        if event_type == key_event_type:
                            key_event = input_record.Event.KeyEvent
                            if key_event.bKeyDown:
                                key = key_event.uChar.UnicodeChar
                                if key or not (
                                    key_event.dwControlKeyState
                                    and key_event.wVirtualKeyCode == 0
                                ):
                                    keys.append(key)
                        elif event_type == window_buffer_size_event:
                            size = input_record.Event.WindowBufferSizeEvent.dwSize
                            new_size = (size.X, size.Y)

                    if keys:
                        text = "".join(keys).encode(
                            "utf-16", "surrogatepass"
                        ).decode("utf-16")
                        for event in parser.feed(text):
                            self.process_event(event)
                    if new_size is not None:
                        self.on_size_change(*new_size)
            except Exception:
                self.app.log.exception("EVENT MONITOR ERROR")

    class NoAltScreenDriver(WindowsDriver):
        def start_application_mode(self) -> None:
            try:
                rows = os.get_terminal_size().lines
            except OSError:
                rows = 24
            sys.stdout.write("\n" * rows)
            sys.stdout.flush()

            loop = asyncio.get_running_loop()
            self._restore_console = win32.enable_application_mode()
            self._writer_thread = WriterThread(self._file)
            self._writer_thread.start()
            self._enable_mouse_support()
            self.write("\x1b[?25l")
            self.write("\033[?1004h")
            self.write("\x1b[>1u")
            self.flush()
            self._enable_bracketed_paste()
            self._event_thread = _ImeEventMonitor(
                loop, self._app, self.exit_event, self.process_message
            )
            self._event_thread.start()

        def write(self, data: str) -> None:
            data = data.replace("\x1b[?1049h", "").replace("\x1b[?1049l", "")
            if data:
                super().write(data)

else:
    from textual.drivers.linux_driver import LinuxDriver

    class NoAltScreenDriver(LinuxDriver):
        def start_application_mode(self) -> None:
            try:
                rows = os.get_terminal_size().lines
            except OSError:
                rows = 24
            sys.stdout.write("\n" * rows)
            sys.stdout.flush()
            super().start_application_mode()

        def write(self, data: str) -> None:
            data = data.replace("\x1b[?1049h", "").replace("\x1b[?1049l", "")
            if data:
                super().write(data)
