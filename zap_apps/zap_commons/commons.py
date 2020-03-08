from itertools import chain, combinations

def powerset_generator(iterable):
    s = list(iterable)
    for subset in chain.from_iterable(combinations(s, r) for r in range(len(s)+1)):
        yield set(subset)