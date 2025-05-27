# -*- coding: utf-8 -*-
# driver_parser/utils.py
import re
from .imports_and_settings import logger, CYRILLIC_TO_LATIN

def normalize_text(text: str) -> str:
    logger.debug(f"UTILS: Normalizing text: {text[:200]}...")
    if not text:
        return ""
    text = text.lower().strip()
    text = ''.join(CYRILLIC_TO_LATIN.get(c, c) for c in text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,-]', '', text)
    return text.strip()

def exclude_authorities(text: str) -> bool:
    logger.debug(f"UTILS: Checking for authorities in: {text[:200]}...")
    if not text:
        return True
    authority_keywords = [
        'уфмс', 'мвд', 'оуфмс', 'тп', 'гу', 'фмс', 'мро', 'ип', 'ооо',
        'паспорт', 'серия', 'номер', 'удостоверение', 'права', 'водительское'
    ]
    text_lower = text.lower()
    return not any(keyword in text_lower for keyword in authority_keywords)