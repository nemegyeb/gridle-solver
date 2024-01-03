import time
from corpora import CORPUS_EN
from gridle_solver import solve
from gridle_parser import parse_gridle
from swap_solver import calculate_swaps
from game_controller import execute_swaps, start_new

def main():
    while True:
        start_new()

        start_time = time.time()
        gridle = parse_gridle()
        end_time = time.time()
        print(f"\tparsing took {end_time - start_time:.6f} seconds.")

        print(gridle)

        try:
            start_time = time.time()
            solution = solve(gridle, CORPUS_EN)
            end_time = time.time()
            print(f"\tsolving took {end_time - start_time:.6f} seconds.")
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
        print(f"\tcalculating swaps took {end_time - start_time:.6f} seconds.")

        execute_swaps(swaps)
        print(f"Solved with {len(swaps)} swaps.")
        time.sleep(1.9)

if __name__ == "__main__":
    main()
