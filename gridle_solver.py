import re
from typing import Optional
from abc import ABC, abstractmethod
from gridle_parser import Cell, Colour, Gridle

GRAY = Colour.GRAY
YELLOW = Colour.YELLOW
GREEN = Colour.GREEN


class WordSelector(ABC):
    def __init__(self, gridle: Gridle, index: int):
        self.index = index
        self.gridle = gridle

    @abstractmethod
    def cells(self) -> list[Cell]:
        pass

    @abstractmethod
    def rows(self) -> set[int]:
        pass

    @abstractmethod
    def columns(self) -> set[int]:
        pass

    # returns a word of the other axis orthogonal to this
    @abstractmethod
    def other_axis(self, other: int) -> list[Cell]:
        pass


class Row(WordSelector):
    def cells(self) -> list[Cell]:
        return self.gridle.get_row(self.index)

    def rows(self) -> set[int]:
        return set(range(3)) - {self.index}

    def columns(self) -> set[int]:
        return set(range(3))

    # returns the column 'other'
    def other_axis(self, other: int) -> list[Cell]:
        return self.gridle.get_col(other)


class Column(WordSelector):
    def cells(self) -> list[Cell]:
        return self.gridle.get_col(self.index)

    def rows(self) -> set[int]:
        return set(range(3))

    def columns(self) -> set[int]:
        return set(range(3)) - {self.index}

    # returns the row of number 'other'
    def other_axis(self, other: int) -> list[Cell]:
        return self.gridle.get_row(other)


class GridleSolution(Gridle):
    def __init__(self, gridle: Gridle, solution: list[list[Optional[str]]]):
        cells = []
        for row_g, row_s in zip(gridle.to_grid(), solution):
            for cell, char in zip(row_g, row_s):
                if cell is not None:
                    cells.append(Cell(cell.start, cell.end, char, Colour.GREEN))

        Gridle.__init__(self, cells)

    def is_valid(self) -> bool:
        return len(self.cells) == 21


# returns all words of the 'corpus' that satisfy the requirements of the word selected by 'selector' from 'gridle'
def possible_words(gridle: Gridle, corpus: list[str], selector: WordSelector) -> list[str]:
    cells = selector.cells()

    rows = selector.rows()
    columns = selector.columns()

    # all gray characters not in this word
    rest = set().union(*map(gridle.get_row, rows), *map(gridle.get_col, columns))
    available_non_intersect = set(filter(Cell.is_gray, rest))

    # yellow chars could also be in an intersecting word
    yellows = set(filter(Cell.is_yellow, cells))

    # list of gray chars that do not also occurr as yellow in this word
    disallowed = set(filter(Cell.is_gray, cells)) - yellows

    # build a regex pattern which candidates have to match
    pattern = ""
    for i, cell in enumerate(cells):
        if cell.is_green():
            pattern += str(cell)
        else:
            # match for any available gray char and yellows of the same word
            available = available_non_intersect.union(filter(Cell.is_yellow, cells))

            # remove the chat at this position and other gray chars in this word
            available -= disallowed.union({cell})

            if i % 2 == 0:
                # also allow yellows of intersecting rows/columns
                available = available.union(filter(Cell.is_yellow, selector.other_axis(i // 2)))

            available = "".join(map(str, available))  # stringify all cells
            pattern += f"[{available}]"

    p = re.compile(pattern)
    regex_filtered_words = list(filter(p.match, corpus))

    # yellow chars that need to be in the word
    definite_yellows = set(filter(Cell.is_yellow, [cells[1], cells[3]]))

    # look for words that contain all the given yellow chars at non-green positions
    possible_words = []
    for word in regex_filtered_words:
        # the same word but green chars removed
        word_without_greens = list(word)
        for cell in cells:
            if cell.is_green():
                word_without_greens.remove(cell.char)

        for c in definite_yellows:
            if c.char not in word_without_greens:
                break
        else:
            possible_words.append(word)

    return possible_words


def solve_gridle(gridle: Gridle, corpus: list[str]) -> GridleSolution:
    result = [[None] * 5, [None] * 5, [None] * 5, [None] * 5, [None] * 5]
    char_bag = gridle.chars()
    row_possibilities = [None] * 5
    col_possibilities = [None] * 5
    for rc in (0, 1, 2):
        row_possibilities[rc * 2] = possible_words(gridle, corpus, Row(gridle, rc))
        col_possibilities[rc * 2] = possible_words(gridle, corpus, Column(gridle, rc))

    changed = True
    while changed:
        changed = False

        # remove candidates that conflict with known characters:
        for r in range(5):
            for c in range(5):
                if result[r][c] is not None:
                    if r in (0, 2, 4):
                        row_possibilities[r] = [p for p in row_possibilities[r] if p[c] == result[r][c]]
                    if c in (0, 2, 4):
                        col_possibilities[c] = [p for p in col_possibilities[c] if p[r] == result[r][c]]

        # remove candidates that would use unavailable characters:
        for possibilities in (row_possibilities, col_possibilities):
            for rc in (0, 2, 4):  # for column or row
                for candidate in possibilities[rc].copy():
                    char_bag_copy = char_bag.copy()
                    for char_index in range(5):
                        if candidate[char_index] in char_bag_copy:
                            char_bag_copy.remove(candidate[char_index])
                        else:
                            possibilities[rc].remove(candidate)
                            changed = True
                            break

        # remove candidates that use a character which no intersecting candidate uses at this position:
        for r in (0, 2, 4):
            for candidate in row_possibilities[r].copy():
                for c in (0, 2, 4):
                    # if there are intersecting candidates but none of them contain the char at the required position:
                    if col_possibilities[c] and candidate[c] not in [x[r] for x in col_possibilities[c]]:
                        row_possibilities[r].remove(candidate)
                        changed = True
                        break
        for c in (0, 2, 4):
            for candidate in col_possibilities[c].copy():
                for r in (0, 2, 4):
                    # if there are intersecting candidates but none of them contain the char at the required position:
                    if row_possibilities[r] and candidate[r] not in [x[c] for x in row_possibilities[r]]:
                        col_possibilities[c].remove(candidate)
                        changed = True
                        break

        # fill in words if there is only one possibility:
        for rc in (0, 2, 4):
            if len(row_possibilities[rc]) == 1:
                changed = True
                word = row_possibilities[rc][0]
                for char_index in range(5):
                    assert result[rc][char_index] in (None, word[char_index])
                    if (
                        char_index in (1, 3) or not col_possibilities[char_index]
                    ):  # if it is the second word on an intersection or the first word on a non-intersection tile
                        char_bag.remove(word[char_index])  # remove first occurrence
                    result[rc][char_index] = word[char_index]
                row_possibilities[rc] = []

            if len(col_possibilities[rc]) == 1:
                changed = True
                word = col_possibilities[rc][0]
                for char_index in range(5):
                    assert result[char_index][rc] in (None, word[char_index])
                    if (
                        char_index in (1, 3) or not row_possibilities[char_index]
                    ):  # if it is the second word on an intersection or the first word on a non-intersection tile
                        char_bag.remove(word[char_index])  # remove first occurrence
                    result[char_index][rc] = word[char_index]
                col_possibilities[rc] = []

    return GridleSolution(gridle, result)
