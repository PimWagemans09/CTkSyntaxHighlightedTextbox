from typing import Tuple
import customtkinter as ctk
import pathlib
import queue
from .highlightingengine import HighlightingEngine
import json


class CTkSyntaxHighlightedTextbox(ctk.CTkTextbox):
    def __init__(
        self,
        master: any,
        tags: dict | pathlib.Path,
        width: int = 200,
        height: int = 200,
        corner_radius: int | None = None,
        border_width: int | None = None,
        border_spacing: int = 3,
        bg_color: str | Tuple[str, str] = "transparent",
        fg_color: str | Tuple[str, str] | None = None,
        border_color: str | Tuple[str, str] | None = None,
        text_color: str | None = None,
        scrollbar_button_color: str | Tuple[str, str] | None = None,
        scrollbar_button_hover_color: str | Tuple[str, str] | None = None,
        font: tuple | ctk.CTkFont | None = None,
        activate_scrollbars: bool = True,
        **kwargs,
    ) -> None:
        """
        A syntax highlighted textbox for customtkinter
        supports all functions and arguments from customtkinter.Textbox
        plus the argument tags
        tags can be a tags dict
        or a path to a json file containing a tags dict
        more info about what a tags dict is can be found in the README
        https://github.com/PimWagemans09/CTkSyntaxHighlightedTextbox/blob/main/README.md
        """
        super().__init__(
            master,
            width,
            height,
            corner_radius,
            border_width,
            border_spacing,
            bg_color,
            fg_color,
            border_color,
            text_color,
            scrollbar_button_color,
            scrollbar_button_hover_color,
            font,
            activate_scrollbars,
            **kwargs,
        )
        self.tagnames = []
        self.tagpatterns = {}
        self.clearModifiedFlag()
        self.bind("<<Modified>>", self._beenModified)
        if isinstance(tags, dict):
            self._load_tags_dict(tags)
        elif isinstance(tags, pathlib.Path):
            self._load_tags_dict_from_file()
        self.callback_queue = queue.Queue()

    def highlight(self):
        try:
            self.highlighter.stop()
        except AttributeError:
            pass
        self.highlighter = HighlightingEngine("highlighter", self, self.callback_queue)
        self.highlighter.start()
        self._check_on_HighlightingEngine()

    def _apply_highlighting(self, indexes: list[tuple[str, int, int]]) -> None:
        self.winfo_toplevel().update_idletasks()
        for tagname in self.tags_dict.keys():
            self.tag_remove(tagName=tagname, index1="0.0", index2=ctk.END)
        for tagname, startindex, endindex in indexes:
            self.tag_add(
                tagName=tagname,
                index1=f"1.0+{startindex}c",
                index2=f"1.0+{endindex}c",
            )

    def _check_on_HighlightingEngine(self):
        try:
            indexes = self.callback_queue.get(False)
            self._apply_highlighting(indexes)
            return
        except queue.Empty:  # raised when queue is empty
            pass
        self.after(1, self._check_on_HighlightingEngine)

    def update_line_numbers(self) -> None:
        self.after_idle(self.linenums.redraw)
        self.after(10, self.update_line_numbers)

    def _beenModified(self, event=None):
        if self._resetting_modified_flag:
            return

        self.clearModifiedFlag()

        self.highlight()

    def clearModifiedFlag(self):
        self._resetting_modified_flag = True

        try:
            self.edit_modified(False)

        finally:
            self._resetting_modified_flag = False

    def _load_tags_dict_from_file(self, path: pathlib.Path) -> None:
        with path.open(mode="r") as file:
            self.tags_dict = json.load(file)
        self._load_tags()

    def _load_tags_dict(self, tags_dict: dict):
        self.tags_dict = tags_dict
        self._load_tags()

    def _load_tags(self):
        for tag in self.tags_dict["tags"]:
            if not "foreground" in tag:
                tag["foreground"] = "#ffffff"
            self.tag_config(tagName=tag["name"], foreground=tag["foreground"])
            self.tagnames.append(tag["name"])
            self.tagpatterns[tag["name"]] = tag["patterns"]
