<<<<<<< HEAD
"""Date-based seasonal layers: snow in winter, flowers in spring and a film strip during Zinemaldia."""
import math
import random

SEASONS = ("winter", "spring", "zinemaldia")
SNOWFLAKES = 26
FLAKE_RADIUS = 7
STRIP_HEIGHT = 18
FLOWER_GAP = 20
PETALS = ("#ff9ecf", "#fff4f8", "#c9a7ff")
THEMES = {"winter": "#9fe8ff", "spring": "#8fe388", "zinemaldia": "#f5c542"}
=======
"""Date-based seasonal layers: snow in winter, drums for the Tamborrada and a film strip during Zinemaldia."""
import math
import random

SEASONS = ("winter", "tamborrada", "zinemaldia")
SNOWFLAKES = 26
FLAKE_RADIUS = 7
STRIP_HEIGHT = 18
DRUMS = 24
THEMES = {"winter": "#9fe8ff", "tamborrada": "#5aa0ff", "zinemaldia": "#f5c542"}
>>>>>>> origin/main


def current(today):
    if today.month == 12 or (today.month == 1 and today.day <= 6):
        return "winter"
<<<<<<< HEAD
    # The first week of spring, from the March equinox.
    if today.month == 3 and 20 <= today.day <= 26:
        return "spring"
=======
    # The Tamborrada drums for 24 hours from midnight on 20 January; the 19th shows it on its eve.
    if today.month == 1 and today.day in (19, 20):
        return "tamborrada"
>>>>>>> origin/main
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


<<<<<<< HEAD
def flower_strip(y, width):
    """A row of flowers swaying in the breeze, below the game."""
    rng = random.Random(3)  # Fixed seed, like the snow.
    base = y + STRIP_HEIGHT - 1
    petals = "".join(f'<circle cx="{2.4 * math.cos(math.radians(a)):.1f}" cy="{2.4 * math.sin(math.radians(a)):.1f}" r="1.8"/>'
                     for a in range(0, 360, 72))
    flowers = [f'<defs><g id="season-flower">{petals}<circle r="1.3" fill="#ffd23f"/></g></defs>']
    for x in range(FLOWER_GAP // 2, width, FLOWER_GAP):
        swing = rng.uniform(6, 12)
        flowers.append(
            f'<g transform="translate({x} {base})"><g><animateTransform attributeName="transform" type="rotate" '
            f'values="-{swing:.0f};{swing:.0f};-{swing:.0f}" dur="{rng.uniform(2.5, 4):.1f}s" repeatCount="indefinite"/>'
            f'<path d="M0 0V-10" stroke="#3fae4f" stroke-width="1.2"/>'
            f'<use href="#season-flower" y="-11" fill="{rng.choice(PETALS)}"/></g></g>'
        )
    return (
        f'<rect y="{y}" width="{width}" height="{STRIP_HEIGHT}" fill="#04140a"/>{"".join(flowers)}'
        f'<rect x="{width / 2 - 125:g}" y="{y}" width="250" height="{STRIP_HEIGHT}" fill="#04140a"/>'
        f'<text x="{width / 2:g}" y="{y + 13}" text-anchor="middle" class="ra-mb" fill="#8fe388" style="font-size:11px">'
        f'SPRING IS HERE · UDABERRIA</text>'
=======
def drum_strip(y, width):
    """A row of drums that beat in turn, like the companies marching through Donostia."""
    gap = width / DRUMS
    drums = "".join(
        f'<g transform="translate({gap * (i + .5):.0f} {y + 10})"><g>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur=".5s" '
        f'begin="{i % 2 * .25:g}s" repeatCount="indefinite"/>'
        f'<rect x="-6" y="-4" width="12" height="9" rx="1" fill="#1d3f8f" stroke="#fff" stroke-width=".8"/>'
        f'<path d="M-6-4l4 9m0-9l4 9m0-9l4 9" stroke="#fff" stroke-width=".6"/>'
        f'<ellipse cy="-4" rx="6" ry="1.6" fill="#f4f4f4"/></g></g>'
        for i in range(DRUMS)
    )
    return (
        f'<rect y="{y}" width="{width}" height="{STRIP_HEIGHT}" fill="#06102a"/>{drums}'
        f'<rect x="{width / 2 - 125:g}" y="{y}" width="250" height="{STRIP_HEIGHT}" fill="#06102a"/>'
        f'<text x="{width / 2:g}" y="{y + 13}" text-anchor="middle" class="ra-mb" fill="#5aa0ff" style="font-size:11px">'
        f'TAMBORRADA · DONOSTIA · 20 JANUARY</text>'
>>>>>>> origin/main
    )


def layer(season, width, top, height, game_y, game_height):
    """Returns the SVG of the season, or nothing outside of them. Sits under the CRT layers."""
    if season is None:
        return ""
    color = THEMES[season]
    theme = f'<style>.ra-term .ra-acc{{fill:{color}}}.ra-term .ra-cur{{fill:{color}}}</style>'
    if season == "winter":
        art = snow(width, top, height)
<<<<<<< HEAD
    elif season == "spring":
        art = flower_strip(game_y + game_height, width)
=======
    elif season == "tamborrada":
        art = drum_strip(game_y + game_height, width)
>>>>>>> origin/main
    else:
        # Just below the game: inside it, the strip would cover the ship.
        art = film_strip(game_y + game_height, width)
    return f'{theme}<g class="ra-term">{art}</g>'
