from typing import List, TypeVar

T = TypeVar('T')

def calculate_swaps(original: List[T], solution: List[T], to_coordinates=False):
    orders = _find_orders(original, solution)
    perms = _make_permutations(orders)
    best = _select_best(perms)
    if to_coordinates:
        return _swaps_to_coordinates(best)
    return best

def _find_orders(original, ordered):
    return [[i for i, o in enumerate(ordered) if o == elem] for elem in original]

def _make_permutations(options):
    match options:
        case []:
            return []
        case [opt]:
            return [[elem] for elem in opt]
        case [opt, *rest]:
            match opt:
                case [e]:
                   return [[e] + r for r in _make_permutations(rest)]
                case [*es]:
                    return [
                        [e] + r
                        for e in es
                        for r in _make_permutations([[o for o in opt if o != e] for opt in rest])
                    ]

def _unshuffle(list):
    swaps = []
    for i in range(len(list)):
        curr = list[i]

        while i != curr:
            list[i], list[curr] = list[curr], list[i]
            swaps.append((i, curr))
            curr = list[i]

    return swaps

def _select_best(perms):
    return min([_unshuffle(perm) for perm in perms], key=lambda l: len(l))

def _swaps_to_coordinates(swaps):
    mapping = {
        0:  (0, 0),
        1:  (0, 1),
        2:  (0, 2),
        3:  (0, 3),
        4:  (0, 4),
        5:  (1, 0),
        6:  (1, 2),
        7:  (1, 4),
        8:  (2, 0),
        9:  (2, 1),
        10: (2, 2),
        11: (2, 3),
        12: (2, 4),
        13: (3, 0),
        14: (3, 2),
        15: (3, 4),
        16: (4, 0),
        17: (4, 1),
        18: (4, 2),
        19: (4, 3),
        20: (4, 4)
    }
    return [(mapping[i], mapping[j]) for (i,j) in swaps]
