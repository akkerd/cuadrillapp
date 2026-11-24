from cuadrillapp.constants import CODE_ALPHABET, CODE_LENGTH, EMOJIS
from cuadrillapp.domain.codes import generate_code, is_valid_code, normalize_code
from cuadrillapp.domain.names import clean_display, normalize_name


def test_code_alphabet_has_no_ambiguous_characters() -> None:
    assert not set("0O1IL") & set(CODE_ALPHABET)


def test_emojis_are_unique() -> None:
    assert len(EMOJIS) == len(set(EMOJIS))


def test_code_input_ignores_case_and_spaces() -> None:
    assert normalize_code(" abc23 ") == "ABC23"
    assert is_valid_code(normalize_code(" abc23 "))


def test_generated_codes_are_valid_and_unique() -> None:
    taken = {"AAAAA"}
    code = generate_code(taken.__contains__)
    assert len(code) == CODE_LENGTH
    assert is_valid_code(code)
    assert code not in taken


def test_names_compare_without_case_accents_or_extra_spaces() -> None:
    assert normalize_name("  Dáni ") == normalize_name("dani")
    assert clean_display("  Ana   María ") == "Ana María"
