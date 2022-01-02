import os
import functools
from datetime import timedelta

days_by_period = {
    'year': timedelta(days=365),
    'month': timedelta(days=30)
}


def subtract_date_by_difference(date, diff):
    return (date.replace(day=1) - diff).replace(day=date.day)


def has_none_value(dictonary):
    for value in dictonary.values():
        if value is None:
            return True

    return False


def is_all_values_none(dictonary):
    for value in dictonary.values():
        if value is not None:
            return False

    return True


def is_key_and_value_in_dictonary(dictonary, key_to_search, value_to_search):
    for key, value in dictonary.items():
        if key == key_to_search and value == value_to_search:
            return True

    return False


def toggle_value(value, values):
    return values[0] if value == values[1] else values[1]


def makedirs_from_path(path):
    directories = path.split('/')

    def check_and_make_dir(path, dir):
        partial_path = path + "/" + dir

        if not os.path.isdir(partial_path):
            os.mkdir(partial_path)

        return partial_path

    functools.reduce(check_and_make_dir, directories)
