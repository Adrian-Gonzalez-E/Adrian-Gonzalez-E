"""Date-based seasonal layers: snow in winter, waves in summer and a film strip during Zinemaldia."""
import math
import random

SEASONS = ("winter", "summer", "zinemaldia")
SNOWFLAKES = 26
FLAKE_RADIUS = 7
STRIP_HEIGHT = 18
WAVE_LENGTH = 40
THEMES = {"winter": "#9fe8ff", "summer": "#ffb627", "zinemaldia": "#f5c542"}


def current(today):
    if today.month == 12 or (today.month == 1 and today.day <= 6):
        return "winter"
    # The first week of summer, from the June solstice.
    if today.month == 6 and 21 <= today.day <= 27:
        return "summer"
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


def wave_strip(y, width):
    """Two rows of waves rolling in opposite directions, like La Concha beach."""
    def wave(level, color, seconds, direction):
        crests = "".join(f"q{WAVE_LENGTH / 4:g} -4 {WAVE_LENGTH / 2:g} 0t{WAVE_LENGTH / 2:g} 0"
                         for _ in range(width // WAVE_LENGTH + 3))
        return (f'<g><animateTransform attributeName="transform" type="translate" from="0 0" '
                f'to="{direction * WAVE_LENGTH} 0" dur="{seconds}s" repeatCount="indefinite"/>'
                f'<path d="M-{WAVE_LENGTH} {y + level}{crests}" stroke="{color}" stroke-width="1.5" fill="none"/></g>')
    return (
        f'<rect y="{y}" width="{width}" height="{STRIP_HEIGHT}" fill="#021624"/>'
        f'{wave(7, "#3a8fd6", 3, 1)}{wave(13, "#7fd3ff", 2, -1)}'
        f'<rect x="{width / 2 - 125:g}" y="{y}" width="250" height="{STRIP_HEIGHT}" fill="#021624"/>'
        f'<text x="{width / 2:g}" y="{y + 13}" text-anchor="middle" class="ra-mb" fill="#ffb627" style="font-size:11px">'
        f'SUMMER IS HERE · UDA</text>'
    )


def layer(season, width, top, height, game_y, game_height):
    """Returns the SVG of the season, or nothing outside of them. Sits under the CRT layers."""
    if season is None:
        return ""
    color = THEMES[season]
    theme = f'<style>.ra-term .ra-acc{{fill:{color}}}.ra-term .ra-cur{{fill:{color}}}</style>'
    if season == "winter":
        art = snow(width, top, height)
    elif season == "summer":
        art = wave_strip(game_y + game_height, width)
    else:
        # Just below the game: inside it, the strip would cover the ship.
        art = film_strip(game_y + game_height, width)
    return f'{theme}<g class="ra-term">{art}</g>'
