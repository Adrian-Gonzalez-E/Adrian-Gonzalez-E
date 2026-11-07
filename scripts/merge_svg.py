#!/usr/bin/env python3
"""Puts Galaga inside the terminal header window, below the scoreboard.

Usage: BIRTH_DATE=YYYY-MM-DD [SEASON=winter|zinemaldia] merge_svg.py galaga.svg terminal.svg calendar.json coins.txt output.svg
Fails without writing the output if the input format changes, so the last good image stays.
The expected structure is that of readme-atelier v1.0.0, pinned in the workflow.
"""
from datetime import date
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import mission_section as mission
import seasons

WIDTH = 840
TERMINAL_HEIGHT = 300
TITLE_BAR_HEIGHT = 30
FREE_SELECTOR = re.compile(r"(?<![\w.-])(text|\*)(?=\s*[,{])")
TITLE = re.compile(r'<text x="420"[^>]*>.*?</text>', re.S)
CRT_LAYERS = '<rect width="840" height="300" fill="url(#ra-scan)"'
BORDER = '<rect x=".5" y=".5" width="839" height="299"'


def split_svg(svg):
    """Returns (width, height, inner content) of the root SVG."""
    root = re.search(r"<svg\b[^>]*>", svg)
    end = svg.rfind("</svg>")
    if not root or end < 0:
        raise ValueError("not an SVG")
    sizes = [re.search(rf'\b{a}="(\d+(?:\.\d+)?)"', root.group(0)) for a in ("width", "height")]
    if not all(sizes):
        raise ValueError("the root SVG does not declare width and height")
    width, height = (float(m.group(1)) for m in sizes)
    return width, height, svg[root.end():end]


def scope_css(content):
    """Limits the terminal's global selectors so they do not affect Galaga."""
    def scope(style):
        return style.group(1) + FREE_SELECTOR.sub(r".ra-term \1", style.group(2)) + style.group(3)
    return re.sub(r"(<style\b[^>]*>)(.*?)(</style>)", scope, content, flags=re.S)


def merge(galaga, terminal, lvl, score, coins, season=None):
    galaga, cycle = mission.play_once(galaga)
    g_width, g_height, g_content = split_svg(galaga)
    t_width, t_height, t_content = split_svg(terminal)
    if TITLE.search(t_content) is None or (t_width, t_height) != (WIDTH, TERMINAL_HEIGHT) or CRT_LAYERS not in t_content or BORDER not in t_content:
        raise ValueError("the terminal does not have the expected structure")
    t_content = mission.credits(t_content)
    title = TITLE.search(t_content)

    extra = round(g_height * WIDTH / g_width)
    total = TERMINAL_HEIGHT + extra + mission.SCOREBOARD_HEIGHT
    layers = t_content.index(CRT_LAYERS)
    game_y = TITLE_BAR_HEIGHT + mission.SCOREBOARD_HEIGHT

    head = scope_css(t_content[:title.start()]).replace(
        'width="840" height="300"', f'width="840" height="{total}"')
    body = scope_css(t_content[title.end():layers])
    tail = t_content[layers:].replace(
        'width="840" height="300"', f'width="840" height="{total}"').replace(
        'width="839" height="299"', f'width="839" height="{total - 1}"')

    screen = (f'<svg x="0" y="{game_y}" width="{WIDTH}" height="{extra}" '
              f'viewBox="0 0 {g_width:g} {g_height:g}">{g_content}</svg>')
    output = (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{total}" viewBox="0 0 {WIDTH} {total}" fill="none" role="img" '
        f'aria-label="Terminal window with Galaga played on my contribution graph and my profile">'
        f'{head}<g class="ra-term">{title.group(0)}</g>{mission.scoreboard(TITLE_BAR_HEIGHT, WIDTH, lvl, score, coins)}{screen}'
        f'{mission.end_screen(game_y, WIDTH, extra, cycle)}'
        f'<g class="ra-term" transform="translate(0 {extra + mission.SCOREBOARD_HEIGHT})">{body}</g>'
        f'{seasons.layer(season, WIDTH, TITLE_BAR_HEIGHT, total - TITLE_BAR_HEIGHT, game_y, extra)}{tail}</svg>'
    )
    ET.fromstring(output)  # Broken XML: better to fail than publish a broken image.
    if "<script" in output:
        raise ValueError("an input contains <script>")
    return output


def main():
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    galaga, terminal, calendar, coins_file, destination = sys.argv[1:]
    with open(galaga, encoding="utf-8") as f:
        g = f.read()
    with open(terminal, encoding="utf-8") as f:
        t = f.read()
    with open(calendar, encoding="utf-8") as f:
        score = json.load(f)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    with open(coins_file, encoding="utf-8") as f:
        coins = int(f.read())
    today = date.today()
    lvl = mission.age(os.environ["BIRTH_DATE"], today)
    output = merge(g, t, lvl, score, coins, seasons.resolve(os.environ.get("SEASON", ""), today))
    with open(destination, "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    main()
