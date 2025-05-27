import re
import logging
from typing import Optional
from dateparser import parse as date_parse

logger = logging.getLogger(__name__)

def normalize_passport(passport: str) -> str:
    passport = re.sub(r'[^0-9]', '', passport)
    if len(passport) == 10:
        return f"{passport[:4]} {passport[4:]}"
    logger.debug(f"Некорректный паспорт для нормализации: {passport} (длина: {len(passport)})")
    return passport

def extract_passport_series_and_number(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для паспорта: {text_cleaned[:100]}")
    PASSPORT_PATTERNS = [
        re.compile(r'(?i)(?:паспорт|серия)\s*[:\-\s]*(?:№\s*)?(\d{4}\s*\d{6})\b', re.UNICODE),
        re.compile(r'(?i)(?:паспорт|серия)\s*[:\-\s]*(?:№\s*)?(\d{2}\s*\d{2}\s*\d{6})\b', re.UNICODE),
        re.compile(r'(?i)\b(\d{4}\s*\d{6})\b(?!\s*(?:ву|водительское|права))', re.UNICODE),
        re.compile(r'(?i)\b(\d{2}\s*\d{2}\s*\d{6})\b(?!\s*(?:ву|водительское|права))', re.UNICODE),
        re.compile(r'(?i)(?:паспорт|серия)\s*[:\-\s]*(?:№\s*)?(\d{10})\b', re.UNICODE),
    ]
    candidates = []
    for pattern in PASSPORT_PATTERNS:
        logger.debug(f"Применён шаблон для паспорта: {pattern.pattern}")
        for match in pattern.finditer(text_cleaned):
            passport = match.group(1).replace(' ', '')
            if len(passport) == 10:
                passport = normalize_passport(passport)
                context = text_cleaned[max(0, match.start() - 50):match.end() + 50].lower()
                priority = 300 if 'паспорт' in context or 'серия' in context else 200
                if 'ву' in context or 'водительское' in context or 'права' in context:
                    priority -= 100
                logger.debug(f"Кандидат паспорта: {passport}, приоритет: {priority}, контекст: {context[:100]}")
                candidates.append((passport, priority, match.start()))
            else:
                logger.debug(f"Кандидат паспорта {passport} исключён: длина {len(passport)} не 10")
    if not candidates:
        logger.debug("Паспорт не найден")
        return None
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return candidates[0][0]

def normalize_issuing_authority(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для места выдачи: {text_cleaned[:100]}")
    patterns = [
        re.compile(r'(?i)(?:выдан\s*[а-яё\s,:]*|кем\s*выдан\s*[а-яё\s,:]*)?(?:отдел|мро|уфмс|оуфмс|мвд|тп\s*уфмс|гу\s*мвд|овд|умвд|мп\s*уфмс|отделом\s*уфмс)[а-яё\s,.\-]{5,200}(?=\s*\d{2}\.\d{2}\.\d{2,}|$)', re.UNICODE),
    ]
    for pattern in patterns:
        match = pattern.search(text_cleaned)
        if match:
            authority = match.group(0).strip()
            authority = re.sub(r'otdeeling', 'отделения', authority, flags=re.IGNORECASE)
            logger.debug(f"Извлечено место выдачи: {authority}")
            return authority
    logger.debug("Место выдачи не найдено")
    return None

def extract_passport_date(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для даты выдачи: {text_cleaned[:100]}")
    patterns = [
        re.compile(r'(?i)(?:выдан|паспорт\s*выдан|кем\s*выдан)\s*[а-яё\s,:]*?\b(\d{2}\.\d{2}\.\d{2,4})\b', re.UNICODE),
        re.compile(r'(?i)(?:уф|мвд|овд|оуфмс|тп\s*уфмс|гу\s*мвд|умвд|мп\s*уфмс)\s*[а-яё\s,.\-]+\s*(\d{2}\.\d{2}\.\d{2,4})\b', re.UNICODE),
    ]
    for pattern in patterns:
        match = pattern.search(text_cleaned)
        if match:
            date_str = match.group(1)
            parsed_date = date_parse(date_str, settings={'DATE_ORDER': 'DMY'})
            if parsed_date:
                formatted_date = parsed_date.strftime('%d.%m.%Y')
                logger.debug(f"Извлечена дата выдачи: {formatted_date}")
                return formatted_date
    logger.debug("Дата выдачи не найдена")
    return None

def extract_passport_code(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для кода подразделения: {text_cleaned[:100]}")
    pattern = re.compile(r'(?i)(?:код\s*подразделения|код)[:\-\s]*(\d{3}-\d{3})\b', re.UNICODE)
    match = pattern.search(text_cleaned)
    if match:
        code = match.group(1)
        logger.debug(f"Извлечён код подразделения: {code}")
        return code
    logger.debug("Код подразделения не найден")
    return None

def extract_passport_data(text: str) -> dict:
    result = {}
    passport = extract_passport_series_and_number(text)
    if passport:
        result['Паспорт_серия_и_номер'] = passport
    authority = normalize_issuing_authority(text)
    if authority:
        result['Паспорт_место_выдачи'] = authority
    date = extract_passport_date(text)
    if date:
        result['Паспорт_дата_выдачи'] = date
    code = extract_passport_code(text)
    if code:
        result['Паспорт_код_подразделения'] = code
    logger.debug(f"Результат паспортных данных: {result}")
    return result
