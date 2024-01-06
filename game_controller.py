import io
import subprocess
from PIL import Image
from gridle_parser import Gridle


def capture_screen() -> Image.Image:
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
    if result.returncode != 0:
        raise Exception("Could not take screenshot")

    return Image.open(io.BytesIO(result.stdout))


def start_new(gridle):
    pass


def execute_swaps(gridle: Gridle, swaps: list[tuple[int, int]]):
    for start, end in swaps:
        start_coords = gridle.cells[start].get_centre()
        end_coords = gridle.cells[end].get_centre()
        _adb_swipe(start_coords, end_coords)


def _adb_swipe(start, end, duration_ms=100):
    start_x, start_y = start
    end_x, end_y = end
    subprocess.run(["adb", "shell", "input", "touchscreen", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)])
