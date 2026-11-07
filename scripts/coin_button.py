"""Generates the Insert coin button: off during the game, lit when the game asks for a coin."""
import xml.etree.ElementTree as ET

WIDTH, HEIGHT = 300, 64
PIXEL = 3
TEXT = "INSERT COIN"
TEXT_X = 72
SLOT_X, SLOT_Y, SLOT_HEIGHT = 38, 14, 36
# 5x7 pixel letters: the text does not depend on the viewer's fonts.
GLYPHS = {
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "N": "10001 11001 10101 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}


def text_path():
    y = (HEIGHT - 7 * PIXEL) // 2
    segments = []
    for i, letter in enumerate(TEXT):
        for r, row in enumerate(GLYPHS[letter].split()):
            for c, bit in enumerate(row):
                if bit == "1":
                    segments.append(f"M{TEXT_X + (i * 6 + c) * PIXEL} {y + r * PIXEL}h{PIXEL}v{PIXEL}h-{PIXEL}z")
    return "".join(segments)


def button(delay_ms):
    """Returns the SVG. delay_ms is when the game asks for a coin, counted from the image load."""
    switch_on = f'<set attributeName="opacity" to="1" begin="{delay_ms}ms" fill="freeze"/>'
    text = text_path()
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'role="img" aria-label="Insert coin">'
        f'<defs><linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b2f36"/>'
        f'<stop offset=".5" stop-color="#15181c"/><stop offset="1" stop-color="#23262c"/></linearGradient>'
        f'<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffe680"/>'
        f'<stop offset="1" stop-color="#d99a14"/></linearGradient>'
        f'<filter id="glow" x="-80%" y="-30%" width="260%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>'
        f'<clipPath id="into"><rect width="{SLOT_X}" height="{HEIGHT}"/></clipPath></defs>'
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="10" fill="url(#metal)" stroke="#7cff9b" stroke-opacity=".35"/>'
        f'<rect x="5" y="5" width="{WIDTH - 10}" height="{HEIGHT - 10}" rx="7" fill="none" stroke="#000" stroke-opacity=".5"/>'
        # Only visible once the game ends: the slot light and the coin.
        f'<g opacity="0">{switch_on}'
        f'<rect x="{SLOT_X - 13}" y="{SLOT_Y - 7}" width="26" height="{SLOT_HEIGHT + 14}" rx="5" fill="#ff3b30" filter="url(#glow)">'
        f'<animate attributeName="opacity" values=".55;1;.55" dur="1.2s" repeatCount="indefinite"/></rect>'
        f'<g clip-path="url(#into)"><g><animateTransform attributeName="transform" type="translate" '
        f'values="-14 32;18 32;18 32;42 32;42 32" keyTimes="0;.3;.62;.8;1" dur="3s" repeatCount="indefinite"/>'
        f'<ellipse rx="11" ry="11" fill="url(#gold)" stroke="#8a5f07"/>'
        f'<ellipse rx="6" ry="6" fill="none" stroke="#a87408" stroke-width="1.5"/></g></g></g>'
        f'<rect x="{SLOT_X - 8}" y="{SLOT_Y - 3}" width="16" height="{SLOT_HEIGHT + 6}" rx="3" fill="#3a3f47" stroke="#0a0b0d"/>'
        f'<rect x="{SLOT_X - 1.5:g}" y="{SLOT_Y}" width="3" height="{SLOT_HEIGHT}" rx="1.5" fill="#000"/>'
        # The dim text stays readable during the game; the lit one replaces it at the end.
        f'<path d="{text}" fill="#6b5a2a"><set attributeName="opacity" to="0" begin="{delay_ms}ms" fill="freeze"/></path>'
        f'<g opacity="0">{switch_on}'
        f'<path d="{text}" fill="#febc2e"><animate attributeName="opacity" values="1;1;.15;.15;1" keyTimes="0;.55;.56;.95;1" '
        f'dur="1.2s" repeatCount="indefinite"/></path></g>'
        f'</svg>\n'
    )
    ET.fromstring(svg)  # Broken XML: better to fail than publish a broken image.
    return svg
