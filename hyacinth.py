import re
import sys

DESIGN = re.compile(r'''
    (?P<design>[A-Z])
    (?P<size>[SL])
    (?P<flowers>(:?\d+[a-z])+)
    (?P<total>\d+)''', re.VERBOSE)


def main():
    for design in iter(sys.stdin.readline, '\n'):
        print('design', DESIGN.match(design).groupdict())
    for flower in (line.strip() for line in sys.stdin):
        print('flower', flower)


if __name__ == '__main__':
    main()
