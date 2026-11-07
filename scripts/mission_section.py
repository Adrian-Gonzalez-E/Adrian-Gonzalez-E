"""Bio scoreboard, mission complete screen and looping credits."""
from collections import Counter
from datetime import date
from html import escape
import re

SCOREBOARD_HEIGHT = 28
PAUSE_MS = 6000
SUCCESS_MS = 4000  # The rest of the pause shows the restart message.
ANIMATION = re.compile(r"<animate(?:Transform)?\b[^>]*>", re.S)
DATA_START = '<text x="548" y="66"'
DATA_END = '<rect x="548" y="262"'
SECONDS_PER_LINE = 1.6
LINE_HEIGHT = 22


def age(birth_date, today):
    """Completed years; birth_date in YYYY-MM-DD format."""
    born = date.fromisoformat(birth_date)
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def extend_cycle(galaga):
    """Holds the empty board PAUSE_MS at the end of the cycle. Returns (svg, original cycle, new cycle) in ms."""
    tags = [t for t in ANIMATION.findall(galaga) if "keyTimes=" in t]
    durations = Counter(re.search(r'dur="(\d+)ms"', t).group(1) for t in tags if re.search(r'dur="\d+ms"', t))
    if not durations:
        raise ValueError("Galaga has no recognizable cycle")
    cycle = int(durations.most_common(1)[0][0])
    new_cycle = cycle + PAUSE_MS

    def adjust(match):
        tag = match.group(0)
        if f'dur="{cycle}ms"' not in tag:
            return tag
        times = re.search(r'keyTimes="([^"]+)"', tag)
        values = re.search(r'values="([^"]+)"', tag)
        if not times or not values:
            raise ValueError("Galaga animation without keyTimes or values")
        t = [float(x) for x in times.group(1).split(";")]
        v = values.group(1).split(";")
        if len(t) != len(v) or t[-1] != 1:
            raise ValueError("Galaga animation with unexpected format")
        scaled = ";".join(f"{x * cycle / new_cycle:.6g}" for x in t) + ";1"
        tag = tag.replace(times.group(0), f'keyTimes="{scaled}"')
        tag = tag.replace(values.group(0), f'values="{values.group(1)};{v[-1]}"')
        return tag.replace(f'dur="{cycle}ms"', f'dur="{new_cycle}ms"')

    return ANIMATION.sub(adjust, galaga), cycle, new_cycle


def scoreboard(y, width, lvl, score, coins):
    baseline = y + 19

    def item(x, label, value):
        return (f'<text x="{x}" y="{baseline}" class="ra-mb" style="font-size:14px">'
                f'<tspan fill="#ff5f57">{label} </tspan><tspan fill="#fff">{value}</tspan></text>')

    return (
        f'<g class="ra-term"><rect y="{y}" width="{width}" height="{SCOREBOARD_HEIGHT}" fill="#000"/>'
        f'{item(20, "LVL", lvl)}{item(110, "SCORE", score)}{item(240, "CLASS", "ENGINEER")}{item(395, "FACTION", "HORDE")}'
        f'{item(540, "COINS", coins)}'
        f'<text x="{width - 20}" y="{baseline}" text-anchor="end" class="ra-mb" fill="#febc2e" style="font-size:14px">INSERT COIN'
        f'<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></text></g>'
    )


def end_screen(y, width, height, cycle, new_cycle):
    """Appears right when the last block falls, during the extend_cycle pause."""
    start = cycle / new_cycle
    switch = (cycle + SUCCESS_MS) / new_cycle
    center = width / 2

    def phase(text, color, size, values, times):
        return (f'<text x="{center:g}" y="{y + height / 2 + size / 3:g}" text-anchor="middle" class="ra-mb" fill="{color}" '
                f'style="font-size:{size}px" opacity="0">{text}<animate attributeName="opacity" values="{values}" '
                f'keyTimes="{times}" calcMode="discrete" dur="{new_cycle}ms" repeatCount="indefinite"/></text>')

    return (
        '<g class="ra-term">'
        + phase("ALL BUGS CLEARED", "#7cff9b", 40, "0;1;0", f"0;{start:.6g};{switch:.6g}")
        + phase("DEPLOYING TO PROD...", "#febc2e", 28, "0;1", f"0;{switch:.6g}")
        + '</g>'
    )


def github_data(terminal):
    """Reads commits and join year from the terminal; fails without them so the last good image stays."""
    commits = re.search(r'Commits</tspan><tspan[^>]*>: ([\d,]+)', terminal)
    joined = re.search(r'Since</tspan><tspan[^>]*>: (\d{4})', terminal)
    if not commits or not joined:
        raise ValueError("the terminal does not show commits and join year")
    return commits.group(1), joined.group(1)


def credits(terminal):
    """Replaces the terminal data column with looping credits."""
    commits, joined = github_data(terminal)
    start, end = terminal.find(DATA_START), terminal.find(DATA_END)
    if start < 0 or end < start:
        raise ValueError("the terminal does not have the expected data column")
    lines = (
        "Directed by Adrián González", "Screenplay by AI", "Script supervisor: Claude", f"Starring {commits} commits",
        "Special effects: Angular", "Typed in TypeScript", "Stunts: Spring Boot", "Cold starts by AWS Lambda",
        "Legacy scenes: PHP", "Faction: Horde", "Weather: Donostia rain", "Zinemaldia: out of office",
        f"On GitHub since {joined}", "No bugs were harmed",
    )
    top, height = 80, 170
    text = "".join(
        f'<text x="680" y="{top + i * LINE_HEIGHT}" text-anchor="middle" class="ra-m ra-fg">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    travel = height + len(lines) * LINE_HEIGHT
    column = (
        '<text x="548" y="66" class="ra-m"><tspan class="ra-acc">$</tspan><tspan class="ra-dim"> ./credits</tspan></text>'
        f'<clipPath id="credits-clip"><rect x="521" y="{top - 4}" width="319" height="{height}"/></clipPath>'
        f'<g clip-path="url(#credits-clip)"><g><animateTransform attributeName="transform" type="translate" '
        f'values="0 {height};0 {height - travel}" dur="{travel / LINE_HEIGHT * SECONDS_PER_LINE:g}s" '
        f'repeatCount="indefinite"/>{text}</g></g>'
    )
    return terminal[:start] + column + terminal[end:]
