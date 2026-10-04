# link_service.py
from typing import List

from deep_links import SUPPORTED_BANKS, SUPPORTED_OSES


def get_links(bank: str, os: str, invoice: str) -> List[str]:
    bank_norm = bank.lower()
    os_norm = os.lower()

    if bank_norm not in SUPPORTED_BANKS:
        raise ValueError(
            f"Неподдерживаемый банк: '{bank}'. Разрешены: {', '.join(sorted(SUPPORTED_BANKS))}"
        )

    if os_norm not in SUPPORTED_OSES:
        raise ValueError("ОС должна быть 'ios' или 'android'")

    # Возвращаем тестовый диплинк по ТЗ
    link = f"test-{bank_norm}-{os_norm}://pay?invoice={invoice}"
    return [link]

