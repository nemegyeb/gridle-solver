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
    shell = subprocess.Popen(["adb", "shell"], stdin=subprocess.PIPE)
    for start, end in swaps:
        start_coords = gridle.cells[start].get_centre()
        end_coords = gridle.cells[end].get_centre()
        _adb_swipe(shell, start_coords, end_coords)

    shell.stdin.close()
    shell.wait()


def _adb_swipe(shell, start, end, duration_ms=100):
    start_x, start_y = start
    end_x, end_y = end
    shell.stdin.write(f"input touchscreen swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}\n".encode())
