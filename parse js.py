def get_firsts(s, *args):
    for i in args:
        if s.startswith(i):
            return i
    return None

def get_first_end(s, *args):
    for i in args:
        if s.endswith(i):
            return i
    return None

def strips(s, *args):
    k = get_firsts(s, *args)
    while k is not None:
        s = s.strip(k)
        k = get_firsts(s, *args)
    k = get_first_end(s, *args)
    while k is not None:
        s = s.strip(k)
        k = get_first_end(s, *args)
    return s

def parse_staff(key, text):
    text = text.replace('\n ', ' ').replace('\n', ' ')
    is_script = text.startswith("<script>")
    print(text)
    keys = text.strip().lstrip("<script").lstrip("<link").rstrip("></script>").rstrip("></link").strip(" ")
    keys = keys.split(" ")
    print(keys)
    d = dict(key.split("=", 1) for key in keys if key)
    if "href" in d:
        d["src"] = d["href"]
        d.pop("href")
    src = strips(d['src'], " ", "\t", "\"", "\'")
    i = strips(d['integrity'], " ", "\t", "\"", "\'")
    oc = strips(d.pop("crossorigin"), " ", "\t", "\"", "\'")
    print(
        f"\t\'{key}\': CDNResource(\n"
        f"\t\t{is_script},\n"
        f"\t\t\"{src}\",\n"
        f"\t\t\"{i}\",\n"
        f"\t\t\"{oc}\"\n"
        f"\t),"
    )


def parse():
    key = input('key')
    text = ''
    t = input("enter text")
    while t:
        text += t
        t = input()
    return key, text


parse_staff(*parse())
