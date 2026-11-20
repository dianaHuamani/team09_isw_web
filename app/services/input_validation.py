import re


NAME_PATTERN = re.compile(r"[^\W\d_]+(?:[ '\u2019-][^\W\d_]+)*", re.UNICODE)
PHONE_PATTERN = re.compile(r"\+?[0-9() .-]+")


def valid_name(value, maximum):
    return 2 <= len(value) <= maximum and NAME_PATTERN.fullmatch(value) is not None


def valid_phone(value):
    digits = sum(character.isdigit() for character in value)
    return (
        7 <= digits <= 15
        and len(value) <= 30
        and PHONE_PATTERN.fullmatch(value) is not None
    )
