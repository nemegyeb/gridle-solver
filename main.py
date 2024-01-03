import time
import pyautogui
from corpora import CORPUS_EN
from gridle_solver import solve
from gridle_parser import parse_gridle
from swap_solver import calculate_swaps

OFFSET_X = 35
OFFSET_Y = 345
SPACING_X = 78.5
SPACING_Y = 73



def row_col_to_pixel_coords(r, c):
    return round(OFFSET_X + c * SPACING_X), round(OFFSET_Y + r * SPACING_Y)



def click_refresh_button():
    pyautogui.mouseDown(321, 163)
    pyautogui.mouseUp()
    return



def execute_swaps(swaps):
    for (start_r, start_c), (end_r, end_c) in swaps:
        start_x, start_y = row_col_to_pixel_coords(start_r, start_c)
        end_x, end_y = row_col_to_pixel_coords(end_r, end_c)

        # drag
        pyautogui.mouseDown(start_x + 50, start_y + 50)
        pyautogui.moveTo(end_x + 50, end_y + 50, duration=0.01)
        pyautogui.mouseUp()



def main():
    while True:
        click_refresh_button()

        start_time = time.time()
        gridle = parse_gridle()
        end_time = time.time()
        elapsed_time = end_time - start_time

        chars, colors = gridle
        print("\n".join([str(x) for x in chars]))
        print("\n".join([str(x) for x in colors]))

        print(f"\tparsing took {elapsed_time:.6f} seconds.")

        try:
            start_time = time.time()
            solution = solve(gridle, CORPUS_EN)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"\tsolving took {elapsed_time:.6f} seconds.")
        except:
            print("An error occurred while trying to solve, skip.")
            continue

        solved = True
        for r in range(5):
            for c in range(5):
                if (r in (0,2,4) or c in (0,2,4)) and solution[r][c] == None:
                    solved = False
        if not solved:
            print("Could not solve, skip.")
            continue


        start_time = time.time()
        swaps = calculate_swaps(gridle.chars, [c for row in solution for c in row if c != None])
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\tcalculating swaps took {elapsed_time:.6f} seconds.")
        execute_swaps(swaps)
        print(f"Solved with {len(swaps)} swaps.")
        time.sleep(1.9)



if __name__ == "__main__":
    main()

