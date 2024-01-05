from typing import TypeVar

T = TypeVar("T")


def calculate_swaps(original: list[T], solution: list[T]) -> list[tuple[int, int]]:
    orders = _find_orders(original, solution)
    perms = _make_permutations(orders)
    best = _select_best(perms)
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
                    return [[e] + r for e in es for r in _make_permutations([[o for o in opt if o != e] for opt in rest])]


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
    return min([_unshuffle(perm) for perm in perms], key=lambda seq: len(seq))
