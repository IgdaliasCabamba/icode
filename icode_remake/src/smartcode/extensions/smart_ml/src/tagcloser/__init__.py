import re


def close_tags(html):
    pattern_find_open_tag = "<[a-zA-Z0-9&\"'=\s:]+>"
    pattern_find_close_tag = "<\/[a-zA-Z0-9&\"'=\s:]+>"
    open_tag = re.findall(pattern_find_open_tag, html)[::-1]
    open_tag_clean = [x[1:-1].strip().split(" ")[0] for x in open_tag]
    close_tag = re.findall(pattern_find_close_tag, html)
    close_tag_clean = [x[2:-1].strip().split(" ")[0] for x in close_tag]
    for tag in open_tag_clean:
        if tag in close_tag_clean:
            close_tag_clean.remove(tag)
        else:
            html += "</" + tag + ">"
    return html
