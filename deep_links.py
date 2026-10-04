from typing import Dict, List
from urllib.parse import urlencode, quote_plus


class UnsupportedBankError(ValueError):
    """Запрошен неизвестный банк."""
    pass


class UnsupportedOSError(ValueError):
    """Запрошена неподдерживаемая ОС."""
    pass


SUPPORTED_BANKS = {
    "tinkoff",
    "alfa",
    "sber",
    "vtb",
    "gazprom",
    "ozon",
    "wildberries",
}

SUPPORTED_OSES = {"ios", "android"}


def _build_test_link(bank: str, os: str, data: Dict) -> str:
    """
    Единое место генерации тестового диплинка.

    Здесь легко будет заменить `test-{bank}-{os}://...` на реальные схемы
    для каждого банка/ОС.
    """
    base_scheme = f"test-{bank}-{os}://pay"

    personal_acc = data.get("PersonalAcc", "")
    sum_rub = data.get("SumRub")
    purpose = data.get("Purpose", "")

    if sum_rub is None:
        # По ТЗ SumRub обязателен, но на всякий случай дополнительно проверим
        raise ValueError("Отсутствует поле SumRub в данных платежа")

    query_params = {
        "account": personal_acc,
        "sum": str(sum_rub),
        "purpose": purpose,
    }

    query_string = urlencode(query_params, quote_via=quote_plus)
    return f"{base_scheme}?{query_string}"


def generate_deep_links(bank: str, os: str, data: Dict) -> List[str]:
    """
    Генерация диплинков по банку и ОС.

    На вход:
        bank — один из: tinkoff, alfa, sber, vtb, gazprom, ozon, wildberries
        os   — "ios" или "android"
        data — результат parse_gost(...)

    На выход:
        список строк-URL (может быть несколько для одного банка).
        Сейчас для простоты возвращаем по одному URL.
    """
    bank_normalized = bank.lower()
    os_normalized = os.lower()

    if bank_normalized not in SUPPORTED_BANKS:
        raise UnsupportedBankError(
            f"Неподдерживаемый банк: '{bank}'. Разрешены: {', '.join(sorted(SUPPORTED_BANKS))}"
        )

    if os_normalized not in SUPPORTED_OSES:
        raise UnsupportedOSError(
            f"Неподдерживаемая ОС: '{os}'. Разрешены: ios, android"
        )

    link = _build_test_link(bank_normalized, os_normalized, data)
    return [link]
