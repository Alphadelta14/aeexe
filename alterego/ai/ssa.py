
_STOP = object()


class SSA(object):
    def __init__(self, iterable):
        self._handle = iterable
        self._fields = []
        self._find_format()

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        line = next(self._handle)
        while not line.startswith('Dialogue:'):
            line = next(self._handle)
        line = line.split('Dialogue:', 1)[1].lstrip()
        return dict(zip(self._fields, self._csvline(line)))

    def _find_format(self):
        for line in self._handle:
            if line.startswith('[Events]'):
                break
        for line in self._handle:
            if line.startswith('Format:'):
                break
        else:
            raise ValueError('Could not find Events:Format')
        line = line.split('Format:', 1)[1]
        self._fields = self._csvline(line)

    @staticmethod
    def _csvline(line):
        row = []
        chars = list(line.strip())+['\n']

        def read_quoted(quote_char):
            col = ''
            while True:
                char = chars.pop(0)
                if char == quote_char:
                    return col
                elif char == '\\':
                    col += char
                    col += chars.pop(0)
                col += char

        def read_col():
            col = ''
            char = chars.pop(0)
            if char == _STOP:
                return _STOP
            while char in (' ', '\t'):
                char = chars.pop(0)
            # if char in '"\'':
            #     return read_quoted(char)
            while True:
                if char == ',':
                    return col
                elif char == '\n':
                    chars.append(_STOP)
                    return col
                elif char == '{':
                    # Strip tags
                    while char != '}':
                        char = chars.pop(0)
                else:
                    col += char
                char = chars.pop(0)
        while True:
            col = read_col()
            if col == _STOP:
                break
            row.append(col)
        return row


def learn_ssa(filename):
    with open(filename) as handle:
        # reader = csv.DictReader(iter_dialog(handle))
        reader = SSA(handle)
        for dialog in reader:
            if dialog['Style'] != 'Default':
                continue
            line = dialog['Text'].replace('\\N', ' ').replace('\\h', ' ')
            yield line
