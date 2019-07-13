from collections import namedtuple, defaultdict
import re

MESSAGE_LINE_REGEX = re.compile('"(\d+)"<.(\w+)> (.*)\n')

class Entry(namedtuple('EntryBase', ['time', 'user', 'text'])):
    pass

def _parse_line(line):
    """Parses a single irssi log line returns an `Entry` or `None`.""" 
    m = MESSAGE_LINE_REGEX.fullmatch(line)

    # None is filtered out later
    if m is None:
        return None

    time, user, text = m.group(1, 2, 3)
    time = int(time)
    return Entry(time=time, user=user, text=text)

def load(path):
    with open(path) as f:
        return \
            [ l
              for l
              in (_parse_line(line) for line in f)
              if l is not None
            ]

def histogram(entries):
    """Takes a list of entries and computes a map from times to sets of entries."""
    h = defaultdict(lambda: set())
    for e in entries:
        h[e.time].add(e)
    return h

def main(args):
    entries = load(args[1])
    h = histogram(entries)
    print("loaded", len(h), "entries")

if __name__ == '__main__':
    import sys
    main(sys.argv)
        
