import io
import subprocess
import pytesseract
import numpy as np
from PIL import Image
from typing import List, Optional, Tuple

class Colour:
    GRAY = "GRAY"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

    def get_ansi(colour):
        match colour:
            case Colour.GRAY:
                return "\033[30;1m"
            case Colour.YELLOW:
                return "\033[33;1m"
            case Colour.GREEN:
                return "\033[32;1m"
            case _:
                raise Exception("Unknown colour")

class Gridle:
    def __init__(self, chars: List[str], colours: List[Colour], coordinates: List[Tuple]):
        self.chars = chars
        self.colours = colours
        self.coordinates = coordinates

    def _to_grid(lst):
        rows = []
        for l in (5, 3, 5, 3, 5):
            chunk = lst[:l]
            lst = lst[l:]
            if l == 3:
                chunk.insert(1, None)
                chunk.insert(3, None)
            rows.append(chunk)
        return rows

    def chars_grid(self) -> List[List[Optional[str]]]:
        return Gridle._to_grid(self.chars)

    def colours_grid(self) -> List[List[Optional[Colour]]]:
        return Gridle._to_grid(self.colours)

    def print(self):
        ANSI_RESET = "\033[0m"
        VERT_BAR = f"{ANSI_RESET}|"
        disp = f"{ANSI_RESET}┌───{'┬───' * 4}┐\n"
        for i, row in enumerate(zip(self.chars_grid(), self.colours_grid())):
            disp += VERT_BAR
            for char, colour in zip(*row):
                if char == None:
                    disp += "   "
                else:
                    disp += f"{Colour.get_ansi(colour)} {char} "
                disp += VERT_BAR
            if i != 4:
                disp += f"\n├───{'┼───' * 4}┤\n"
            else:
                disp += f"\n└───{'┴───' * 4}┘"

        print(disp)

def parse_gridle() -> Gridle:
    res = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
    if res.returncode != 0:
        raise Exception("Could not take screenshot")

    img = Image.open(io.BytesIO(res.stdout))
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # prepare for OCR
    data = np.array(img)
    data[np.all(data == _Colours.BLACK, axis=-1)] = _Colours.BACKGROUND
    data[np.all(data == _Colours.BACKGROUND, axis=-1)] = _Colours.WHITE
    data[np.all(data == _Colours.GRAY, axis=-1)] = _Colours.BLACK
    data[np.all(data == _Colours.YELLOW, axis=-1)] = _Colours.BLACK
    data[np.all(data == _Colours.GREEN, axis=-1)] = _Colours.BLACK
    img_c = Image.fromarray(data)

    # do OCR and parse colours
    chars = []
    colours = []
    coords = []
    start = _find_first(img)
    for count in (5, 3, 5, 3, 5):
        cell = start
        for _ in range(count):
            end = _extract_cell(img, cell)
            chars.append(_get_char(img_c, cell, end))
            colours.append(_get_colour(img, cell, end))
            coords.append((cell, end))
            cell = _next_cell(img, cell)
        start = _next_cell(img, start, horizontal=False)

    return Gridle(chars, colours, coords)

class _Colours:
    GRAY = (99, 99, 99)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BACKGROUND = (48, 48, 48)

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

def _get_colour(image, start, end):
    data = np.array(image.crop(start + end))

    # Calculate the average colour
    background_colour = np.array(_Colours.BACKGROUND)
    average_colour = np.mean(data, axis=(0, 1)) - background_colour
    r, g, b = average_colour

    # Select cell colour
    if g > 0 and r < 0 and b < 0:
        return Colour.GREEN
    elif g > 0 and r > 0 and b < 0:
        return Colour.YELLOW
    elif (r - g) ** 2 + (r - b) ** 2 >= 1:
        raise Exception("Could not parse cell colour")
    return Colour.GRAY

def _get_char(image, start, end):
    data = pytesseract.image_to_string(image.crop(start + end), config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    data = data.replace(" ", "").replace("\n", "")
    if data == "A":
        # Sometimes 'Z', 'Y' and 'V' are mistaken for an 'A' to avoid this, perform OCR again with better setting for those characters
        data10 = pytesseract.image_to_string(image.crop(start + end), config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        data10 = data10.replace(" ", "").replace("\n", "")
        if data == data10:
            return data
        elif len(data10) != 1:
            raise Exception("Could not parse cell character")
        return data10
    
    if len(data) != 1:
        raise Exception("Could not parse cell character")
    return data
