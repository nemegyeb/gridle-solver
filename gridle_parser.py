import io
import subprocess
import pytesseract
import numpy as np
from PIL import Image

class Colour:
    GRAY = "GRAY"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

class _Colours:
    GRAY = (99, 99, 99)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    BACKGROUND = (48, 48, 48)

def parse_gridle():
    data = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True).stdout
    img = Image.open(io.BytesIO(data))
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # prepare for OCR
    data = np.array(img)
    data[np.all(data == _Colours.GRAY, axis=-1)] = _Colours.WHITE
    data[np.all(data == _Colours.YELLOW, axis=-1)] = _Colours.WHITE
    data[np.all(data == _Colours.BLACK, axis=-1)] = _Colours.BACKGROUND
    img_c = Image.fromarray(data)

    """data = pytesseract.image_to_string(Image.fromarray(data), config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    # parse characters
    lines = data.split("\n")
    assert len(lines) > 6
    chars = []
    for line in lines[1:6]:
        assert len(line) == 5
        chars.append([c if c != ' ' else None for c in list(line)])"""

    # do OCR and parse colours
    chars = []
    colours = []
    start = _find_first(img)
    for y in range(5):
        cell = start
        row_col = []
        row_char = []
        count = 5 if y not in (1, 3) else 3
        for _ in range(count):
            end = _extract_cell(img, cell)
            row_col.append(_get_color(img, cell, end))
            row_char.append(_get_char(img_c, cell, end))
            cell = _next_cell(img, cell)
        if count == 3:
            row_char.insert(1, None)
            row_char.insert(3, None)
            row_col.insert(1, None)
            row_col.insert(3, None)
        chars.append(row_char)
        colours.append(row_col)
        start = _next_cell(img, start, horizontal=False)

    return (chars, colours)

def _find_first(image):
    width, height = image.size
    state = 0
    for y in range(height):
        rgb = image.getpixel((width//2, y))
        match state, rgb:
            case 0, _Colours.BACKGROUND:
                state = 1
            case 1, _Colours.BLACK:
                start_y = y
                break

    state = 0
    for x in range(width//2, 0, -1):
        rgb = image.getpixel((x, start_y))
        match state, rgb:
            case 0, _Colours.BACKGROUND:
                state = 1
            case 1, _Colours.BLACK:
                state = 2
            case 2, _Colours.BACKGROUND:
                state = 3
            case 3, _Colours.BLACK:
                state = 4
            case 4, _Colours.BACKGROUND:
                return (x+1, start_y)

def _extract_cell(image, start):
    width, height = image.size
    start_x, start_y = start
    for x in range(start_x, width):
        if image.getpixel((x, start_y)) == _Colours.BACKGROUND:
            end_x = x - 1
            break

    for y in range(start_y, height):
        if image.getpixel((end_x, y)) == _Colours.BACKGROUND:
            return (end_x, y - 1)

def _next_cell(image, start, horizontal=True):
    width, height = image.size
    start_x, start_y = start
    state = 0
    if horizontal:
        for x in range(start_x, width):
            rgb = image.getpixel((x, start_y))
            match state, rgb:
                case 0, _Colours.BACKGROUND:
                    state = 1
                case 1, _Colours.BLACK:
                    return (x, start_y)
    else:
        for y in range(start_y, height):
            rgb = image.getpixel((start_x, y))
            match state, rgb:
                case 0, _Colours.BACKGROUND:
                    state = 1
                case 1, _Colours.BLACK:
                    return (start_x, y)

def _get_color(image, start, end):
    data = np.array(image.crop((*start, *end)))

    # Calculate the average color
    background_color = np.array(_Colours.BACKGROUND)
    average_color = np.mean(data, axis=(0, 1)) - background_color
    r, g, b = average_color
    if g > 0 and r < 0 and b < 0:
        return Colour.GREEN
    elif g > 0 and r > 0 and b < 0:
        return Colour.YELLOW
    else:
        if not ((r - g) ** 2 + (r - b) ** 2 < 1):
            print(f"{(r - g) ** 2 + (r - b) ** 2=}, {r=}, {b=}, {g=}, image saved as /tmp/parser_fail.png")
            image.crop((*start, *end)).save("/tmp/parser_fail.png", format="png")
        assert (r - g) ** 2 + (r - b) ** 2 < 1
        return Colour.GRAY

def _get_char(image, start, end):
    data = pytesseract.image_to_string(image.crop((*start, *end)), config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    data = data.replace(" ", "").replace("\n", "")
    if data == "A":
        data10 = pytesseract.image_to_string(image.crop((*start, *end)), config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        data10 = data10.replace(" ", "").replace("\n", "")
        if data == data10:
            return data
        else:
            assert len(data10) == 1
            return data10
    else:
        if len(data) != 1:
            print(f"{len(data)=}, {data=}, image saved as /tmp/parser_fail.png")
            image.crop((*start, *end)).save("/tmp/parser_fail.png", format="png")
        assert len(data) == 1
        return data
