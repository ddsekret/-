import re
import logging
from typing import Optional, List
from dateparser import parse as date_parse

logger = logging.getLogger(__name__)

def find_name(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для ФИО: {text_cleaned[:100]}")
    STOPWORDS = ['паспорт', 'серия', 'номер', 'адрес', 'телефон', 'автомобиль', 'прицеп', 'выдан', 'уфмс', 'мвд']
    FIO_STOPWORDS = ['выдан', 'отдел', 'уфмс', 'мвд', 'по', 'рф', 'обл', 'области', 'республике']
    initial_to_name = {
        'и.': {'male': 'Иван', 'female': 'Ирина'},
        'с.': {'male': 'Сергей', 'female': 'Светлана'},
        'в.': {'male': 'Вячеслав', 'female': 'Вера'},
        'г.': {'male': 'Геннадий', 'female': 'Галина'},
        'а.': {'male': 'Александр', 'female': 'Александра'},
        'л.': {'male': 'Леонид', 'female': 'Людмила'},
        'ю.': {'male': 'Юрий', 'female': 'Юлия'},
        'э.': {'male': 'Эльдар', 'female': 'Эльвира'},
        'м.': {'male': 'Михаил', 'female': 'Мария'},
        'т.': {'male': 'Тимур', 'female': 'Татьяна'},
        'н.': {'male': 'Николай', 'female': 'Наталья'},
        'д.': {'male': 'Дмитрий', 'female': 'Дарья'},
        'п.': {'male': 'Павел', 'female': 'Полина'},
    }

    def is_valid_fio_candidate(fio: str) -> bool:
        fio_lower = fio.lower()
        valid = (not any(word in fio_lower for word in FIO_STOPWORDS) and
                 len(fio.split()) >= 2 and fio != 'ФИО ВОДИТЕЛЯ')
        logger.debug(f"Проверка кандидата ФИО: {fio}, валидно: {valid}")
        return valid

    def expand_shortened_fio(fio: str) -> Optional[str]:
        parts = fio.strip().split()
        if len(parts) >= 3 and all(part[0].isupper() for part in parts if part):
            logger.debug(f"Полное ФИО найдено: {fio}")
            return fio
        if len(parts) >= 2 and '.' in parts[-1]:
            surname = parts[0]
            initials = [i.strip('.') for i in parts[-1].split('.')]
            if len(initials) == 2 and all(i.lower() in initial_to_name for i in initials if i):
                gender = 'male' if surname.endswith('ич') or surname.endswith('ий') else 'female'
                expanded = f"{surname} {initial_to_name[initials[0].lower()][gender]} {initial_to_name[initials[1].lower()][gender]}"
                logger.debug(f"Расширенное ФИО: {fio} -> {expanded}")
                return expanded
        cleaned_fio = re.sub(r'^(?:водитель|ф\.и\.о\.|данные\s*о\s*водителе)\s*[:\-]?\s*', '', fio, flags=re.IGNORECASE).strip()
        parts = cleaned_fio.split()
        if len(parts) >= 3 and all(part[0].isupper() for part in parts if part):
            logger.debug(f"Очищенное полное ФИО: {cleaned_fio}")
            return cleaned_fio
        logger.debug(f"Не удалось расширить ФИО: {fio}")
        return None

    patterns = [
        re.compile(r'(?i)(?:водитель|ф\.и\.о\.|данные\s*о\s*водителе)\s*[:\-]?\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)\b', re.UNICODE),
        re.compile(r'(?i)(?:водитель|ф\.и\.о\.|данные\s*о\s*водителе)\s*[:\-]?\s*([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)\b', re.UNICODE),
        re.compile(r'(?i)\b([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)\b', re.UNICODE),
        re.compile(r'(?i)\b([А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)\b', re.UNICODE),
    ]
    candidates = []
    for pattern in patterns:
        logger.debug(f"Применён шаблон для ФИО: {pattern.pattern}")
        for match in pattern.finditer(text_cleaned):
            fio = match.group(1).strip()
            if is_valid_fio_candidate(fio):
                context = text_cleaned[max(0, match.start() - 50):match.start()].lower()
                priority = 300 if any(kw in context for kw in ['водитель', 'ф.и.о.', 'данные о водителе']) else 200
                word_count = len(fio.split())
                priority += word_count * 100
                logger.debug(f"Кандидат ФИО: {fio}, приоритет: {priority}, контекст: {context}")
                candidates.append((fio, priority, match.start()))
            else:
                logger.debug(f"Кандидат ФИО {fio} исключён: не валиден")
    if not candidates:
        logger.debug("ФИО не найдено")
        return None
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return expand_shortened_fio(candidates[0][0])

def extract_date_of_birth(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для даты рождения: {text_cleaned[:100]}")
    patterns = [
        re.compile(r'(?i)(?:д\.р\.|дата\s*рождения)[\s:]*(\d{2}\.\d{2}\.\d{4})\b', re.UNICODE),
        re.compile(r'(?i)\b(\d{2}\.\d{2}\.\d{4})\b(?!\s*(?:выдан|код|тел|паспорт|серия|водительское))', re.UNICODE),
    ]
    for pattern in patterns:
        logger.debug(f"Применён шаблон для даты рождения: {pattern.pattern}")
        match = pattern.search(text_cleaned)
        if match:
            date_str = match.group(1)
            parsed_date = date_parse(date_str, settings={'DATE_ORDER': 'DMY'})
            if parsed_date and 1900 <= parsed_date.year <= 2007:
                formatted_date = parsed_date.strftime('%d.%m.%Y')
                logger.debug(f"Извлечена дата рождения: {formatted_date}")
                return formatted_date
            logger.debug(f"Дата {date_str} исключена: вне диапазона 1900-2007")
    logger.debug("Дата рождения не найдена")
    return None

def extract_phone(text: str) -> List[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для телефона: {text_cleaned[:100]}")
    patterns = [
        re.compile(r'(?:тел[\.:]?\s*)?(?:\+7|8)[\-\s]?\d{3}[\-\s]?\d{3}[\-\s]?\d{2}[\-\s]?\d{2}\b', re.UNICODE),
        re.compile(r'(?:тел[\.:]?\s*)?(?:\+\d{1,3}|8)\d{10}\b', re.UNICODE),
    ]
    phones = []
    for pattern in patterns:
        logger.debug(f"Применён шаблон для телефона: {pattern.pattern}")
        for match in pattern.finditer(text_cleaned):
            phone = match.group(0)
            phone = re.sub(r'[^0-9+]', '', phone)
            if len(phone) >= 11:
                formatted_phone = f"+7 ({phone[-10:-7]}) {phone[-7:-4]}-{phone[-4:-2]}-{phone[-2:]}"
                if formatted_phone not in phones:
                    logger.debug(f"Извлечён телефон: {formatted_phone}")
                    phones.append(formatted_phone)
    return phones

def extract_driver_license(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для ВУ: {text_cleaned[:100]}")
    patterns = [
        re.compile(r'(?i)(?:ву|водительское\s*удостоверение|права)[\s:]*(\d{2}\s*\d{2}\s*\d{6})\b', re.UNICODE),
        re.compile(r'(?i)(?:ву|водительское\s*удостоверение|права)[\s:]*(\d{4}\s*\d{6})\b', re.UNICODE),
        re.compile(r'(?i)(?:ву|водительское\s*удостоверение|права)[\s:]*(\d{10})\b', re.UNICODE),
    ]
    candidates = []
    for pattern in patterns:
        logger.debug(f"Применён шаблон для ВУ: {pattern.pattern}")
        for match in pattern.finditer(text_cleaned):
            license = match.group(1).replace(' ', '')
            if len(license) == 10:
                license = f"{license[:4]} {license[4:]}"
                context = text_cleaned[max(0, match.start() - 50):match.end() + 50].lower()
                priority = 200 if 'ву' in context or 'водительское' in context or 'права' in context else 100
                if 'паспорт' in context or 'серия' in context:
                    priority -= 100
                logger.debug(f"Кандидат ВУ: {license}, приоритет: {priority}, контекст: {context[:100]}")
                candidates.append((license, priority, match.start()))
    if not candidates:
        logger.debug("ВУ не найдено")
        return None
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return candidates[0][0]

def extract_personal_data(text: str) -> dict:
    result = {}
    name = find_name(text)
    if name:
        result['Водитель'] = name
    date_of_birth = extract_date_of_birth(text)
    if date_of_birth:
        result['Дата_рождения'] = date_of_birth
    phones = extract_phone(text)
    if phones:
        result['Телефон'] = phones
    driver_license = extract_driver_license(text)
    if driver_license:
        result['ВУ_серия_и_номер'] = driver_license
    logger.debug(f"Результат личных данных: {result}")
    return result
