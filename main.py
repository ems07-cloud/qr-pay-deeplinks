# main.py
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import DeepLinkRequest, DeepLinkResponse
from gost_parser import parse_gost, GostParseError
from deep_links import (
    generate_deep_links,
    UnsupportedBankError,
    UnsupportedOSError,
    SUPPORTED_BANKS,
)
from link_service import get_links as get_test_links

BASE_DIR = Path(__file__).resolve().parent
OPEN_PAGE_PATH = BASE_DIR / "open_page.html"
CHOOSE_BANK_PAGE_PATH = BASE_DIR / "choose_bank.html"

app = FastAPI(
    title="Payment Deep Link Generator",
    version="2.0.0",
    description=(
        "Сервис для генерации диплинков оплаты:\n"
        "- Этап 1: генерация диплинков по ГОСТ/ST00012.\n"
        "- Этап 2: универсальные ссылки /open/{bank}/{invoice_id} и выбор банка.\n"
    ),
)

# Static для JS
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


# ==========================
# Этап 1 — старый эндпоинт
# ==========================
@app.post("/api/v1/deeplink", response_model=DeepLinkResponse)
async def create_deeplink(payload: DeepLinkRequest) -> DeepLinkResponse:
    """
    Сгенерировать диплинки оплаты по строке ГОСТ/ST00012.

    Валидация:
    - неизвестный банк → 400
    - неверная ОС (не ios/android) → 400
    - ошибка парсинга ГОСТ → 400
    """
    try:
        parsed_data = parse_gost(payload.gost)
    except GostParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        links = generate_deep_links(payload.bank, payload.os, parsed_data)
    except UnsupportedBankError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except UnsupportedOSError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return DeepLinkResponse(links=links)


# ==========================
# Этап 2 — универсальная ссылка
# ==========================

@app.get("/open/{bank}/{invoice_id}")
async def open_payment_page(bank: str, invoice_id: str):
    """
    Универсальная ссылка для автоопределения ОС и открытия диплинка.

    Возвращает HTML-страницу (open_page.html), где JS:
    - определяет ОС (ios/android/unknown),
    - дергает /api/v1/get_links,
    - перебирает диплинки.
    """
    if bank.lower() not in SUPPORTED_BANKS:
        raise HTTPException(status_code=400, detail="Неподдерживаемый банк")

    if not OPEN_PAGE_PATH.exists():
        raise HTTPException(status_code=500, detail="Файл open_page.html не найден")

    return FileResponse(str(OPEN_PAGE_PATH))


@app.get("/choose-bank/{invoice_id}")
async def choose_bank_page(invoice_id: str):
    """
    Страница выбора банка.
    На ней пользователь выбирает банк → переход на /open/{bank}/{invoice_id}.
    """
    if not CHOOSE_BANK_PAGE_PATH.exists():
        raise HTTPException(status_code=500, detail="Файл choose_bank.html не найден")

    return FileResponse(str(CHOOSE_BANK_PAGE_PATH))


@app.get("/api/v1/get_links", response_model=DeepLinkResponse)
async def api_get_links(
    bank: str = Query(..., description="Идентификатор банка"),
    os: str = Query(..., description="ОС: ios или android"),
    invoice: str = Query(..., description="Идентификатор платежа"),
) -> DeepLinkResponse:
    """
    Backend-эндпоинт для получения тестовых диплинков по банку/ОС/счёту.

    Формат ответа:
    {
      "links": [
        "test-{bank}-{os}://pay?invoice=..."
      ]
    }
    """
    try:
        links = get_test_links(bank=bank, os=os, invoice=invoice)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return DeepLinkResponse(links=links)


# Пример запуска:
#   uvicorn main:app --reload
#
# Пример универсальной ссылки:
#   http://127.0.0.1:8000/open/tinkoff/INV-123
#
# Страница выбора банка:
#   http://127.0.0.1:8000/choose-bank/INV-123
