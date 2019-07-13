from collections import namedtuple, defaultdict
import re
import numpy as np

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

class id_mapper:
    """Wrapper around a defaultdict for assigning unique identifiers
    to hashable objects.
    """
    def __init__(self):
        self.reset()
        
    def __getitem__(self, k):
        if self._back[k] == -1:
            self._back[k] = self._next_id
            self._next_id += 1
        return self._back[k]

    def reset(self):
        self._next_id = 0
        self._back = defaultdict(lambda: -1)

    def  __len__(self):
        return len(self._back)

def histogram_to_array(h, t_min, t_max):
    users = id_mapper()

    a = []

    for i in range(t_min, t_max + 1):
        entries = h[i]
        ids = np.array([users[e.user] for e in entries])
        a.append(ids)

    return np.array(a)

def user_ids(entries):
    """Computes a map from usernames to unique numbers."""
    users = id_mapper()
    for e in entries:
        users[e.user]
    return users

def histogram_to_matrix(entries, users=None):
    if users is None:
        users = user_ids(entries)
    n = len(users)
    # note: n is the least upper bound of users
    t_min, t_max = entries[0].time, entries[-1].time
    row_count = t_max + 1 - t_min
    m = np.ndarray( (row_count, n), dtype=np.float64 )
    max_msgs = 0.0
    for e in entries:
        m[e.time - t_min, users[e.user]] += 1
        p = m[e.time - t_min, users[e.user]]
        if p > max_msgs:
            max_msgs = p
    m /= max_msgs
    print("max_msgs", max_msgs)
    return m

def main(args):
    entries = load(args[1])
    users = user_ids(entries)
    
    h = histogram(entries)
    a = histogram_to_array(h, entries[0].time, entries[-1].time)
    m = histogram_to_matrix(entries, users)
    print("loaded", len(h), "entries")

if __name__ == '__main__':
    import sys
    main(sys.argv)
        
