import re
from typing import Optional
from abc import ABC, abstractmethod
from gridle_parser import Cell, Colour, Gridle


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
                if char is not None:
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
    row_possibilities = []
    col_possibilities = []
    for rc in range(3):
        row_possibilities.append(possible_words(gridle, corpus, Row(gridle, rc)))
        col_possibilities.append(possible_words(gridle, corpus, Column(gridle, rc)))

    changed = True
    while changed:
        changed = False

        # remove candidates that conflict with known characters:
        for i in range(3):
            for j in range(5):
                if result[i * 2][j] is not None:
                    row_possibilities[i] = [p for p in row_possibilities[i] if p[j] == result[i * 2][j]]
                if result[j][i * 2] is not None:
                    col_possibilities[i] = [p for p in col_possibilities[i] if p[j] == result[j][i * 2]]

        # remove candidates that would use unavailable characters:
        for possibilities in (row_possibilities, col_possibilities):
            for possibility in possibilities:  # for column or row
                for candidate in possibility.copy():
                    char_bag_copy = char_bag.copy()
                    for char in candidate:
                        if char in char_bag_copy:
                            char_bag_copy.remove(char)
                        else:
                            possibility.remove(candidate)
                            changed = True
                            break

        # remove candidates that use a character which no intersecting candidate uses at this position:
        for r, row in enumerate(row_possibilities):
            for candidate in row.copy():
                for c, col in enumerate(col_possibilities):
                    # if there are intersecting candidates but none of them contain the char at the required position:
                    if col and candidate[c * 2] not in [word[r * 2] for word in col]:
                        row.remove(candidate)
                        changed = True
                        break
        for c, col in enumerate(col_possibilities):
            for candidate in col.copy():
                for r, row in enumerate(row_possibilities):
                    # if there are intersecting candidates but none of them contain the char at the required position:
                    if row and candidate[r * 2] not in [word[c * 2] for word in row]:
                        col.remove(candidate)
                        changed = True
                        break

        # fill in words if there is only one possibility:
        for rc in range(3):
            match row_possibilities[rc]:
                case [word]:
                    changed = True
                    for i, char in enumerate(word):
                        assert result[rc * 2][i] in (None, char)
                        # if it is the first character on a non-intersection or the second on an intersection tile
                        if i % 2 != 0 or not col_possibilities[i // 2]:
                            char_bag.remove(char)  # remove first occurrence
                        result[rc * 2][i] = char
                    row_possibilities[rc].clear()

            match col_possibilities[rc]:
                case [word]:
                    changed = True
                    for i, char in enumerate(word):
                        assert result[i][rc * 2] in (None, char)
                        # if it is the first character on a non-intersection or the second on an intersection tile
                        if i % 2 != 0 or not row_possibilities[i // 2]:
                            char_bag.remove(char)  # remove first occurrence
                        result[i][rc * 2] = char
                    col_possibilities[rc].clear()

    return GridleSolution(gridle, result)
