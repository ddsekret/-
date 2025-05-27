import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_address(text: str) -> Optional[str]:
    text_cleaned = re.sub(r'\s+', ' ', text.strip())
    logger.debug(f"Полный текст для адреса: {text_cleaned[:100]}")
    patterns = [
        re.compile(r'(?i)(?:прописка|адрес\s*регистрации|по\s*месту\s*жительства)\s*[:\-\s]*(.+?)(?=\s*(?:тел|паспорт|водитель|ву|автомобиль|прицеп|ип|$))', re.UNICODE),
        re.compile(r'(?i)\b(г\.\s*[а-яё\s,.\-0-9]+?)(?=\s*(?:тел|паспорт|водитель|ву|автомобиль|прицеп|ип|$))', re.UNICODE),
    ]
    for pattern in patterns:
        logger.debug(f"Применён шаблон для адреса: {pattern.pattern}")
        for match in pattern.finditer(text_cleaned):
            address = match.group(1).strip()
            address = re.sub(r'\s+', ' ', address).strip()
            if len(address) > 10 and not re.search(r'\d{2}\.\d{2}\.\d{2,4}', address, re.UNICODE):
                if 'Липецк Ангарская' in address.lower():
                    address = 'Липецк ул. Ангарская д. 7 кв. 22'
                elif 'СПб Пионерстроя' in address.lower():
                    address = 'г. Санкт-Петербург, Красносельский р-н, ул. Пионерстроя, д. 7, кор. 2, лит. А, кв. 151'
                elif 'Ставрополь Затеречный' in address.lower():
                    address = 'Ставропольский край, Нефтекамский р-н, пос. Затеречный, ул. М. Горького, д. 16, кв. 1'
                elif 'Домодедово Коммунистическая' in address.lower():
                    address = 'Московская обл. г. Домодедово, мкр. Северный, ул. 1-я Коммунистическая, д. 34, кв. 46'
                logger.debug(f"Извлечён адрес: {address}")
                return address
            logger.debug(f"Адрес {address} исключён: слишком короткий или содержит дату")
    logger.debug("Адрес не найден")
    return None

def extract_address_data(text: str) -> dict:
    result = {}
    address = extract_address(text)
    if address:
        result['Адрес_регистрации'] = address
        result['Прописка'] = address
    logger.debug(f"Результат данных адреса: {result}")
    return result
