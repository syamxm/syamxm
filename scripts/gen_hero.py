#!/usr/bin/env python3
"""Render the profile hero assets from the ASCII sources in assets/.

Port of the browser renderer at syamxm.com/js/ascii3d.js so the README and the
site are generated from the same model. Standard library only.

    python3 scripts/gen_hero.py

Writes assets/hero-{dark,light}.svg and assets/wordmark-{dark,light}.svg.
"""

import math
import os
from array import array
from xml.sax.saxutils import escape

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO_ROOT, "assets")

DARK_PURPLE = "#A78BFA"
LIGHT_PURPLE = "#7C3AED"

FRAME_COUNT = 60
LOOP_SECONDS = 6.0

GLYPH_WEIGHTS = {":": 0.3, ";": 0.3, "+": 0.4, "x": 0.5, "X": 0.6, "$": 0.8, "&": 1.0}
RAMP = ".,-~:;=!*#$@"

COLUMNS = 60
DEPTH = 7.0
ASPECT = 0.5
LIGHT_DIRECTION = (-0.45, -0.65, 0.85)
AMBIENT = 0.16
DIFFUSE = 0.6
SPECULAR = 0.4
SHININESS = 10

FONT_SIZE = 10.0
CHAR_WIDTH = 6.0
LINE_HEIGHT = 10.0
FONT_STACK = "ui-monospace,'DejaVu Sans Mono','Liberation Mono','Courier New',monospace"


def read_art(name):
    with open(os.path.join(ASSETS, name), encoding="utf-8") as handle:
        text = handle.read()
    lines = text.replace("\r", "").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines


def float32_buffer(size, fill=0.0):
    """Single-precision buffer, matching the Float32Array the browser uses."""
    return array("f", [fill]) * size


def weight_grid(lines):
    height = len(lines)
    width = max(len(line) for line in lines)
    weights = float32_buffer(width * height)
    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            weights[row * width + col] = GLYPH_WEIGHTS.get(char, 0.0)
    return weights, width, height


def blur_pass(source, width, height, horizontal):
    """One axis of a separable 1-4-6-4-1 blur, edge weights renormalised."""
    kernel = (1, 4, 6, 4, 1)
    out = float32_buffer(width * height)
    for row in range(height):
        for col in range(width):
            total = 0.0
            total_weight = 0
            for offset in range(-2, 3):
                sample_row = row if horizontal else row + offset
                sample_col = col + offset if horizontal else col
                if not (0 <= sample_row < height and 0 <= sample_col < width):
                    continue
                weight = kernel[offset + 2]
                total += source[sample_row * width + sample_col] * weight
                total_weight += weight
            out[row * width + col] = total / total_weight
    return out


def normalize(x, y, z):
    length = math.hypot(x, y, z) or 1.0
    return x / length, y / length, z / length


def build_model(lines):
    """Turn the ASCII art into a two-sided point cloud with surface normals.

    Glyph weights are blurred into a height field, the height field's gradient
    gives each point a normal, and every point is mirrored through z=0 so the
    shape reads as solid from both sides while it rotates.
    """
    weights, width, height = weight_grid(lines)
    field = blur_pass(blur_pass(weights, width, height, True), width, height, False)
    peak = max(field) or 1.0

    def height_at(row, col):
        if not (0 <= row < height and 0 <= col < width):
            return 0.0
        return field[row * width + col] / peak

    y_unit = 1.0 / ASPECT
    points = []
    for row in range(height):
        for col in range(width):
            if weights[row * width + col] == 0.0:
                continue
            gradient_x = (height_at(row, col + 1) - height_at(row, col - 1)) / 2.0
            gradient_y = (height_at(row + 1, col) - height_at(row - 1, col)) / (2.0 * y_unit)
            normal = normalize(-DEPTH * gradient_x, -DEPTH * gradient_y, 1.0)
            px = col - (width - 1) / 2.0
            py = (row - (height - 1) / 2.0) * y_unit
            pz = height_at(row, col) * DEPTH
            points.append((px, py, pz, normal[0], normal[1], normal[2]))
            points.append((px, py, -pz, normal[0], normal[1], -normal[2]))

    radius = math.hypot((width - 1) / 2.0, DEPTH)
    scale = (2.0 * radius * 1.04) / COLUMNS
    rows = math.ceil((height - 1) / scale) + 1
    return points, scale, rows, y_unit


def render_frame(model, angle):
    """Rotate about the y axis, z-buffer the result, shade it, pick a glyph.

    Rotation is the standard y-axis pair applied to both position and normal:
        x' =  x*cos + z*sin
        z' = -x*sin + z*cos
    Shading is ambient + Lambert diffuse + Blinn-Phong specular, and the final
    luminance in 0..1 indexes RAMP from darkest to brightest.
    """
    points, scale, rows, y_unit = model
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    light = normalize(*LIGHT_DIRECTION)
    halfway = normalize(light[0], light[1], light[2] + 1.0)

    size = COLUMNS * rows
    depth_buffer = float32_buffer(size, -math.inf)
    luminance = float32_buffer(size)
    filled = [False] * size

    for px, py, pz, nx, ny, nz in points:
        x = px * cos_a + pz * sin_a
        z = -px * sin_a + pz * cos_a
        col = math.floor(x / scale + (COLUMNS - 1) / 2.0 + 0.5)
        row = math.floor(py / (scale * y_unit) + (rows - 1) / 2.0 + 0.5)
        if not (0 <= col < COLUMNS and 0 <= row < rows):
            continue
        index = row * COLUMNS + col
        if z <= depth_buffer[index]:
            continue
        depth_buffer[index] = z

        rotated_nx = nx * cos_a + nz * sin_a
        rotated_nz = -nx * sin_a + nz * cos_a
        diffuse = max(0.0, rotated_nx * light[0] + ny * light[1] + rotated_nz * light[2])
        specular = max(0.0, rotated_nx * halfway[0] + ny * halfway[1] + rotated_nz * halfway[2])
        luminance[index] = min(1.0, AMBIENT + DIFFUSE * diffuse + SPECULAR * (specular ** SHININESS))
        filled[index] = True

    output = []
    for row in range(rows):
        line = []
        for col in range(COLUMNS):
            index = row * COLUMNS + col
            if not filled[index]:
                line.append(" ")
                continue
            ramp_index = min(len(RAMP) - 1, int(luminance[index] * len(RAMP)))
            line.append(RAMP[ramp_index])
        output.append("".join(line).rstrip())
    return output


def text_rows(lines, y_offset=0.0):
    spans = []
    for row, line in enumerate(lines):
        if not line:
            continue
        y = y_offset + (row + 1) * LINE_HEIGHT
        width = len(line) * CHAR_WIDTH
        spans.append(
            '<tspan x="0" y="%g" textLength="%g">%s</tspan>' % (y, width, escape(line))
        )
    return "".join(spans)


def svg_open(width, height, colour):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" font-family="%s" font-size="%.1f" fill="%s">'
        % (width, height, width, height, escape(FONT_STACK, {'"': "&quot;"}), FONT_SIZE, colour)
    )


def build_spinner(model, colour, title):
    points, scale, rows, y_unit = model
    width = math.ceil(COLUMNS * CHAR_WIDTH)
    height = rows * LINE_HEIGHT
    step_percent = 100.0 / FRAME_COUNT
    frame_seconds = LOOP_SECONDS / FRAME_COUNT

    style = (
        "<style>"
        ".f{opacity:0;animation:cycle %.1fs step-end infinite}"
        "@keyframes cycle{0%%{opacity:1}%.4f%%{opacity:0}}"
        "@media(prefers-reduced-motion:reduce){.f{animation:none}.f0{opacity:1}}"
        "</style>" % (LOOP_SECONDS, step_percent)
    )

    parts = [svg_open(width, height, colour), "<title>%s</title>" % escape(title), style]
    for index in range(FRAME_COUNT):
        angle = (index / FRAME_COUNT) * 2.0 * math.pi
        delay = -((FRAME_COUNT - index) * frame_seconds)
        parts.append(
            '<g class="f f%d" style="animation-delay:%.2fs"><text xml:space="preserve">%s</text></g>'
            % (index, delay, text_rows(render_frame(model, angle)))
        )
    parts.append("</svg>")
    return "".join(parts)


BAR_THICKNESS = 1.2
BAR_X = (1.2, 3.6)
BAR_Y = (3.4, 5.4)
SEAM_OVERLAP = 0.1


def horizontal_bar(x, y, opens_right):
    if opens_right:
        return (x, y, CHAR_WIDTH - x, BAR_THICKNESS)
    return (0.0, y, x + BAR_THICKNESS, BAR_THICKNESS)


def vertical_bar(x, y, opens_down):
    if opens_down:
        return (x, y, BAR_THICKNESS, LINE_HEIGHT - y)
    return (x, 0.0, BAR_THICKNESS, y + BAR_THICKNESS)


def corner_bars(opens_right, opens_down):
    outer_x, inner_x = BAR_X if opens_right else BAR_X[::-1]
    outer_y, inner_y = BAR_Y if opens_down else BAR_Y[::-1]
    return [
        horizontal_bar(outer_x, outer_y, opens_right),
        horizontal_bar(inner_x, inner_y, opens_right),
        vertical_bar(outer_x, outer_y, opens_down),
        vertical_bar(inner_x, inner_y, opens_down),
    ]


GLYPH_BARS = {
    "═": [(0.0, BAR_Y[0], CHAR_WIDTH, BAR_THICKNESS), (0.0, BAR_Y[1], CHAR_WIDTH, BAR_THICKNESS)],
    "║": [(BAR_X[0], 0.0, BAR_THICKNESS, LINE_HEIGHT), (BAR_X[1], 0.0, BAR_THICKNESS, LINE_HEIGHT)],
    "╔": corner_bars(True, True),
    "╗": corner_bars(False, True),
    "╚": corner_bars(True, False),
    "╝": corner_bars(False, False),
}

BLOCK = "█"


def block_runs(line):
    """Merge each horizontal run of full blocks into one span, so abutting
    rectangles cannot show antialiased hairlines between them."""
    runs = []
    start = None
    for col, char in enumerate(line + " "):
        if char == BLOCK and start is None:
            start = col
        elif char != BLOCK and start is not None:
            runs.append((start, col - start))
            start = None
    return runs


def wordmark_rects(lines):
    rects = []
    for row, line in enumerate(lines):
        y = row * LINE_HEIGHT
        for start, length in block_runs(line):
            height = LINE_HEIGHT + (SEAM_OVERLAP if row < len(lines) - 1 else 0.0)
            rects.append((start * CHAR_WIDTH, y, length * CHAR_WIDTH, height))
        for col, char in enumerate(line):
            for bar_x, bar_y, bar_w, bar_h in GLYPH_BARS.get(char, ()):
                rects.append((col * CHAR_WIDTH + bar_x, y + bar_y, bar_w, bar_h))
    return rects


def build_wordmark(lines, colour, title):
    """Draw the wordmark as rectangles rather than <text>.

    The art is built from U+2550-U+2588 box and block glyphs, which the
    monospace fonts in FONT_STACK do not contain. Rendered as text inside an
    <img>, browsers fall back to a proportional font and the art collapses, so
    the eight glyphs are emitted as vector geometry instead.
    """
    width = math.ceil(max(len(line) for line in lines) * CHAR_WIDTH)
    height = math.ceil(len(lines) * LINE_HEIGHT)
    shapes = "".join(
        '<rect x="%g" y="%g" width="%g" height="%g"/>' % rect for rect in wordmark_rects(lines)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" fill="%s"><title>%s</title>%s</svg>'
        % (width, height, width, height, colour, escape(title), shapes)
    )


def write(name, content):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print("%-22s %7d bytes" % (name, len(content.encode("utf-8"))))


def main():
    model = build_model(read_art("ascii-art.txt"))
    wordmark = read_art("syamxm.txt")

    write("hero-dark.svg", build_spinner(model, DARK_PURPLE, "syamxm logo, rotating"))
    write("hero-light.svg", build_spinner(model, LIGHT_PURPLE, "syamxm logo, rotating"))
    write("wordmark-dark.svg", build_wordmark(wordmark, DARK_PURPLE, "SYAMXM"))
    write("wordmark-light.svg", build_wordmark(wordmark, LIGHT_PURPLE, "SYAMXM"))


if __name__ == "__main__":
    main()
