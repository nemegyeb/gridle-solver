
from gridle_parser import Colour
GRAY = Colour.GRAY
YELLOW = Colour.YELLOW
GREEN = Colour.GREEN



def print_gridle(gridle):
    gridle_chars, gridle_colors = gridle
    ANSI_RESET = "\033[0m"
    VERT_BAR = f"{ANSI_RESET}|"
    str = f"{ANSI_RESET}┌───{('┬───' * (len(gridle_chars[0]) - 1))}┐\n"
    for row in range(len(gridle_chars)):
        str += VERT_BAR
        for col in range(len(gridle_chars[row])):
            if gridle_chars[row][col] == None:
                str += f"   {VERT_BAR}"
            else:
                if gridle_colors[row][col] == GREEN:
                    str += "\033[32;1m"
                elif gridle_colors[row][col] == YELLOW:
                    str += "\033[33;1m"
                else:
                    assert gridle_colors[row][col] == GRAY
                    str += "\033[30;1m"
                str += f" {gridle_chars[row][col]} {VERT_BAR}"
        if row != len(gridle_chars) - 1:
            str += f"\n├───{('┼───' * (len(gridle_chars[0]) - 1))}┤\n"
        else:
            str += f"\n└───{('┴───' * (len(gridle_chars[0]) - 1))}┘"
    print(str)