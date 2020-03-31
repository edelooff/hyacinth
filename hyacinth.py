from collections import (
    Counter,
    defaultdict)
import random
import re
import sys

DESIGN = re.compile(r'''
    (?P<design>[A-Z])
    (?P<size>[SL])
    (?P<flowers>(:?\d+[a-z])*)  # The specification is fuzzy on 1+ or 0+
    (?P<total>\d+)''', re.VERBOSE)
DESIGN_FLOWER = re.compile(r'''
    (?P<count>\d+)
    (?P<species>[a-z])''', re.VERBOSE)


class Pool:
    def __init__(self):
        self.common_species = set()
        self.designers = []
        self.flowers = Counter()

    def add_designer(self, designer):
        """Adds a BouquetDesigner for the pool size.

        It also updates the set of known required species, allowing better
        picking of 'filler' flowers for requested bouquets.
        """
        self.designers.append(designer)
        self.common_species |= designer.required_flowers.keys()

    def add_flower(self, species):
        """Adds a flower of given species to the pool of available flowers."""
        self.flowers[species] += 1
        for designer in self.designers:
            if designer.add(species):
                print(self.create_bouquet(designer))

    def create_bouquet(self, designer):
        """Creates a bouquet according to the given designers design.

        After creating the bouquet, other designers are informed of the
        removal of flower species from the shared pool.
        """
        bouquet = designer.create(self.flowers, self.common_species)
        bouquet_string = designer.stringify_bouquet(bouquet)
        for bundle in bouquet.items():
            for designer in self.designers:
                designer.remove(*bundle)
        return bouquet_string


class BouquetDesigner:
    def __init__(self, design, size, required_flowers, total_count):
        self.design = design
        self.size = size
        self.random_flower_count = total_count - sum(required_flowers.values())
        self.required_flowers = required_flowers
        self.total_count = total_count
        self.pool_available = Counter()
        self.wildcards = 0

    def add(self, species):
        if species in self.required_flowers:
            self.pool_available[species] += 1
        else:
            self.wildcards += 1
        return self.can_create()

    def can_create(self):
        for flower, count in self.required_flowers.items():
            if self.pool_available[flower] < count:
                return False
        available = sum(self.pool_available.values()) + self.wildcards
        if available >= self.total_count:
            return True
        return False

    def create(self, pool, common_species):
        """Returns a bouquet (species listing) assembled from the given pool.

        After picking the required flowers, if additional flowers are needed,
        this method selects a sample of flowers from the rest of the pool in
        two steps:

        1. Species of flowers used by other BouquetDesigners are avoided so
           that selection for this bouquet causes the least conflict.
        2. A random sample of flowers is picked, to avoid consistently stealing
           from the same other designers. Randomly selecting also hopefully
           generates nice and pleasing outcomes for the recipient, though this
           hypothesis has not been tested in the least.

        In all cases we bias to picking random flowers that we have a surplus
        of. In an ideal world we would have a function that determines the
        correct bias to introduce here.
        """
        bouquet = Counter()
        for species, quantity in self.required_flowers.items():
            pool[species] -= quantity
            bouquet[species] += quantity
        # Pick the remaining flowers
        if self.random_flower_count:
            remaining = self.random_flower_count
            for do_not_pick in (common_species, set()):
                population = []
                for species in pool.keys() ^ do_not_pick:
                    population.extend([species] * pool[species])
                sample_size = min(len(population), remaining)
                for species in random.sample(population, sample_size):
                    pool[species] -= 1
                    bouquet[species] += 1
                remaining -= sample_size
                if not remaining:
                    break
        return bouquet

    def remove(self, species, quantity):
        """Proceses removal of flowers from the flower pool.

        This will update either the cache for available required flowers, or
        if it's a speciess not -required- for this deisgn, the wildcard count.
        """
        if species in self.required_flowers:
            self.pool_available[species] -= quantity
        else:
            self.wildcards -= quantity

    def stringify_bouquet(self, bouquet):
        flowers = sorted(bouquet.items())
        flowerstring = (f'{count}{species}' for species, count in flowers)
        return f'{self.design}{self.size}{"".join(flowerstring)}'

    @classmethod
    def from_specification(cls, design):
        spec = DESIGN.match(design).groupdict()
        spec_flowers = DESIGN_FLOWER.findall(spec['flowers'])
        flowers = {species: int(count) for count, species in spec_flowers}
        return cls(
            spec['design'], spec['size'], flowers, int(spec['total']))


def read_until_empty(fp):
    """Yields lines from the given filepointer until an empty line is hit."""
    while (line := fp.readline().strip()):
        yield line


def main():
    pools = defaultdict(Pool)
    for design in read_until_empty(sys.stdin):
        designer = BouquetDesigner.from_specification(design)
        pools[designer.size].add_designer(designer)
    for species, size in read_until_empty(sys.stdin):
        pools[size].add_flower(species)


if __name__ == '__main__':
    main()
