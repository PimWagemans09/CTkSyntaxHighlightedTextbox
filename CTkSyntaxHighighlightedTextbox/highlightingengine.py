from typing import NoReturn
import threading
import ctypes
import customtkinter as ctk
from . import syntax_highlighted_textbox
from typing import Any, Tuple
import re
import queue


class HighlightingEngine(threading.Thread):
    def __init__(
        self,
        name: str,
        master: "syntax_highlighted_textbox.CTkSyntaxHighlightedTextbox",
        callback_queue: queue.Queue,
    ) -> None:  # "CTkSyntaxHighlightedTextbox" in quotes to avoid circular import
        threading.Thread.__init__(self)
        self.daemon = True
        self.master = master
        self.callback_queue = callback_queue
        self.name = name

    def run(self) -> NoReturn:
        indexes: list[Tuple[str, int, int]] = []
        text_to_search = self.master.get("1.0", ctk.END)
        try:
            for tagname in self.master._tagnames:
                pattern: re.Pattern
                for pattern in self.master._tagpatterns[tagname]:
                    match: re.Match
                    for match in pattern.finditer(string=text_to_search):
                        if len(match.groups()) > 0:
                            for i in range(1, len(match.groups()) + 1):
                                if match.start(i) < 0:
                                    continue
                                indexes.append((tagname, match.start(i), match.end(i)))
                        else:
                            indexes.append((tagname, match.start(), match.end()))

            self.callback_queue.put(item=indexes)
        finally:
            pass

    def get_id(self) -> Any:

        # returns id of the respective thread
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self) -> None:
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
