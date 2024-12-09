import re
from ast import literal_eval


def str_to_bool(string: str):
    return string in ["1", "true", True]


def remove_quotes(input_string: str):
    return re.sub(r"^'(.*)'$", r"\1", input_string)


def is_array(string: str):
    return bool(re.search(r"\w+\[\d+\]$", string))


def get_str_array_index(string: str):
    match = re.search(r"\w+\[(\d+)\]$", string)
    if match:
        return int(match.group(1))
    else:
        return None


def split_str_array(string: str):
    return string.split("[")[0] if "[" in string else string


def is_dict(string: str):
    return bool(re.search(r"\{.*?\}", string))


def convert_to_dict(string: str):
    try:
        if is_dict(string):
            keys = re.findall(r"([^:\s]+)(?=:)", string)

            for key in keys:
                if key.startswith("{"):
                    key = key.replace("{", "")
                if not key.startswith("'"):
                    string = string.replace(key, f"'{key}'")
            string = literal_eval(string)
    except Exception as e:
        print(e)
    return string


def parse_str_to_list_or_tuple(arg: str):
    """
    Convert strings to their respective data structure (lists or tuples only).
    """
    arg = arg.strip()

    if arg.startswith("[") and arg.endswith("]"):
        items = arg[1:-1].split(",")
        return [item.strip().strip("'").strip('"') for item in items]

    elif arg.startswith("(") and arg.endswith(")"):
        items = arg[1:-1].split(",")
        return tuple(item.strip().strip("'").strip('"') for item in items)

    return arg
