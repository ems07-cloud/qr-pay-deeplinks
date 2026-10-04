import pytest

from gost_parser import GostParseError, parse_gost

VALID = (
    "ST00012|Name=ООО «Ромашка»|PersonalAcc=40702810900000012345|BankName=АО «Банк»"
    "|BIC=044525974|CorrespAcc=30101810145250000974|Sum=150000|SumRub=1500"
    "|Purpose=Оплата по счёту 42|PayeeINN=7701234567"
)


def test_parses_all_fields_and_casts_sums():
    data = parse_gost(VALID)
    assert data["Name"] == "ООО «Ромашка»"
    assert data["BIC"] == "044525974"
    assert data["Sum"] == 150000
    assert data["SumRub"] == 1500


def test_value_may_contain_equals_sign():
    data = parse_gost(VALID.replace("Оплата по счёту 42", "Оплата=аванс"))
    assert data["Purpose"] == "Оплата=аванс"


def test_works_without_prefix():
    assert parse_gost(VALID.split("|", 1)[1])["PayeeINN"] == "7701234567"


@pytest.mark.parametrize(
    "text, message",
    [
        ("", "Пустая строка"),
        ("ST00012", "Отсутствуют поля"),
        (VALID.replace("|BIC=044525974", ""), "BIC"),
        (VALID.replace("SumRub=1500", "SumRub=полторы"), "SumRub"),
        (VALID.replace("|Sum=", "||Sum="), "пустой сегмент"),
        (VALID + "|битый_сегмент", "без '='"),
    ],
    ids=["empty", "no-fields", "no-bic", "sum-not-number", "double-separator", "no-equals"],
)
def test_rejects_broken_strings(text, message):
    with pytest.raises(GostParseError, match=message):
        parse_gost(text)
