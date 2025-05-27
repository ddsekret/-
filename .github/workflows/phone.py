# -*- coding: utf-8 -*-
# driver_parser/phone.py
import re
import logging
from typing import Optional, List
from .imports_and_settings import logging

logger = logging.getLogger(__name__)

PHONE_PATTERNS = [
    re.compile(r'(?i)\b(?:тел\.?|телефон|моб\.?)\s*[:\-\s]*(\+?\d[\d\s\-\(\)]{9,})\b'),
    re.compile(r'(?i)\b(\+?[78][\d\s\-\(\)]{9,})\b'),
    re.compile(r'(?i)\b(\+?\d{1,2}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2})\b'),
]

def extract_phone_number(text: str) -> Optional[List[str]]:
    """Extracts phone numbers from text and formats them.

    Args:
        text: Input text containing potential phone numbers.

    Returns:
        List of formatted phone numbers (e.g., ['+7 (XXX) XXX-XX-XX']) or None if not found.
    """
    logger.debug(f"Извлечение телефона: {text[:200]}...")
    phones = []
    text_normalized = re.sub(r'\s+', ' ', text).strip()

    for pattern in PHONE_PATTERNS:
        for match in pattern.finditer(text_normalized):
            phone = match.group(1).strip()
            phone_clean = re.sub(r'[^\d]', '', phone)
            if len(phone_clean) < 10 or len(phone_clean) > 12:
                continue
            if phone_clean.startswith('7') or phone_clean.startswith('8'):
                phone_clean = '+7' + phone_clean[1:]
            elif not phone_clean.startswith('+'):
                phone_clean = '+7' + phone_clean
            if len(phone_clean) == 12:
                formatted_phone = f"{phone_clean[:2]} ({phone_clean[2:5]}) {phone_clean[5:8]}-{phone_clean[8:10]}-{phone_clean[10:12]}"
                if formatted_phone not in phones:
                    phones.append(formatted_phone)
                    logger.debug(f"Выбран телефон: {formatted_phone}")

    if phones:
        return phones
    logger.warning(f"Не удалось извлечь телефон: {text[:100]}...")
    return None