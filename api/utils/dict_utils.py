def safe_pop(dictionary: dict, keys: list):
    """
    Safely remove the specified keys in a dictionary.
    """
    if not isinstance(keys, list):
        keys = [keys]

    for key in keys:
        if key in dictionary:
            dictionary.pop(key)


def invert_dict(dictionary: dict):
    inverted_dict = {value: key for key, value in dictionary.items()}
    return inverted_dict


def get_common_dict(dict_1: dict, dict_2: dict):
    dict_1.update({k: dict_2[k] for k in dict_1 if k in dict_2})
    return dict_1


def merge_dicts(dict_1: dict, dict_2: dict) -> dict:
    combined_keys = set(dict_1.keys()).union(set(dict_2.keys()))
    result_dict = {key: dict_2.get(key, dict_1.get(key)) for key in combined_keys}

    return result_dict
