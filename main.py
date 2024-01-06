from corpora import CORPUS_EN
from gridle_solver import solve_gridle
from gridle_parser import Gridle
from swap_solver import calculate_swaps
from game_controller import capture_screen, execute_swaps


def main():
    image = capture_screen()

    gridle = Gridle.parse(image)
    gridle.print()

    solution = solve_gridle(gridle, CORPUS_EN)
    if len(solution.cells) != 21:
        print("Could not solve.")
        exit(1)

    solution.print()

    swaps = calculate_swaps(gridle.chars(), solution.chars())

    execute_swaps(gridle, swaps)


if __name__ == "__main__":
    main()
