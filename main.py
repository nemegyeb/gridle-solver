from corpora import CORPUS_EN
from gridle_solver import solve
from gridle_parser import parse_gridle
from swap_solver import calculate_swaps
from game_controller import execute_swaps

def main():
    gridle = parse_gridle()
    gridle.print()

    solution = solve(gridle, CORPUS_EN)

    solved = True # TODO
    for r in range(5):
        for c in range(5):
            if (r in (0,2,4) or c in (0,2,4)) and solution[r][c] == None:
                solved = False
    if not solved:
        print("Could not solve.")
        exit(1)

    swaps = calculate_swaps(gridle.chars, [c for row in solution for c in row if c != None])
    
    execute_swaps(gridle, swaps)

if __name__ == "__main__":
    main()
