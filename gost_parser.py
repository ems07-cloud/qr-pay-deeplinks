from typing import Dict, Any


class GostParseError(ValueError):
    """Ошибка при парсинге строки ГОСТ."""
    pass


REQUIRED_FIELDS = {
    "Name",
    "PersonalAcc",
    "BankName",
    "BIC",
    "CorrespAcc",
    "Sum",
    "SumRub",
    "Purpose",
    "PayeeINN",
}


def parse_gost(gost_string: str) -> Dict[str, Any]:
    """
    Парсинг строки ГОСТ/ST00012 в словарь.

    Формат:
    ST00012|Key1=Value1|Key2=Value2|...

    - Игнорируется префикс ST00012
    - Разделитель полей: "|"
    - Каждое поле: ключ=значение
    - Sum и SumRub приводятся к int
    """
    if not gost_string:
        raise GostParseError("Пустая строка ГОСТ")

    raw = gost_string.strip()
    parts = raw.split("|")

    if not parts:
        raise GostParseError("Некорректная строка ГОСТ")

    # Игнорируем префикс ST00012, если он есть в начале
    if parts[0].startswith("ST"):
        parts = parts[1:]

    if not parts:
        raise GostParseError("Отсутствуют поля после префикса ST00012")

    data: Dict[str, Any] = {}

    for part in parts:
        if not part:
            # Пустой сегмент (двойной ||) считаем ошибкой — строка битая
            raise GostParseError("Обнаружен пустой сегмент в строке ГОСТ")
        if "=" not in part:
            raise GostParseError(f"Сегмент без '=' в строке ГОСТ: '{part}'")
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise GostParseError(f"Пустой ключ в сегменте: '{part}'")

        if key in ("Sum", "SumRub"):
            try:
                data[key] = int(value)
            except ValueError:
                raise GostParseError(f"Поле {key} должно быть числом: '{value}'")
        else:
            data[key] = value

    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise GostParseError(
            f"Отсутствуют обязательные поля ГОСТ: {', '.join(sorted(missing))}"
        )

    return data
