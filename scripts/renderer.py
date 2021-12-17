"""
Program used to render Corruption(s*).
Note: Does not support Deviations.
Version 0.1
Author: @tbql#3063

Usage:
python -m scripts.render <token_id> <insight> <output_path> [--print_ascii]

Example:
python -m scripts.render 836 1000 output.svg
"""
import argparse
import sys

import numpy as np
from web3 import Web3


BORDERS = ['/', '$', '|', '8', '_', '?', '#', '%', '^', '~', ':']

CHECKERS = ['|', '-', '=', '+', '\\', ':', '~']

PHRASES = [
    'GENERATION',
    'INDIVIDUAL',
    'TECHNOLOGY',
    'EVERYTHING',
    'EVERYWHERE',
    'UNDERWORLD',
    'ILLUMINATI',
    'TEMPTATION',
    'REVELATION',
    'CORRUPTION',
]

FG_COLORS = [
    '#022FB7',
    '#262A36',
    '#A802B7',
    '#3CB702',
    '#B76F02',
    '#B70284',
]

BG_COLORS = [
    '#0D1302',
    '#020A13',
    '#130202',
    '#1A1616',
    '#000000',
    '#040A27',
]

MODULI = {
    'BORDER': 11,
    'CORRUPTOR': 11,
    'PHRASE': 10,
    'CHECKER': 7,
    'CORRUPTION': 1024,
    'BGCOLOR': 6,
    'FGCOLOR': 6,
}

Y_LOOKUP = [
    20,
    31,
    42,
    53,
    64,
    75,
    86,
    97,
    108,
    119,
    130,
    141,
    152,
    163,
    174,
    185,
    196,
    207,
    218,
    229,
    240,
    251,
    262,
    273,
    284,
    295,
    306,
    317,
    328,
    339,
    350,
]

FONT = ('data:font/otf;base64,T1RUTwAJAIAAAwAQQ0ZGIA45LnsAAAScAAAcDk9TLzKYLsiI'
        'AAABsAAAAGBjbWFwTWBSjwAAA6gAAADUaGVhZB0E8IMAAACkAAAANmhoZWEGQgGTAAABj'
        'AAAACRobXR4DvYKnwAAANwAAACubWF4cABVUAAAAACcAAAABm5hbWWF3C/5AAACEAAAAZ'
        'Vwb3N0/4YAMgAABHwAAAAgAABQAABVAAAAAQAAAAEAAI9iLoJfDzz1AAMD6AAAAADdyta'
        'UAAAAAN3K1pQAAP8CAlgDdQAAAAcAAgAAAAAAAAH0AF0CWAAAABAAZABBAFAAawB1ADUA'
        'PAA8AFQAVQBaADwARgAwAGQAMABkAEsAKAA8AA4ADwAUAAkANwBLAAIAPAA4AD8AWABFA'
        'AQAaQA7ABgARgApABIAOQAVADwAQgBUAB8AGQArAAoALgAuAFQANwBVAE4AWAAsAFMAPQ'
        'BFAEsAPQDpAOkANgAeAFYAUgCBADgBCgBhADAARABEAE4AIwAcAAAAMgAAAAAATgAAAAE'
        'AAAPo/zgAAAJYAAAAAAJYAAEAAAAAAAAAAAAAAAAAAAACAAQCVgGQAAUACAKKAlgAAABL'
        'AooCWAAAAV4AMgD6AAAAAAAAAAAAAAAAAAAAAwAAMEAAAAAAAAAAAFVLV04AwAAgJcgDI'
        'P84AMgD6ADIQAAAAQAAAAAB9AK8AAAAIAAAAAAADQCiAAEAAAAAAAEACwAAAAEAAAAAAA'
        'IABwALAAEAAAAAAAQACwAAAAEAAAAAAAUAGAASAAEAAAAAAAYAEwAqAAMAAQQJAAEAFgA'
        '9AAMAAQQJAAIADgBTAAMAAQQJAAMAPABhAAMAAQQJAAQAFgA9AAMAAQQJAAUAMACdAAMA'
        'AQQJAAYAJgDNAAMAAQQJABAAFgA9AAMAAQQJABEADgBTQ29ycnVwdGlvbnNSZWd1bGFyV'
        'mVyc2lvbiAxLjAwMDtGRUFLaXQgMS4wQ29ycnVwdGlvbnMtUmVndWxhcgBDAG8AcgByAH'
        'UAcAB0AGkAbwBuAHMAUgBlAGcAdQBsAGEAcgAxAC4AMAAwADAAOwBVAEsAVwBOADsAQwB'
        'vAHIAcgB1AHAAdABpAG8AbgBzAC0AUgBlAGcAdQBsAGEAcgBWAGUAcgBzAGkAbwBuACAA'
        'MQAuADAAMAAwADsARgBFAEEASwBpAHQAIAAxAC4AMABDAG8AcgByAHUAcAB0AGkAbwBuA'
        'HMALQBSAGUAZwB1AGwAYQByAAAAAAAAAgAAAAMAAAAUAAMAAQAAABQABADAAAAAKAAgAA'
        'QACAAgACUAKwAvADkAOgA9AD8AWgBcAF8AegB8AH4AoCISJZMlniXI//8AAAAgACMAKwA'
        'tADAAOgA9AD8AQQBcAF4AYQB8AH4AoCISJZElniXI////4QAAAB8AAAAGAAcADwAD/8H/'
        '6QAA/7v/zP/P/2HeOdrA2rLajAABAAAAJgAAACgAAAAAAAAAAAAAAAAAIAAAAAAAAAAAA'
        'AAAAAAAAAAAAABDAEkATwBGAEAARABOAEcAAwAAAAAAAP+DADIAAAAAAAAAAAAAAAAAAA'
        'AAAAAAAAEABAIAAQEBFENvcnJ1cHRpb25zLVJlZ3VsYXIAAQEBJPgPAPggAfghAvgYBPs'
        'qDAOL+5L47PoJBfciD/diEascGWASAAcBAQgPFBsiMz51bmkyNTlFbHRzaGFkZXNoYWRl'
        'ZGtzaGFkZXVuaTI1Qzhjb3B5cmlnaHQgbWlzc2luZ0NvcnJ1cHRpb25zAAABAAEAACIZA'
        'EIZABEJAA8AABsAACAAAAQAABAAAD0AAA4AAEAAAF0AAAUAAAwAAKYAAB4AAF8AAD8AAA'
        'YAAYcEAFUCAAEA3QDeARYBlQH4Ak0CcQKTAvcDHwNAA3IDpQPDBAoEPARoBLIFDQVXBdg'
        'GHgZVBn4GzwcLBzIHUwfSCCAIbwjbCTgJjAntCikKUgqUCs0K+wtnC6oL7QxQDJgM4w08'
        'DXkNzg33DkEOeQ7DDuEPQw9qD7IQAhA2EIIQ6REFEYYR6RH4EiASixLnEwATGRMtEz8TV'
        'hPjFAMUFRQ0FHIUlxU0FVsVjRZFF6QX5CD7XNCsuqyirLqsx6yjw6GtoqywcKaspq2vra'
        'WssKzOEujVQfdjJ6ytrGr3Iz7YE/++UPgu+1wV+nwHE/++gPvR/nwGE/+/YNXQFawH0bo'
        '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'
        'NFbq9XAcgCrq9XAdZ90wqCv3UBLsiClsGKAogCkgKKAogCroiClwGKAogCroiClwGKAog'
        'CroiClwGKAo9Cv3UBLsnClsmCrsHE7/9lL1bJgq6JwpcJgq6JwpcJgq6JwpcJgq5JwpdB'
        'v6NBLq9XAdECi4KWfdMFbsHJAq9WwYuCkQK/dQEuyIKWwYkCiAKSAokCiAKuiIKXAYkCi'
        'AKuiIKXAYkCiAKuiIKXAYkCj0KDpR2Adn4UQP3v/jpFXJda1tlWFhGYVZqZr9LqmSUfrJ'
        'Xq1+kZpl2lnmUeqS5rsC4xsHTsrykpQhPziL3HlDuCA57m/iIm/dMm9+bBvtsmwceoDf/'
        'DAmLDAv47BT48xWrEwA6AgABAAYADgAVABkAHgAnAC8ANAA5AD0ASQBYAGAAZwBsAHIAe'
        'AB+AIQAiQCVAJoAoQCoAK8AtgC8AMIAyADSANoA4ADzAP4BBQEaASEBQAFRAVcBXQF0AY'
        'cBmgGqAbQBugHGAcwB0wHdAecB6wH1Af8CCAIRAhZZ900VCwYT//2gWQYLBxO//aS9C/l'
        'QFQsTv/2oCyAKur1cByAKCwYTv/2kIAoLBy4KvQsTv/3ECyMKSAsVu71bByUKur1cBwtZ'
        'BvcdBL27WQb3HQROCgu9uyEK9x0ECwYTX/2ivQsTv/2UCxP/+6C9CwcT/35oCxP//ZC9C'
        '4vO+ALOCwZZClkLUArv/rsVQgq6KwoL/gM/CgtBCr27KwoLBhOf/qRZC6B2+VB3AQsF9x'
        'nMSAYLBhP/f2ALf9X41NULBL26WQYLIAq5IgpdBkAKC1AKvf67QQoLFb27KwoL/o0Eur1'
        'cByUKur1cB1n3TCoKCxVCCrorCr3+AxULTgr3HgS9CwQT//1gvbohCvceBBP//WC9uiEK'
        'C00KLgpNCgv3b0n3I/tP+z87+xb7fB7jFvdYvef3BfcVr/sb+y0LUQpcNwr7HgYTn/2kv'
        'Vw3Cgv7RrpJCgu7IgpbBgu4u7i6uLu4uri6uLu4uri6ubq4urm5CxVopnCwsqimrq9uqW'
        'RmcG1nHg4VZKVvs7akp7K2cqNgY3FzYB4LG/tHMDP7P/tH0Dn3LNe4CyAKugckCr1cBgt'
        'YCrpZBgsGsfcyBUYGZfsyBQsEvblZBgsGE5/9pL0L+wUGE/+/YPs6C72Lvb29vb2LvQsE'
        'WAoL4wPv+UkV/UneC0rOBpBxjlFxGgu9+VEVXL26Bwu9ulkG9x4EvQsTX/2kCwAA')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('token_id', type=int)
    parser.add_argument('insight', type=int)
    parser.add_argument('output_path')
    parser.add_argument('--print_ascii', action='store_true')
    args = parser.parse_args()

    if not (0 <= args.token_id < 4196):
        sys.exit('Token ID must be a non-negative integer less than 4196')
    if args.insight < 1:
        sys.exit('Insight value must be a positive integer')

    canvas, color_canvas, side_canvas, attr = draw(args.token_id, args.insight)
    if args.print_ascii:
        print(render_ascii(canvas, color_canvas, side_canvas))

    svg = render_svg(canvas, color_canvas, side_canvas,
                     args.token_id, args.insight, *attr)
    with open(args.output_path, 'w') as f:
        f.write(svg)


def draw(token_id, insight):
    # Determine properties of Corruption
    border = BORDERS[property_value('BORDER', token_id)]
    corruptor = BORDERS[property_value('CORRUPTOR', token_id)]
    phrase = PHRASES[property_value('PHRASE', token_id)]
    checker = CHECKERS[property_value('CHECKER', token_id)]
    iterations = property_value('CORRUPTION', token_id)
    fg_color = property_value('FGCOLOR', token_id)
    bg_color = BG_COLORS[fg_color]
    secret_phrase = PHRASES[fg_color + 4]
    fg_color = FG_COLORS[property_value('BGCOLOR', token_id)]

    # Draw border
    canvas = np.full((31, 31), '.')
    canvas[0, :] = border
    canvas[-1, :] = border
    canvas[:, 0] = border
    canvas[:, -1] = border

    # Draw center image
    draw_circle(canvas, phrase[0], 15, 15, 12)
    draw_circle(canvas, phrase[1], 15, 15, 11)
    if insight < 20:
        for i in range(2, 10):
            draw_circle(canvas, phrase[i], 15, 15, 12 - i)

    # Add corruptions
    for i in range(iterations):
        x = coordinate('X', token_id, i) % 30
        y = coordinate('Y', token_id, i) % 30
        canvas[y, x] = corruptor

    # Draw insight text
    length = 8 + len(str(insight))
    canvas[-1, 31 - length:] = list(f'INSIGHT {insight}')

    # Draw middle box
    for i in range(10, 0, -1):
        if insight >= i * 2:
            draw_middle_box(canvas, (phrase[i - 1], checker), i)

    # Draw additional elements if insight is >= 20
    color_canvas = None
    side_canvas = None
    if insight >= 20:
        color_canvas = np.full((31, 31), ' ')
        for i in range(insight // 4):
            x = coordinate('X2', token_id, i) % 30
            y = coordinate('Y2', token_id, i) % 29
            color_canvas[y, x] = border if i % 2 == 0 else corruptor
            canvas[y, x] = ' '

        side_canvas = color_canvas[:6, :].copy()
        side_canvas[0, :] = '|'
        side_canvas[-1, :] = '|'
        side_canvas[:6, 0] = '|'
        side_canvas[:6, -1] = '|'
        side_canvas[0, 2:12] = list(' CONCEPTS ')
        side_canvas[2, 2:14] = list(f'+ {phrase}')
        side_canvas[3, 2:14] = list(f'+ {secret_phrase}')

    return canvas, color_canvas, side_canvas, (bg_color, fg_color)


def render_ascii(canvas, color_canvas=None, side_canvas=None):
    if color_canvas is None:
        full_canvas = canvas
    else:
        full_canvas = np.full((31, 64), ' ')
        full_canvas[:31, :31] = canvas
        full_canvas[:6, 33:] = side_canvas
        for y in range(canvas.shape[0]):
            for x in range(canvas.shape[1]):
                if color_canvas[y, x] != ' ':
                    full_canvas[y, x] = color_canvas[y, x]

    return '\n'.join([''.join(line) for line in full_canvas])


def render_svg(canvas, color_canvas, side_canvas,
               token_id, insight, bg_color, fg_color):
    # Generate the SVG code for the main canvas
    canvas_output = ''
    for i, line in enumerate(canvas):
        text = ''.join(line).replace(' ', '&#x000A0;').replace('.', '&#x0002e;')
        canvas_output += f'<text x="10" y="{Y_LOOKUP[i]}" class="base">{text}</text>'

    # Generate the SVG code for the color overlay and side canvas
    if color_canvas is not None:
        for i in range(30):
            color = FG_COLORS[((token_id + i) * i * 41) % 6]
            text = ''.join(color_canvas[i]).replace(' ', '&#x000A0;')
            canvas_output += f'<text x="10" y="{Y_LOOKUP[i]}" class="base" style="fill: {color}">{text}</text>'
        canvas_output += '<g transform="translate(200 0)">'
        for i in range(6):
            text = ''.join(side_canvas[i]).replace(' ', '&#x000A0;')
            canvas_output += f'<text x="10" y="{Y_LOOKUP[i]}" class="base">{text}</text>'
        canvas_output += '</g>'

    # Generate the full SVG code
    width = 820 if color_canvas is None else 1640
    canvas_width = 205 if color_canvas is None else 410
    svg_bg_color = bg_color if insight > 2 else secret_phrase
    svg_output = (
        '<svg xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMin meet" viewBox="0 0 ' + str(width) + ' 1460">'
          '<style>'
            '@font-face { font-family: CorruptionsFont; src: url("' + FONT + '") format("opentype"); } '
            '.base { fill: ' + fg_color + '; font-family: CorruptionsFont; font-size: 10px; }'
          '</style>'
          '<g transform="scale(4 4)">'
            '<rect width="' + str(canvas_width) + '" height="365" fill="' + svg_bg_color + '" />'
            + canvas_output +
          '</g>'
        '</svg>'
    )
    return svg_output


def draw_partial_circle(canvas, fill_value, x, y, rx, ry):
    canvas[y + ry, x + rx] = fill_value
    canvas[y + ry, x - rx] = fill_value
    canvas[y - ry, x + rx] = fill_value
    canvas[y - ry, x - rx] = fill_value
    canvas[y + rx, x + ry] = fill_value
    canvas[y + rx, x - ry] = fill_value
    canvas[y - rx, x + ry] = fill_value
    canvas[y - rx, x - ry] = fill_value


def draw_circle(canvas, fill_value, x, y, radius):
    # Bresenham’s circle drawing algorithm
    rx = 0
    ry = radius
    d = 3 - 2 * radius
    draw_partial_circle(canvas, fill_value, x, y, rx, ry)
    while ry >= rx:
        rx += 1
        if d > 0:
            ry -= 1
            d += 4 * (rx - ry) + 10
        else:
            d += 4 * rx + 6
        draw_partial_circle(canvas, fill_value, x, y, rx, ry)


def draw_middle_box(canvas, fill_values, size):
    d = 15 - size
    length = size * 2 + 1
    for iy in range(length):
        for ix in range(length):
            canvas[d + iy, d + ix] = fill_values[((d + iy) + (d + ix)) % 2]


def property_value(name, token_id):
    b = Web3.solidityKeccak(['string', 'uint256'], [name, token_id])
    return int.from_bytes(b, 'big') % MODULI[name]


def coordinate(name, token_id, salt):
    b = Web3.solidityKeccak(['string', 'uint256', 'uint256'], [name, salt, token_id])
    return int.from_bytes(b, 'big')


if __name__ == '__main__':
    sys.exit(main())