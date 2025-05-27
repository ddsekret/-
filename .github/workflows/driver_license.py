# -*- coding: utf-8 -*-
# parser/driver_license.py
from typing import Dict, Optional
from .imports_and_settings import re, logger

logger.debug("Логгер инициализирован в driver_license")
if logger.handlers:
    logger.handlers[0].flush()

def parse_driver_license_data(text: str) -> Dict[str, Optional[str]]:
    """Parses driver license data from text."""
    logger.debug(f"Поиск данных водительского удостоверения в тексте: {text[:100]}...")
    data = {
        "ВУ_серия_и_номер": None,
        "В/У_дата_срок": None
    }

    # Извлечение серии и номера водительского удостоверения
    license_pattern = r"(?i)(?:Вод\.уд\.?|В/у|ВОД\. УДОСТ\.?|Права)\s*[:\-\s]*(?:(\d{2}\s*\d{2}\s*\d{6})|(\d{4}\s*\d{6}))"
    license_match = re.search(license_pattern, text, re.MULTILINE)
    if license_match:
        if license_match.group(1):
            license_raw = license_match.group(1).strip()
        else:
            license_raw = license_match.group(2).strip()
        data["ВУ_серия_и_номер"] = re.sub(r'\s+', ' ', license_raw).strip()
        logger.debug(f"Водительское удостоверение извлечено: {data['ВУ_серия_и_номер']}")
    else:
        # Альтернативный шаблон для случаев вроде "Вод. Уд. 9920 777159"
        alt_license_pattern = r"(?i)(?:Вод\. Уд\.?|В/у|ВОД\. УДОСТ\.?|Права)\s*[:\-\s]*(\d{4}\s*\d{6})"
        alt_license_match = re.search(alt_license_pattern, text, re.MULTILINE)
        if alt_license_match:
            data["ВУ_серия_и_номер"] = alt_license_match.group(1).strip()
            logger.debug(f"Водительское удостоверение извлечено (альтернативный шаблон): {data['ВУ_серия_и_номер']}")
        else:
            logger.debug("ВУ_серия_и_номер не найдено")

    # Извлечение даты выдачи или срока действия  действия
    date_pattern = r"(?i)(?:Вод\.уд\.?|В/у|ВОД\. УДОСТ\.?|Права)\s*[:\-\s]*(?:\d{2}\s*\d{2}\s*\d{6}|\d{4}\s*\d{6})\s*(?:(?:Выдано|В/У\s*дата\s*срок|дата\s+выдачи|выдано|от)\s*[:\-\s]*\s*)(\d{2}\.\d{2}\.\d{4}(?:\s*г\.)?)(?=\s*(?:Код\s+подразделения|тел\.?|телефон|а/м|прицеп|перевозчик|Дата\s+рождения|$))"
    date_match = re.search(date_pattern, text, re.MULTILINE)
    if date_match:
        data["В/У_дата_срок"] = date_match.group(1).replace(" г.", "").replace("г.", "").strip()
        logger.debug(f"В/У_дата_срок извлечена (regex): {data['В/У_дата_срок']}")
    else:
        # Альтернативный шаблон для случаев вроде "дата выдачи 11.04.2024 г."
        alt_date_pattern = r"(?i)(?:дата\s+выдачи|от|выдано)\s*[:\-\s]*(\d{2}\.\d{2}\.\d{4}(?:\s*г\.)?)(?=\s*(?:Код\s+подразделения|тел\.?|телефон|а/м|прицеп|перевозчик|$))"
        alt_date_match = re.search(alt_date_pattern, text, re.MULTILINE | re.DOTALL)
        if alt_date_match:
            data["В/У_дата_срок"] = alt_date_match.group(1).replace(" г.", "").replace("г.", "").strip()
            logger.debug(f"В/У_дата_срок извлечена (альтернативный шаблон): {data['В/У_дата_срок']}")
        else:
            logger.debug("В/У_дата_срок не найдена")

    return data
