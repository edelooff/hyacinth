from collections import Counter
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

    @classmethod
    def from_specification(cls, design):
        spec = DESIGN.match(design).groupdict()
        spec_flowers = DESIGN_FLOWER.findall(spec['flowers'])
        flowers = {species: int(count) for count, species in spec_flowers}
        return cls(
            spec['design'], spec['size'], flowers, int(spec['total']))


def main():
    designers = []
    pool = Counter()
    for design in iter(sys.stdin.readline, '\n'):
        designers.append(BouquetDesigner.from_specification(design))
    for species, size in (line.strip() for line in sys.stdin):
        pool[species + size] += 1
        for designer in designers:
            if designer.added(species, size):
                print(f'Designer {designer} can create a bouquet')


if __name__ == '__main__':
    main()
