"""Marcador con bio, pantalla de misión cumplida y créditos en bucle."""
from collections import Counter
from datetime import date
from html import escape
import re

ALTO_MARCADOR = 28
PAUSA_MS = 6000
EXITO_MS = 4000  # El resto de la pausa muestra el reinicio.
ANIMACION = re.compile(r"<animate(?:Transform)?\b[^>]*>", re.S)
INICIO_DATOS = '<text x="548" y="66"'
FIN_DATOS = '<rect x="548" y="262"'
SEGUNDOS_POR_LINEA = 1.6
ALTO_LINEA = 22


def edad(nacimiento, hoy):
    """Años cumplidos; nacimiento en formato AAAA-MM-DD."""
    nacido = date.fromisoformat(nacimiento)
    return hoy.year - nacido.year - ((hoy.month, hoy.day) < (nacido.month, nacido.day))


def alargar_ciclo(galaga):
    """Mantiene el tablero vacío PAUSA_MS al final del ciclo. Devuelve (svg, ciclo original, ciclo nuevo) en ms."""
    tags = [t for t in ANIMACION.findall(galaga) if "keyTimes=" in t]
    duraciones = Counter(re.search(r'dur="(\d+)ms"', t).group(1) for t in tags if re.search(r'dur="\d+ms"', t))
    if not duraciones:
        raise ValueError("Galaga no tiene un ciclo reconocible")
    ciclo = int(duraciones.most_common(1)[0][0])
    nuevo = ciclo + PAUSA_MS

    def ajustar(m):
        tag = m.group(0)
        if f'dur="{ciclo}ms"' not in tag:
            return tag
        tiempos = re.search(r'keyTimes="([^"]+)"', tag)
        valores = re.search(r'values="([^"]+)"', tag)
        if not tiempos or not valores:
            raise ValueError("animación de Galaga sin keyTimes o values")
        t = [float(x) for x in tiempos.group(1).split(";")]
        v = valores.group(1).split(";")
        if len(t) != len(v) or t[-1] != 1:
            raise ValueError("animación de Galaga con formato inesperado")
        escalados = ";".join(f"{x * ciclo / nuevo:.6g}" for x in t) + ";1"
        tag = tag.replace(tiempos.group(0), f'keyTimes="{escalados}"')
        tag = tag.replace(valores.group(0), f'values="{valores.group(1)};{v[-1]}"')
        return tag.replace(f'dur="{ciclo}ms"', f'dur="{nuevo}ms"')

    return ANIMACION.sub(ajustar, galaga), ciclo, nuevo


def marcador(y, ancho, lvl, score):
    base = y + 19

    def dato(x, etiqueta, valor):
        return (f'<text x="{x}" y="{base}" class="ra-mb" style="font-size:14px">'
                f'<tspan fill="#ff5f57">{etiqueta} </tspan><tspan fill="#fff">{valor}</tspan></text>')

    return (
        f'<g class="ra-term"><rect y="{y}" width="{ancho}" height="{ALTO_MARCADOR}" fill="#000"/>'
        f'{dato(20, "LVL", lvl)}{dato(140, "SCORE", score)}{dato(290, "CLASS", "ENGINEER")}{dato(470, "FACTION", "HORDE")}'
        f'<text x="{ancho - 20}" y="{base}" text-anchor="end" class="ra-mb" fill="#febc2e" style="font-size:14px">INSERT COIN'
        f'<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></text></g>'
    )


def pantalla_final(y, ancho, alto, ciclo, nuevo):
    """Aparece justo cuando cae el último bloque, durante la pausa de alargar_ciclo."""
    inicio = ciclo / nuevo
    cambio = (ciclo + EXITO_MS) / nuevo
    centro = ancho / 2

    def fase(texto, color, tam, valores, tiempos):
        return (f'<text x="{centro:g}" y="{y + alto / 2 + tam / 3:g}" text-anchor="middle" class="ra-mb" fill="{color}" '
                f'style="font-size:{tam}px" opacity="0">{texto}<animate attributeName="opacity" values="{valores}" '
                f'keyTimes="{tiempos}" calcMode="discrete" dur="{nuevo}ms" repeatCount="indefinite"/></text>')

    return (
        '<g class="ra-term">'
        + fase("ALL BUGS CLEARED", "#7cff9b", 40, "0;1;0", f"0;{inicio:.6g};{cambio:.6g}")
        + fase("DEPLOYING TO PROD...", "#febc2e", 28, "0;1", f"0;{cambio:.6g}")
        + '</g>'
    )


def datos_github(terminal):
    """Saca commits y año de alta del terminal; sin ellos falla y se conserva la última imagen buena."""
    commits = re.search(r'Commits</tspan><tspan[^>]*>: ([\d,]+)', terminal)
    alta = re.search(r'Since</tspan><tspan[^>]*>: (\d{4})', terminal)
    if not commits or not alta:
        raise ValueError("el terminal no muestra commits y año de alta")
    return commits.group(1), alta.group(1)


def creditos(terminal):
    """Sustituye la columna de datos del terminal por créditos en bucle."""
    commits, alta = datos_github(terminal)
    inicio, fin = terminal.find(INICIO_DATOS), terminal.find(FIN_DATOS)
    if inicio < 0 or fin < inicio:
        raise ValueError("el terminal no tiene la columna de datos esperada")
    lineas = (
        "Directed by Adrián González", "Screenplay by AI", "Script supervisor: Claude", f"Starring {commits} commits",
        "Special effects: Angular", "Typed in TypeScript", "Stunts: Spring Boot", "Cold starts by AWS Lambda",
        "Legacy scenes: PHP", "Faction: Horde", "Weather: Donostia rain", "Zinemaldia: out of office",
        f"On GitHub since {alta}", "No bugs were harmed",
    )
    arriba, alto = 80, 170
    texto = "".join(
        f'<text x="680" y="{arriba + i * ALTO_LINEA}" text-anchor="middle" class="ra-m ra-fg">{escape(l)}</text>'
        for i, l in enumerate(lineas)
    )
    recorrido = alto + len(lineas) * ALTO_LINEA
    columna = (
        '<text x="548" y="66" class="ra-m"><tspan class="ra-acc">$</tspan><tspan class="ra-dim"> ./credits</tspan></text>'
        f'<clipPath id="creditos-clip"><rect x="521" y="{arriba - 4}" width="319" height="{alto}"/></clipPath>'
        f'<g clip-path="url(#creditos-clip)"><g><animateTransform attributeName="transform" type="translate" '
        f'values="0 {alto};0 {alto - recorrido}" dur="{recorrido / ALTO_LINEA * SEGUNDOS_POR_LINEA:g}s" '
        f'repeatCount="indefinite"/>{texto}</g></g>'
    )
    return terminal[:inicio] + columna + terminal[fin:]
