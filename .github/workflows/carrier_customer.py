# -*- coding: utf-8 -*-
# parser/carrier_customer.py
import re
from typing import Dict, Optional
from .imports_and_settings import logger

logger.debug("Логгер инициализирован в carrier_customer")
logger.handlers[0].flush()

def parse_carrier_customer_data(text: str) -> Dict[str, Optional[str]]:
    """Parses carrier/customer data from text."""
    logger.debug(f"Поиск данных перевозчика в тексте: {text[:100]}...")
    data = {
        "Перевозчик": None,
        "Короткое название": None
    }

    carrier_pattern = r"(?i)перевозчик\s*[:\-\s]*(.*?)(?=\s*$)"
    carrier_match = re.search(carrier_pattern, text, re.MULTILINE)
    if carrier_match:
        carrier = carrier_match.group(1).strip()
        data["Перевозчик"] = carrier
        logger.debug(f"Перевозчик извлечён: {data['Перевозчик']}")

        # Extract short name (e.g., last name from "ИП Иванов")
        short_name_pattern = r"(?i)ИП\s+([А-ЯЁ][а-яё]+)"
        short_name_match = re.search(short_name_pattern, carrier)
        if short_name_match:
            data["Короткое название"] = short_name_match.group(1)
            logger.debug(f"Короткое название извлечено: {data['Короткое название']}")
        else:
            # If no "ИП", use the last word as short name
            words = carrier.split()
            if words:
                data["Короткое название"] = words[-1]
                logger.debug(f"Короткое название извлечено (последнее слово): {data['Короткое название']}")
    else:
        logger.debug("Перевозчик не найден")

    return data
