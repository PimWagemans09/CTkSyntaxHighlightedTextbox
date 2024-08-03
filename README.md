# CTkSyntaxHighlightedTextbox

CTkHighlightedTextbox is a customtkinter textbox with built in syntax highlighting.<br>
The syntax highlighting is fully customizable a works using regexes.

i made this because i needed it for another project and i decided to publish it

## CTkHighlightedTextbox

### arguments

there currently is only one extra argument: `tags`<br>
tags can either be a `dict` or a `pathlib.Path` pointing to a json file containing said dict<br>
the structure of the dict is the following:<br>

```python
{"tags":[{
    "name":"Example", "text_color":"#f00", "background":"#000", "patterns":["e"]}
}

]}
```
