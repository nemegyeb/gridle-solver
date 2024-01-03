import subprocess

def start_new(gridle):
    pyautogui.mouseDown(321, 163)
    pyautogui.mouseUp()
    return

def execute_swaps(gridle, swaps):
    for start, end in swaps:
        start = gridle.coordinates[start]
        end = gridle.coordinates[end]
        start = _get_cell_centre(start)
        end = _get_cell_centre(end)
        _adb_swipe(start, end)

def _adb_swipe(start, end, duration_ms=100):
    subprocess.run(["adb", "shell", "input", "touchscreen", "swipe", *map(str, start + end), str(duration_ms)])

def _get_cell_centre(cell):
    start, end = cell
    return ((start[0] + end[0])//2, (start[1] + end[1])//2)
