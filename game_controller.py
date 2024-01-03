import subprocess

def start_new(gridle):
    pyautogui.mouseDown(321, 163)
    pyautogui.mouseUp()
    return

def execute_swaps(gridle, swaps):
    for start, end in swaps:
        start_coords = gridle.cells[start].get_centre()
        end_coords = gridle.cells[end].get_centre()
        _adb_swipe(start_coords, end_coords)

def _adb_swipe(start, end, duration_ms=100):
    subprocess.run(["adb", "shell", "input", "touchscreen", "swipe", *map(str, start + end), str(duration_ms)])
