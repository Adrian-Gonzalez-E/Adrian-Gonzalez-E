"""Date-based seasonal layers: snow in winter, fireworks for Semana Grande and a film strip during Zinemaldia."""
import math
import random

SEASONS = ("winter", "semana-grande", "zinemaldia")
SNOWFLAKES = 26
FLAKE_RADIUS = 7
STRIP_HEIGHT = 18
FIREWORKS = 8
SPARKS = 14
SPARK_COLORS = ("#ff4d6d", "#ffd23f", "#4dd9ff", "#9dff6a", "#ff9ef0", "#ffffff")
THEMES = {"winter": "#9fe8ff", "semana-grande": "#ff4d6d", "zinemaldia": "#f5c542"}


def current(today):
    if today.month == 12 or (today.month == 1 and today.day <= 6):
        return "winter"
    # shortcut: fixed window around 15 August, while the festival week moves each year; adjust it if it moves out of it.
    if today.month == 8 and 10 <= today.day <= 17:
        return "semana-grande"
    # shortcut: fixed window around the festival, whose dates change yearly; adjust it if they move out of it.
    if today.month == 9 and today.day >= 15:
        return "zinemaldia"
    return None


def resolve(forced, today):
    """Returns the season to show; forced is empty, 'auto' or a season, to preview it on any date."""
    if forced in ("", "auto"):
        return current(today)
    if forced not in SEASONS:
        raise ValueError(f"unknown season: {forced}")
    return forced


def flake_path():
    """Six-armed snowflake drawn as a vector, so it does not depend on the viewer's fonts or emoji."""
    segments = []
    for degrees in range(0, 360, 60):
        arm = math.radians(degrees)
        tip = (FLAKE_RADIUS * math.cos(arm), FLAKE_RADIUS * math.sin(arm))
        fork = (FLAKE_RADIUS * .6 * math.cos(arm), FLAKE_RADIUS * .6 * math.sin(arm))
        segments.append(f"M0 0L{tip[0]:.1f} {tip[1]:.1f}")
        for side in (-1, 1):
            branch = arm + side * math.radians(50)
            segments.append(f"M{fork[0]:.1f} {fork[1]:.1f}l{2.5 * math.cos(branch):.1f} {2.5 * math.sin(branch):.1f}")
    return "".join(segments)


def snow(width, top, height):
    rng = random.Random(7)  # Fixed seed: daily regenerations do not change the image without a reason.
    flakes = [f'<defs><path id="season-flake" d="{flake_path()}" fill="none" stroke="#dff6ff" '
              f'stroke-width="1.2" stroke-linecap="round"/></defs>']
    for _ in range(SNOWFLAKES):
        x = rng.uniform(0, width)
        duration = rng.uniform(9, 18)
        spin = rng.choice((-1, 1)) * 360
        flakes.append(
            f'<g opacity="{rng.uniform(.65, 1):.2f}"><animateTransform attributeName="transform" type="translate" '
            f'from="{x:.0f} {top - 10}" to="{x:.0f} {top + height + 10}" dur="{duration:.1f}s" '
            f'begin="-{rng.uniform(0, duration):.1f}s" repeatCount="indefinite"/>'
            f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="{spin}" '
            f'dur="{rng.uniform(8, 16):.1f}s" repeatCount="indefinite"/>'
            f'<use href="#season-flake" transform="scale({rng.uniform(.65, 1.35):.2f})"/></g></g>'
        )
    return "".join(flakes)


def film_strip(y, width):
    holes = "".join(
        f'<rect x="{x}" y="{y + row}" width="7" height="3" rx="1" fill="#f5c542"/>'
        for x in range(-21, width + 21, 21) for row in (2, STRIP_HEIGHT - 5)
    )
    return (
        f'<rect y="{y}" width="{width}" height="{STRIP_HEIGHT}" fill="#120e02"/>'
        f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="21 0" dur="1s" repeatCount="indefinite"/>{holes}</g>'
        f'<rect x="{width / 2 - 125:g}" y="{y}" width="250" height="{STRIP_HEIGHT}" fill="#120e02"/>'
        f'<text x="{width / 2:g}" y="{y + 13}" text-anchor="middle" class="ra-mb" fill="#f5c542" style="font-size:11px">'
        f'ZINEMALDIA SEASON · DONOSTIA</text>'
    )


def fireworks(width, top, height):
    """Bursts of sparks that open and fade at different places and times, like the fireworks over La Concha."""
    rng = random.Random(15)  # Fixed seed, like the snow.
    sparks = "".join(
        f'<path d="M{6 * math.cos(math.radians(a)):.1f} {6 * math.sin(math.radians(a)):.1f}'
        f'L{30 * math.cos(math.radians(a)):.1f} {30 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(0, 360, 360 // SPARKS)
    )
    items = [f'<defs><g id="season-burst" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 5">{sparks}</g></defs>']
    for _ in range(FIREWORKS):
        x, y = rng.uniform(40, width - 40), rng.uniform(top + 40, top + height - 40)
        duration = rng.uniform(2.5, 4)
        begin = f'begin="-{rng.uniform(0, duration):.1f}s"'
        # Opens in the first 40% of the cycle and stays dark for the rest, until the next burst.
        timing = f'keyTimes="0;.4;1" dur="{duration:.1f}s" {begin} repeatCount="indefinite"'
        items.append(
            f'<g transform="translate({x:.0f} {y:.0f}) scale({rng.uniform(.7, 1.3):.2f})">'
            f'<g opacity="0"><animate attributeName="opacity" values="1;0;0" {timing}/>'
            f'<animateTransform attributeName="transform" type="scale" values=".1;1;1" {timing}/>'
            f'<use href="#season-burst" stroke="{rng.choice(SPARK_COLORS)}"/></g></g>'
        )
    return "".join(items)


def layer(season, width, top, height, game_y, game_height):
    """Returns the SVG of the season, or nothing outside of them. Sits under the CRT layers."""
    if season is None:
        return ""
    color = THEMES[season]
    theme = f'<style>.ra-term .ra-acc{{fill:{color}}}.ra-term .ra-cur{{fill:{color}}}</style>'
    if season == "winter":
        art = snow(width, top, height)
    elif season == "semana-grande":
        art = fireworks(width, top, height)
    else:
        # Just below the game: inside it, the strip would cover the ship.
        art = film_strip(game_y + game_height, width)
    return f'{theme}<g class="ra-term">{art}</g>'
