from typing import List


def _check_for_substring_match(string_to_check: str, substrings: List[str]) -> bool:
    return any((sub_string in string_to_check for sub_string in substrings))
