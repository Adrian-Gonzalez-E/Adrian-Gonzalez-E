"""Date-based seasonal layers: snow in winter and a film strip during Zinemaldia."""
import random

SEASONS = ("winter", "zinemaldia")
SNOWFLAKES = 45
STRIP_HEIGHT = 18
THEMES = {"winter": "#9fe8ff", "zinemaldia": "#f5c542"}


def current(today):
    if today.month == 12 or (today.month == 1 and today.day <= 6):
        return "winter"
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


def snow(width, top, height):
    rng = random.Random(7)  # Fixed seed: daily regenerations do not change the image without a reason.
    flakes = []
    for _ in range(SNOWFLAKES):
        duration = rng.uniform(7, 16)
        flakes.append(
            f'<circle cx="{rng.uniform(0, width):.0f}" r="{rng.uniform(.8, 2.2):.1f}" fill="#fff" '
            f'opacity="{rng.uniform(.35, .85):.2f}"><animate attributeName="cy" from="{top - 4}" to="{top + height + 4}" '
            f'dur="{duration:.1f}s" begin="-{rng.uniform(0, duration):.1f}s" repeatCount="indefinite"/></circle>'
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


def layer(season, width, top, height, game_y, game_height):
    """Returns the SVG of the season, or nothing outside of them. Sits under the CRT layers."""
    if season is None:
        return ""
    color = THEMES[season]
    theme = f'<style>.ra-term .ra-acc{{fill:{color}}}.ra-term .ra-cur{{fill:{color}}}</style>'
    if season == "winter":
        art = snow(width, top, height)
    else:
        # Just below the game: inside it, the strip would cover the ship.
        art = film_strip(game_y + game_height, width)
    return f'{theme}<g class="ra-term">{art}</g>'
