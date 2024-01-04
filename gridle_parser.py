import pytesseract
import numpy as np
from PIL import Image
from typing import Optional

class Colour:
    GRAY = "GRAY"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

    def get_ansi(colour: type['Colour']) -> str:
        match colour:
            case Colour.GRAY:
                return "\033[30;1m"
            case Colour.YELLOW:
                return "\033[33;1m"
            case Colour.GREEN:
                return "\033[32;1m"
            case _:
                raise Exception("Unknown colour")

class Cell:
    def __init__(self, start: tuple[int, int], end: tuple[int, int], char: str, colour: Colour):
        self.end = end
        self.start = start
        self.char = char
        self.colour = colour

    def get_centre(self) -> tuple[int, int]:
        return ((self.start[0] + self.end[0])//2, (self.start[1] + self.end[1])//2)

    def parse(img_array: np.array, start: tuple[int, int], end: tuple[int, int]) -> type['Cell']:
        start_x, start_y = start
        end_x, end_y = end
        img_array = img_array[start_y:end_y, start_x:end_x]
        colour = Cell.get_colour(img_array)

        return Cell(start, end, Cell.get_char(img_array), colour)

    def get_colour(img_array: np.array) -> Colour: # TODO
        # Calculate the average colour
        r, g, b = np.mean(img_array, axis=(0, 1))- _Colours.BACKGROUND

        # Select cell colour
        if g > 0 and r < 0 and b < 0:
            return Colour.GREEN
        elif g > 0 and r > 0 and b < 0:
            return Colour.YELLOW
        elif (r - g) ** 2 + (r - b) ** 2 >= 1:
            raise Exception("Could not parse cell colour")
        return Colour.GRAY

    def get_char(img_array: np.array) -> str:
        img_array[np.all(img_array < _Colours.GRAY, axis=-1)] = _Colours.WHITE
        img_array[~np.all(img_array == _Colours.WHITE, axis=-1)] = _Colours.BLACK
        data = pytesseract.image_to_string(Image.fromarray(img_array), config='--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        data = data.replace("\n", "")

        if len(data) != 1:
            raise Exception("Could not parse cell character")
        return data

class Gridle:
    def __init__(self, cells: list[Cell]):
        self.cells = cells

    def parse(image: Image) -> type['Gridle']:
        if image.mode != 'RGB':
            image = image.convert('RGB')

        cells = []
        img_array =  np.array(image)
        start = _find_first(img_array)
        for row in range(5):
            count = (5, 3, 5, 3, 5)[row]
            cell = start
            for i in range(count):
                end = _extract_cell(img_array, cell)
                cells.append(Cell.parse(img_array, cell, end))
                if i + 1 != count:
                    cell = _next_horizontal(img_array, cell)
            if row < 4:
                start = _next_vertical(img_array, start)

        return Gridle(cells)

    def chars(self) -> list[str]:
        return [cell.char for cell in self.cells]

    def to_grid(self) -> list[list[Optional[Cell]]]:
        rows = []
        lst = self.cells
        for l in (5, 3, 5, 3, 5):
            chunk = lst[:l]
            lst = lst[l:]
            if l == 3:
                chunk.insert(1, None)
                chunk.insert(3, None)
            rows.append(chunk)
        return rows

    def print(self):
        ANSI_RESET = "\033[0m"
        VERT_BAR = f"{ANSI_RESET}|"
        disp = f"{ANSI_RESET}┌───{'┬───' * 4}┐\n"
        for i, row in enumerate(self.to_grid()):
            disp += VERT_BAR
            for cell in row:
                if cell == None:
                    disp += "   "
                else:
                    disp += f"{Colour.get_ansi(cell.colour)} {cell.char} "
                disp += VERT_BAR
            if i != 4:
                disp += f"\n├───{'┼───' * 4}┤\n"
            else:
                disp += f"\n└───{('┴───' * 4)}┘"
        print(disp)

class _Colours:
    GRAY = (99, 99, 99)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BACKGROUND = (48, 48, 48)

def _find_first(img_array):
    width = img_array.shape[1]

    first_back =  _next_matching(img_array[:, width//2] == _Colours.BACKGROUND)
    first_y = first_back + _next_matching(img_array[first_back:, width//2] == _Colours.BLACK)

    first_x = _next_matching(img_array[first_y] == _Colours.BLACK)

    return (first_x, first_y)

def _extract_cell(img_array, start):
    start_x, start_y = start
    end_x = start_x + _next_matching(img_array[start_y, start_x:] == _Colours.BACKGROUND) - 1
    end_y = start_y + _next_matching(img_array[start_y:, end_x] == _Colours.BACKGROUND) - 1

    return (end_x, end_y)

def _next_horizontal(img_array, start):
    start_x, start_y = start
    next_back = start_x + _next_matching(img_array[start_y, start_x:] == _Colours.BACKGROUND)
    next_black = next_back + _next_matching(img_array[start_y, next_back:] == _Colours.BLACK)

    return (next_black, start_y)

def _next_vertical(img_array, start):
    start_x, start_y = start
    next_back = start_y + _next_matching(img_array[start_y:, start_x] == _Colours.BACKGROUND)
    next_black = next_back + _next_matching(img_array[next_back:, start_x] == _Colours.BLACK)

    return (start_x, next_black)

def _next_matching(condition):
        return np.nonzero(np.all(condition, axis=-1))[0][0]
