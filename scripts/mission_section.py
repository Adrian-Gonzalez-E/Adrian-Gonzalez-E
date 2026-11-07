"""Bio scoreboard, mission complete screen and looping credits."""
from collections import Counter
from datetime import date
from html import escape
import re

SCOREBOARD_HEIGHT = 28
SUCCESS_MS = 4000
ANIMATION = re.compile(r"<animate(?:Transform)?\b[^>]*>", re.S)
DATA_START = '<text x="548" y="66"'
DATA_END = '<rect x="548" y="262"'
SECONDS_PER_LINE = 1.6
LINE_HEIGHT = 22


def age(birth_date, today):
    """Completed years; birth_date in YYYY-MM-DD format."""
    born = date.fromisoformat(birth_date)
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def play_once(galaga):
    """Plays the game a single time and freezes its last frame. Returns (svg, cycle in ms). Stars keep moving."""
    tags = [t for t in ANIMATION.findall(galaga) if "keyTimes=" in t]
    durations = Counter(re.search(r'dur="(\d+)ms"', t).group(1) for t in tags if re.search(r'dur="\d+ms"', t))
    if not durations:
        raise ValueError("Galaga has no recognizable cycle")
    cycle = int(durations.most_common(1)[0][0])

    def freeze(match):
        tag = match.group(0)
        if f'dur="{cycle}ms"' not in tag:
            return tag
        times = re.search(r'keyTimes="([^"]+)"', tag)
        values = re.search(r'values="([^"]+)"', tag)
        if not times or not values or 'repeatCount="indefinite"' not in tag:
            raise ValueError("Galaga animation without keyTimes, values or repeatCount")
        t = times.group(1).split(";")
        if len(t) != len(values.group(1).split(";")) or float(t[-1]) != 1:
            raise ValueError("Galaga animation with unexpected format")
        return tag.replace('repeatCount="indefinite"', 'repeatCount="1" fill="freeze"')

    return ANIMATION.sub(freeze, galaga), cycle


def scoreboard(y, width, lvl, score, coins):
    baseline = y + 19

    def item(x, label, value):
        return (f'<text x="{x}" y="{baseline}" class="ra-mb" style="font-size:14px">'
                f'<tspan fill="#ff5f57">{label} </tspan><tspan fill="#fff">{value}</tspan></text>')

    return (
        f'<g class="ra-term"><rect y="{y}" width="{width}" height="{SCOREBOARD_HEIGHT}" fill="#000"/>'
        f'{item(20, "LVL", lvl)}{item(150, "SCORE", score)}{item(310, "CLASS", "ENGINEER")}{item(510, "FACTION", "HORDE")}'
        f'{item(710, "COINS", coins)}</g>'
    )


def end_screen(y, width, height, cycle):
    """Shows the success message when the last block falls, then stays on the call to insert a coin."""
    success_end = cycle + SUCCESS_MS
    center = width / 2
    middle = y + height / 2
    return (
        f'<g class="ra-term"><text x="{center:g}" y="{middle + 13:g}" text-anchor="middle" class="ra-mb" fill="#7cff9b" '
        f'style="font-size:40px" opacity="0">ALL BUGS CLEARED<animate attributeName="opacity" values="0;1;0" '
        f'keyTimes="0;{cycle / success_end:.6g};1" calcMode="discrete" dur="{success_end}ms" fill="freeze"/></text>'
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{success_end}ms" fill="freeze"/><g>'
        f'<animate attributeName="opacity" values="1;.25;1" dur="1.2s" repeatCount="indefinite"/>'
        f'<text x="{center:g}" y="{middle:g}" text-anchor="middle" class="ra-mb" fill="#febc2e" style="font-size:26px">'
        f'INSERT COIN TO CONTINUE</text>'
        f'<path d="M{center - 10:g} {middle + 14:g}h20l-10 12z" fill="#febc2e"/></g></g></g>'
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
