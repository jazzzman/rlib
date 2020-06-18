from . import generate_alias_pattern, is_alias,\
    find_matching_aliases, suggest_similar_names
import unittest


class TestAliasPatternGenerator(unittest.TestCase):

    def test_single_character_translit_makes_square_bracket_pattern(self):
        char = 'к'

        pattern = generate_alias_pattern(char)

        assert pattern.startswith('[')
        assert pattern.endswith(']')
        assert '|' not in pattern

    def test_multi_character_translit_makes_or_pattern(self):
        char = 'ж'

        pattern = generate_alias_pattern(char)

        assert pattern.startswith('(')
        assert pattern.endswith(')')
        assert '|' in pattern

    def test_empty_character_translit_makes_question_pattern(self):
        char = 'ь'

        pattern = generate_alias_pattern(char)

        assert pattern.startswith('[')
        assert pattern.endswith(']?')


class TestIsAlias(unittest.TestCase):
    def test_name_is_alias_of_itself_lowercase(self):
        import re
        name = 'Маклыгина'

        pattern = generate_alias_pattern(name)
        assert re.match(pattern, name.lower()) is not None

    def test_name_is_not_alias_of_itself_sentencecase(self):
        import re
        name = 'Маклыгина'

        pattern = generate_alias_pattern(name)

        assert re.match(pattern, name) is None

    def test_translit_name_is_an_alias(self):
        name = 'Грачев'
        other_name = 'Grachev'

        pattern = generate_alias_pattern(name)

        assert is_alias(pattern, other_name)

    def test_russian_e_is_an_alias(self):
        name = 'Лощенов'
        other_name = 'Лощёнов'

        pattern = generate_alias_pattern(name)
        assert is_alias(pattern, other_name)

    def test_different_name_is_not_an_alias(self):
        name = 'Романишкин'
        other_name = 'Грачев'

        pattern = generate_alias_pattern(name)

        assert not is_alias(pattern, other_name)


class TestFindAliases(unittest.TestCase):
    def test_finds_english_aliases(self):
        name = 'Савельева'
        other_names = [
            'Saveleva',
            'Savel\'eva',
            'Savelieva',
            'Saveljeva']

        pattern = generate_alias_pattern(name)
        found_aliases = find_matching_aliases(pattern, other_names)

        for on in other_names:
            assert on in found_aliases

    def test_finds_russian_aliases(self):
        name = 'Лощёнов'
        other_names = [
            'Лощёнов',
            'Лощенов',
            'лощенов']

        pattern = generate_alias_pattern(name)
        found_aliases = find_matching_aliases(pattern, other_names)

        for on in other_names:
            assert on in found_aliases

    def test_ignores_non_aliases_returns_empty_list(self):
        name = 'Романишкин'
        other_names = [
            'Грачев',
            'Loschenov']

        pattern = generate_alias_pattern(name)
        found_aliases = find_matching_aliases(pattern, other_names)

        for on in other_names:
            assert on not in found_aliases


class TestFindSimilarNames(unittest.TestCase):
    def test_suggests_with_different_letter(self):
        name = 'Loschenov'
        other_names = [
            'Loschenov',
            'Loshchenov',
            'Savelieva']

        suggestions = suggest_similar_names(name, other_names)

        assert 'Loschenov' in suggestions
        assert 'Loshchenov' in suggestions
        assert 'Savelieva' not in suggestions


if __name__ == '__main__':
    unittest.main()
