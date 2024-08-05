from typing import Tuple
import customtkinter as ctk
import pathlib
import queue
from .highlightingengine import HighlightingEngine
import json
import re


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
        plus the argument "tags"\n
        "tags" can be a tags dict or a path to a json file containing a tags dict
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
        self._highlighting = False
        self._tagnames = []
        self._tagpatterns: dict[str, list[re.Pattern]] = {}
        self._clearModifiedFlag()
        self.bind("<<Modified>>", self._beenModified)
        self.bind("<Key>", lambda event: self.highlight())
        if isinstance(tags, dict):
            self._load_tags_dict(tags)
        elif isinstance(tags, pathlib.Path):
            self._load_tags_dict_from_file()
        self.callback_queue = queue.Queue()

        self.highlight()

    def replace_tags_dict(
        self,
        tags: dict | pathlib.Path,
    ):
        for tag in self._tagnames:
            self.tag_delete(tag)
        self._tagnames = []
        self._tagpatterns = {}
        if isinstance(tags, dict):
            self._load_tags_dict(tags)
        elif isinstance(tags, pathlib.Path):
            self._load_tags_dict_from_file()
        self.highlight()

    def highlight(self):
        try:
            self._highlightingengine.stop()
        except AttributeError:
            pass
        self._highlighting = True
        self._highlightingengine = HighlightingEngine(
            "highlighter", self, self.callback_queue
        )

        self._highlightingengine.start()
        self._DONT_CALL_check_on_HighlightingEngine()

    def _apply_highlighting(self, indexes: list[tuple[str, int, int]]) -> None:
        self.winfo_toplevel().update_idletasks()
        for tagname in self._tagnames:
            self.tag_remove(tagName=tagname, index1="0.0", index2=ctk.END)
        for tagname, startindex, endindex in indexes:
            self.tag_add(
                tagName=tagname,
                index1=f"1.0+{startindex}c",
                index2=f"1.0+{endindex}c",
            )

    def _DONT_CALL_check_on_HighlightingEngine(
        self,
    ):  # dont call outside of self.highlight()
        if not self._highlighting:
            return
        try:
            indexes = self.callback_queue.get(False)
            self._apply_highlighting(indexes)
            self._highlighting = True
            return
        except queue.Empty:
            pass
        self.after(1, self._DONT_CALL_check_on_HighlightingEngine)

    def _beenModified(self, event=None):
        if self._resetting_modified_flag:
            return

        self._clearModifiedFlag()

        self.highlight()

    def _clearModifiedFlag(self):
        self._resetting_modified_flag = True

        try:
            self.edit_modified(False)

        finally:
            self._resetting_modified_flag = False

    def _load_tags_dict_from_file(self, path: pathlib.Path) -> None:
        with path.open(mode="r") as file:
            self._tags_dict = json.load(file)
        self._load_tags()

    def _load_tags_dict(self, tags_dict: dict):
        self._tags_dict = tags_dict
        self._load_tags()

    def _load_tags(self):
        re.purge()
        for tag in self._tags_dict["tags"]:
            if "text_color" in tag:
                self.tag_config(tagName=tag["name"], foreground=tag["text_color"])
            if "background" in tag:
                self.tag_config(tagName=tag["name"], background=tag["background"])
            self._tagnames.append(tag["name"])
            compiled_patterns = []
            for pattern in tag["patterns"]:
                compiled_pattern = re.compile(pattern=pattern, flags=re.MULTILINE)
                compiled_patterns.append(compiled_pattern)
            self._tagpatterns[tag["name"]] = compiled_patterns
