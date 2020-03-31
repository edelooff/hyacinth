from collections import Counter
import random
import re
import sys

DESIGN = re.compile(r'''
    (?P<design>[A-Z])
    (?P<size>[SL])
    (?P<flowers>(:?\d+[a-z])+)
    (?P<total>\d+)''', re.VERBOSE)
DESIGN_FLOWER = re.compile(r'''
    (?P<count>\d+)
    (?P<species>[a-z])''', re.VERBOSE)


class BouquetDesigner:
    def __init__(self, design, size, required_flowers, total_count):
        self.design = design
        self.size = size
        self.random_flower_count = total_count - sum(required_flowers.values())
        self.required_flowers = required_flowers
        self.total_count = total_count
        self.pool_available = Counter()
        self.wildcards = 0

    def added(self, species, size):
        if size == self.size:
            if species in self.required_flowers:
                self.pool_available[species] += 1
            else:
                self.wildcards += 1
            return self.can_create()  # Only relevant if correct size was added

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

    def remove(self, species, size, quantity=1):
        """Proceses removal of flowers from the flower pool.

        This will update either the cache for available required flowers, or
        if it's a speciess not -required- for this deisgn, the wildcard count.
        """
        if size == self.size:
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
    designers = []
    pools = {'L': Counter(), 'S': Counter()}
    for design in iter(sys.stdin.readline, '\n'):
        designers.append(BouquetDesigner.from_specification(design))
    for species, size in (line.strip() for line in sys.stdin):
        pools[size][species] += 1
        for designer in designers:
            if designer.added(species, size):
                bouquet = designer.create(pools[size])
                # Move this out of the main loop probably
                for b_species, quantity in bouquet.items():
                    for gen in designers:
                        gen.remove(b_species, size, quantity=quantity)
                print(designer.stringify_bouquet(bouquet))


if __name__ == '__main__':
    main()
