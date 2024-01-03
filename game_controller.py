import pyautogui

OFFSET_X = 35
OFFSET_Y = 345
SPACING_X = 78.5
SPACING_Y = 73

def row_col_to_pixel_coords(r, c):
    return round(OFFSET_X + c * SPACING_X), round(OFFSET_Y + r * SPACING_Y)

def start_new():
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
