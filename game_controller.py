import subprocess

def start_new(gridle):
    pyautogui.mouseDown(321, 163)
    pyautogui.mouseUp()
    return

def execute_swaps(gridle, swaps):
    for start_index, end_index in swaps:
        start_cell = gridle.coordinates[start_index]
        end_cell = gridle.coordinates[end_index]
        start_coords = _get_cell_centre(start_cell)
        end_coords = _get_cell_centre(end_cell)
        _adb_swipe(start_coords, end_coords)

def _adb_swipe(start, end, duration_ms=100):
    start_x, start_y = start
    end_x, end_y = end
    subprocess.run(["adb", "shell", "input", "touchscreen", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)])

def _get_cell_centre(cell):
    start, end = cell
    return ((start[0] + end[0])//2, (start[1] + end[1])//2)
