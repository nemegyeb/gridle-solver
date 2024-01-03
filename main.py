import time
# import pyautogui
import subprocess
from gridle_parser import parse_gridle
from gridle_solver import solve
from swap_solver import calculate_swaps
from corpora import CORPUS_EN


OFFSET_X = 154
OFFSET_Y = 680
SPACING = 177.5



def row_col_to_pixel_coords(r, c):
    return round(OFFSET_X + c * SPACING), round(OFFSET_Y + r * SPACING)



# def click_refresh_button():
#     pyautogui.mouseDown(321, 163)
#     pyautogui.mouseUp()
#     return



def adb_swipe(start_x, start_y, end_x, end_y, duration_ms=100):
    cmd = f"adb shell input touchscreen swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
    subprocess.run(cmd.split())



def execute_swaps(swaps):
    for (start_r, start_c), (end_r, end_c) in swaps:
        start_x, start_y = row_col_to_pixel_coords(start_r, start_c)
        end_x, end_y = row_col_to_pixel_coords(end_r, end_c)
        adb_swipe(start_x, start_y, end_x, end_y)



def main():

    start_time = time.time()
    gridle = parse_gridle()
    end_time = time.time()

    gridle.print()

    print(f"parsing took {end_time - start_time:.6f} seconds.")

    try:
        start_time = time.time()
        solution = solve(gridle, CORPUS_EN)
        end_time = time.time()
        print(f"solving took {end_time - start_time:.6f} seconds.")
    except:
        print("An error occurred while trying to solve.")
        exit(1)

    solved = True
    for r in range(5):
        for c in range(5):
            if (r in (0,2,4) or c in (0,2,4)) and solution[r][c] == None:
                solved = False
    if not solved:
        print("Could not solve.")
        exit(1)


    start_time = time.time()
    swaps = calculate_swaps(chars, solution)
    end_time = time.time()
    print(f"calculating swaps took {end_time - start_time:.6f} seconds.")
    execute_swaps(swaps)
    print(f"Solved with {len(swaps)} swaps.")
    # time.sleep(1.9)

if __name__ == "__main__":
    main()
