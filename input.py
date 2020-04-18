def sep(string: str) -> tuple:
    arr = string.split(' ', 1)
    rest = arr[1]
    idx = rest.find('}')
    tp, rest = rest[:idx+1], rest[idx+1:].strip()
    a, b = rest.split(' ', 1)
    return tp, a, b


def get_value(lst):
    """
    0: property
    1: type
    2: name
    3: description
    :return:
    """
    text = f"\t/**\n"
    if lst[1].startswith('_'):
        text += '\t * @private\n'
    text += f"\t * @name {lst[1]}\n" \
            f"\t * @type {lst[0]}\n" \
            f"\t * @desc {lst[2]}\n" \
            f"\t */"
    return text

def parse_attr(s):
    idx = s.find('*')
    string = s[idx+1:].lstrip()
    return sep(string)

def parse_dlr(texts):
    lst = [i.strip().split(':') for i in texts.split('\n')]
    return dict([(i[0].strip(), i[1].strip().rstrip(',')) for i in lst])


dlr = """when_cooldown_ends: 0,
	state: 0,
	__work: null
	__current_seconds: null,"""



values = """ * @property {number} when_cooldown_ends time of the progress
 * @property {number} state the state of the progress (0-2), 0-stopped, 1-start wait 2-half time passed
 * @property {SimpleInterval} __work SimpleInterval for updating auto update the progress bar.  handler of progress update interval
 * @property {string} __current_seconds to make prorgess text update event 1 seconds 
"""

def find(s, lst):
    for i in lst:
        if i[1] == s:
            return i


if __name__ == '__main__':
    dlr = parse_dlr(dlr)
    values = [parse_attr(val) for val in values.split('\n') if val]
    for item in dlr.items():
        # first find
        t = find(item[0], values)
        print(get_value(t))
        print(f'\t{": ".join(item)},')