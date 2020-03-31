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
        self.designers = []
        self.flowers = Counter()

    def add_designer(self, designer):
        """Adds a BouquetDesigner for the pool size."""
        self.designers.append(designer)

    def add_flower(self, species):
        """Adds a flower of given species to the pool of available flowers."""
        self.flowers[species] += 1
        for designer in self.designers:
            if designer.add(species):
                bouquet = designer.create(self.flowers)
                print(designer.stringify_bouquet(bouquet))
                for bundle in bouquet.items():
                    for gen in self.designers:
                        gen.remove(*bundle)


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

    def create(self, pool):
        """Returns a bouquet (species listing) assembled from the given pool.

        After picking the required flowers, if additional flowers are needed,
        this method selects a sample of flowers from the pool at random. This
        avoids pathological behaviour where it *consistently* steals the same
        flower speciess required by other designs, it simply picks a few of
        everything, with a bias to flowers there are a lot of.
        """
        bouquet = Counter()
        for species, count in self.required_flowers.items():
            pool[species] -= count
            bouquet[species] += count
        # Pick the remaining flowers
        if self.random_flower_count:
            population = []
            for species, count in pool.items():
                population.extend([species] * count)
            for species in random.sample(population, self.random_flower_count):
                pool[species] -= 1
                bouquet[species] += 1
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


def main():
    pools = defaultdict(Pool)
    for design in iter(sys.stdin.readline, '\n'):
        designer = BouquetDesigner.from_specification(design)
        pools[designer.size].add_designer(designer)
    for species, size in (line.strip() for line in sys.stdin):
        pools[size].add_flower(species)


if __name__ == '__main__':
    main()
