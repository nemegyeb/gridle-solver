import re
from gridle_parser import Cell, Colour, Gridle

GRAY = Colour.GRAY
YELLOW = Colour.YELLOW
GREEN = Colour.GREEN


# pick a row list or column list from the gridle
def pick_list(gridle, row=None, column=None):
    assert (row is None) != (column is None)  # exactly one of the two is given
    assert row in (None, 0, 2, 4)
    assert column in (None, 0, 2, 4)

    if row is not None:
        return gridle[row]
    else:
        return [row_list[column] for row_list in gridle]


# returns a string containing all the yellow chars in the row and column that intersect at (row,column)
def available_intersect(gridle_chars, gridle_colors, row, column):
    if row in (1, 3) or column in (1, 3):  # not an intersection
        return ""

    row_chars = pick_list(gridle_chars, row=row)
    row_colors = pick_list(gridle_colors, row=row)
    col_chars = pick_list(gridle_chars, column=column)
    col_colors = pick_list(gridle_colors, column=column)

    yellows = ""
    for i in range(5):
        if row_colors[i] == YELLOW:
            yellows += row_chars[i]
        if col_colors[i] == YELLOW:
            yellows += col_chars[i]

    return "".join(set(yellows))


def possible_words(gridle, corpus, row=None, column=None):
    assert (row is None) != (column is None)  # exactly one of the two is given
    assert row in (None, 0, 2, 4)
    assert column in (None, 0, 2, 4)

    gridle_chars = _grid_chars(gridle)
    gridle_colors = _grid_colours(gridle)
    available_non_intersect = ""

    chars = pick_list(gridle_chars, row=row, column=column)
    colors = pick_list(gridle_colors, row=row, column=column)

    for r in range(5):
        for c in range(5):
            if r == row or c == column:
                if gridle_colors[r][c] == YELLOW:
                    available_non_intersect += gridle_chars[r][c]
            else:
                if gridle_colors[r][c] == GRAY:
                    available_non_intersect += gridle_chars[r][c]

    available_non_intersect = "".join(set(available_non_intersect))

    yellows = ""
    for i in range(len(chars)):
        if colors[i] == YELLOW:
            yellows += chars[i]

    # all the yellow chars that need to be in the word
    yellows_non_intersect = ""
    for i in (1, 3):
        if colors[i] == YELLOW:
            yellows_non_intersect += chars[i]

    # get a list of gray chars that do not also occurr as yellow in this word
    grays = ""
    for i in range(5):
        if colors[i] == GRAY and chars[i] not in yellows:
            grays += chars[i]

    # build a regex pattern which candidates have to match
    pattern = ""
    for i in range(5):
        if colors[i] == GREEN:
            pattern += chars[i]
        else:
            # match for any available char but not the one at this position and not other grays in this word
            available = available_non_intersect.translate({ord(c): None for c in chars[i] + grays})

            # also allow yellows of intersecting rows/columns
            if row is not None:
                available += available_intersect(gridle_chars, gridle_colors, row, i)
            else:
                available += available_intersect(gridle_chars, gridle_colors, i, column)

            available = "".join(set(available))  # remove duplicates
            pattern += f"[{available}]"
    p = re.compile(pattern)
    regex_filtered_words = list(filter(p.match, corpus))

    # look for words that contain all the given yellow chars at non-green positions
    possible_words = []
    for word in regex_filtered_words:
        # the same word but green chars are replaced with an underscore
        word_without_greens = list(word)
        for i in range(len(word)):
            if colors[i] == GREEN:
                word_without_greens[i] = "_"
        word_without_greens = "".join(word_without_greens)

        for c in yellows_non_intersect:
            if c not in word_without_greens:
                break
        else:
            possible_words.append(word)

    return possible_words


def solve_gridle(gridle, corpus):
    result = [[None] * 5, [None] * 5, [None] * 5, [None] * 5, [None] * 5]
    char_bag = gridle.chars()
    row_possibilities = [None] * 5
    col_possibilities = [None] * 5
    for rc in (0, 2, 4):
        row_possibilities[rc] = possible_words(gridle, corpus, row=rc)
        col_possibilities[rc] = possible_words(gridle, corpus, column=rc)

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

    return Gridle([Cell(0, 0, c, GREEN) for row in result for c in row if c is not None])


def _grid_chars(gridle):
    return [[cell.char if cell is not None else None for cell in row] for row in gridle.to_grid()]


def _grid_colours(gridle):
    return [[cell.colour if cell is not None else None for cell in row] for row in gridle.to_grid()]
