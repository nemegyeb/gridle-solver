import pytesseract
import numpy as np
from PIL import Image
from enum import auto, Enum
from typing import Optional, Self


class Colour(Enum):
    GRAY = auto()
    YELLOW = auto()
    GREEN = auto()

    def get_ansi(colour: Self) -> str:
        match colour:
            case Colour.GRAY:
                return "\033[30;1m"
            case Colour.YELLOW:
                return "\033[33;1m"
            case Colour.GREEN:
                return "\033[32;1m"
            case _:
                raise Exception("Unknown colour")


class GameColours:
    GRAY = (99, 99, 99)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    BACKGROUND = (48, 48, 48)


class Cell:
    def __init__(self, start: tuple[int, int], end: tuple[int, int], char: str, colour: Colour):
        self.end = end
        self.start = start
        self.char = char
        self.colour = colour

    def __format__(self, format_spec: str) -> str:
        return format(f"{Colour.get_ansi(self.colour)}{self.char}\033[0m", format_spec)

    def get_centre(self) -> tuple[int, int]:
        return ((self.start[0] + self.end[0]) // 2, (self.start[1] + self.end[1]) // 2)

    def parse(img_array: np.ndarray, start: tuple[int, int], end: tuple[int, int]) -> Self:
        start_x, start_y = start
        end_x, end_y = end
        img_array = img_array[start_y:end_y, start_x:end_x]
        colour = Cell.get_colour(img_array)

        return Cell(start, end, Cell.get_char(img_array), colour)

    def get_colour(img_array: np.ndarray) -> Colour:
        # Calculate the average color of non-backgroud colours
        valid = img_array[~np.all(img_array <= GameColours.BACKGROUND, axis=-1)]
        mean = valid.mean(axis=0)

        # select closest colour from possibilities
        colours = np.array([GameColours.GRAY, GameColours.YELLOW, GameColours.GREEN])
        index = np.linalg.norm(colours - mean, axis=1).argmin()

        # the colour must be present in the image
        if not (valid == colours[index]).all(axis=-1).any():
            raise Exception("Could not parse cell colour")

        return [Colour.GRAY, Colour.YELLOW, Colour.GREEN][index]

    def get_char(img_array: np.ndarray) -> str:
        img_array[np.all(img_array < GameColours.GRAY, axis=-1)] = GameColours.WHITE
        img_array[~np.all(img_array == GameColours.WHITE, axis=-1)] = GameColours.BLACK
        data = pytesseract.image_to_string(
            Image.fromarray(img_array), config="--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )
        data = data.replace("\n", "")

        if len(data) != 1:
            raise Exception("Could not parse cell character")
        return data


class Gridle:
    def __init__(self, cells: list[Cell]):
        self.cells = cells

    def parse(image: Image) -> Self:
        if image.mode != "RGB":
            image = image.convert("RGB")

        img = _GridleImage(image)
        start = img.find_first_cell()
        cells = img.parse_row(start, 5)
        for count in (3, 5, 3, 5):
            start = img.next_vertical(start)
            cells.extend(img.parse_row(start, count))
        return Gridle(cells)

    def chars(self) -> list[str]:
        return [cell.char for cell in self.cells]

    def to_grid(self) -> list[list[Optional[Cell]]]:
        rows = []
        lst = self.cells
        for count in (5, 3, 5, 3, 5):
            chunk = lst[:count]
            lst = lst[count:]
            if count == 3:
                chunk.insert(1, None)
                chunk.insert(3, None)
            rows.append(chunk)
        return rows

    def get_row(self, row) -> list[Cell]:
        if row not in (0, 1, 2):
            raise Exception("Gridle only has 3 rows")
        return self.cells[row * 8 : row * 8 + 5]

    def get_col(self, col) -> list[Cell]:
        if col not in (0, 1, 2):
            raise Exception("Gridle only has 3 columns")
        return [cell for i, cell in enumerate(self.cells) if i in (2 * col, 5 + col, 8 + 2 * col, 13 + col, 16 + 2 * col)]

    def print(self):
        VERT_BAR = "|"
        disp = f"┌───{'┬───' * 4}┐\n"
        for i, row in enumerate(self.to_grid()):
            disp += VERT_BAR
            for cell in row:
                if cell is None:
                    disp += "   "
                else:
                    disp += f" {cell} "
                disp += VERT_BAR
            if i != 4:
                disp += f"\n├───{'┼───' * 4}┤\n"
            else:
                disp += f"\n└───{('┴───' * 4)}┘"
        print(disp)


class _GridleImage:
    def __init__(self, image):
        self.img_array = np.array(image)

    def find_first_cell(self):
        width = self.img_array.shape[1]

        first_back = _next_background(self.img_array[:, width // 2])
        first_y = first_back + _next_black(self.img_array[first_back:, width // 2])

        first_x = _next_black(self.img_array[first_y])

        return (first_x, first_y)

    def parse_row(self, start, length):
        row = []
        for i in range(length):
            end = self.extract_cell(start)
            row.append(Cell.parse(self.img_array, start, end))
            if i + 1 < length:
                start = self.next_horizontal(start)
        return row

    def extract_cell(self, start):
        start_x, start_y = start
        end_x = start_x + _next_background(self.img_array[start_y, start_x:]) - 1
        end_y = start_y + _next_background(self.img_array[start_y:, end_x]) - 1

        return (end_x, end_y)

    def next_horizontal(self, start):
        start_x, start_y = start
        next_back = start_x + _next_background(self.img_array[start_y, start_x:])
        next_black = next_back + _next_black(self.img_array[start_y, next_back:])

        return (next_black, start_y)

    def next_vertical(self, start):
        start_x, start_y = start
        next_back = start_y + _next_background(self.img_array[start_y:, start_x])
        next_black = next_back + _next_black(self.img_array[next_back:, start_x])

        return (start_x, next_black)


def _next_matching(condition):
    return np.nonzero(np.all(condition, axis=-1))[0][0]


def _next_background(area):
    return _next_matching(area == GameColours.BACKGROUND)


def _next_black(area):
    return _next_matching(area == GameColours.BLACK)
