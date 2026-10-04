from typing import List

from pydantic import BaseModel, Field


class DeepLinkRequest(BaseModel):
    """
    Входные данные для генерации диплинка оплаты.
    """
    bank: str = Field(..., description="Идентификатор банка (tinkoff, alfa, sber, vtb, gazprom, ozon, wildberries)")
    os: str = Field(..., description="ОС клиента: ios или android")
    gost: str = Field(..., description="Строка в формате ГОСТ/ST00012 (как в платежных QR)")


class DeepLinkResponse(BaseModel):
    """
    Ответ сервиса с набором диплинков.
    """
    links: List[str] = Field(..., description="Список сгенерированных диплинков")
