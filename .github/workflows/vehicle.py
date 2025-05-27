import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def normalize_vehicle_number(text: str, is_trailer: bool = False) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для {'прицепа' if is_trailer else 'автомобиля'}: {text_cleaned[:100]}")
    VEHICLE_PATTERNS = [
        re.compile(r'(?i)(?:автомобиль|машина|а\/м|тягач)\s*[:\-\s]*(?:№\s*)?([А-ЯЁA-Z0-9\s\/-]{6,30})\b', re.UNICODE),
        re.compile(r'(?i)\b(ман|вольво|скания|мерседес|даф|jac|volvo|scania|mersedes-benz)\s*([А-ЯЁ]{1,2}\s*\d{3}\s*[А-ЯЁ]{2}\s*\d{2,3})\b', re.UNICODE),
        re.compile(r'(?i)\b([А-ЯЁA-Z0-9\s\/-]{6,30})\b(?=\s*(?:ман|вольво|скания|мерседес|даф|jac|volvo|scania|mersedes))\b', re.UNICODE),
    ]
    TRAILER_PATTERNS = [
        re.compile(r'(?i)(?:прицеп|п\/п|п\/прицеп)\s*[:\-\s]*(?:№\s*)?([А-ЯЁA-Z0-9\s\/]{6,20})\b', re.UNICODE),
        re.compile(r'(?i)(?:прицеп|п\/п|п\/прицеп)\s*[:\-\s]*(?:№\s*)?(шмиц|кроне)\s*([а-яёa-z0-9\s\/]{6,20})\b', re.UNICODE),
        re.compile(r'(?i)\b([А-ЯЁ]{1,2}\s*\d{4}\s*\/?\s*\d{2,3})\b', re.UNICODE),
    ]
    patterns = TRAILER_PATTERNS if is_trailer else VEHICLE_PATTERNS
    candidates = []
    for pattern in patterns:
        logger.debug(f"Применён шаблон для {'прицепа' if is_trailer else 'автомобиля'}: {pattern.pattern}")
        for match in pattern.finditer(text_cleaned):
            vehicle = match.group(1).strip()
            if is_trailer and len(match.groups()) > 1:
                vehicle = f"{match.group(1)} {match.group(2)}".strip()
            context = text_cleaned[max(0, match.start() - 50):match.start()].lower()
            priority = 300 if ('автомобиль' in context or 'машина' in context or 'а/м' in context or 'тягач' in context) and not is_trailer else 200
            if is_trailer and ('прицеп' in context or 'п/п' in context or 'п/прицеп' in context or 'шмиц' in vehicle.lower() or 'кро' in vehicle.lower()):
                priority += 50
            if 'мерседес' in context or 'mersedes' in vehicle.lower():
                vehicle = vehicle.replace('MERSEDES', 'MERSEDES-BENZ').replace('Мерседес', 'MERSEDES-BENZ')
            if re.match(r'[А-ЯЁA-Z0-9\s\/-]{6,30}$', vehicle, re.UNICODE):
                logger.debug(f"Кандидат {'прицепа' if is_trailer else 'автомобиля'}: {vehicle}, приоритет: {priority}, контекст: {context}")
                candidates.append((vehicle, priority, match.start()))
            else:
                logger.debug(f"Кандидат {'прицепа' if is_trailer else 'автомобиля'} {vehicle} исключён: не соответствует формату")
    if not candidates:
        logger.debug(f"{'Прицеп' if is_trailer else 'Автомобиль'} не найден")
        return None
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return candidates[0][0]

def extract_vehicle_data(text: str) -> dict:
    result = {}
    vehicle = normalize_vehicle_number(text)
    if vehicle:
        result['Автомобиль'] = vehicle
    trailer = normalize_vehicle_number(text, is_trailer=True)
    if trailer:
        result['Прицеп'] = trailer
    logger.debug(f"Результат данных транспортных средств: {result}")
    return result
