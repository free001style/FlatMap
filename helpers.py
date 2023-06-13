import re

def find_substring(string, substring):
    index = string.find(substring)
    if index != -1:
        words = string[:index].split()
        return words[-1]
    else:
        return str(None)


def find_first_digit(string):
    match = re.search(r'\d+', string)
    if match:
        return match.group()
    else:
        return None
