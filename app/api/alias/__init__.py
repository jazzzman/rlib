from typing import List

__all__ = ['generate_alias_pattern', 'is_alias',
           'find_matching_aliases', 'suggest_similar_names']


def generate_alias_pattern(name: str) -> str:
    from .translit_dict import from_ru
    name = name.lower()
    pattern = []
    for c in name:
        alias_symbols = [c] + from_ru[c]
        contains_empty = '' in alias_symbols
        if contains_empty:
            alias_symbols.remove('')
        if all(map(lambda x: len(x) <= 1, alias_symbols)):
            pattern.append(
                '[' +
                ''.join(alias_symbols) +
                ']')
        else:
            pattern.append(
                '(?:' +
                '|'.join(alias_symbols) +
                ')'
            )
        if contains_empty:
            pattern.append('?')
    return ''.join(pattern)


def is_alias(pattern: str, other_name: str) -> bool:
    import re
    return re.match(pattern, other_name.lower()) is not None


def find_matching_aliases(pattern: str, names: List[str]) -> List[str]:
    result = list(filter(lambda n: is_alias(pattern, n), names))
    return result if result else []


def suggest_similar_names(name: str, other_names: List[str], up_to=3) -> List[str]:
    from difflib import get_close_matches
    matches = get_close_matches(name, other_names, n=up_to)
    return [''.join(seq_chars) for seq_chars in matches]
