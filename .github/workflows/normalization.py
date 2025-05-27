# -*- coding: utf-8 -*-
# parser/normalization.py
from typing import Dict, Optional
from .imports_and_settings import re, logger, SUBDIVISIONS, COMPOSITE_CITIES, CITY_NOMINATIVE, SMALL_WORDS, CAR_BRANDS, TRAILER_BRANDS, PROTECTED_STREET_NAMES

logger.debug("Логгер инициализирован в normalization")
logger.handlers[0].flush()

def normalize_data(data: Dict[str, Optional[str]], text: str) -> Dict[str, Optional[str]]:
    """Нормализует извлечённые данные (адреса, место выдачи паспорта, номера)."""
    normalized = data.copy()
    logger.debug(f"Нормализация данных: {normalized}")
    logger.handlers[0].flush()

    # Нормализация Паспорт_место_выдачи с использованием SUBDIVISIONS
    if "Паспорт_код_подразделения" in normalized and normalized["Паспорт_код_подразделения"]:
        code = normalized["Паспорт_код_подразделения"]
        if code in SUBDIVISIONS:
            subdivision_data = SUBDIVISIONS[code]
            place = subdivision_data['subdivision']
            region = subdivision_data.get('region', '')
            if "Паспорт_место_выдачи" not in normalized or not normalized["Паспорт_место_выдачи"]:
                normalized["Паспорт_место_выдачи"] = place
                logger.debug(f"Установлено место выдачи паспорта: {place}")
                logger.handlers[0].flush()
            elif region and region.lower() not in normalized["Паспорт_место_выдачи"].lower():
                normalized["Паспорт_место_выдачи"] = f"{place} ({region})"
                logger.debug(f"Нормализовано место выдачи паспорта: {normalized['Паспорт_место_выдачи']}")
                logger.handlers[0].flush()
        else:
            logger.warning(f"Код подразделения {code} не найден в SUBDIVISIONS")
            logger.handlers[0].flush()
    if "Паспорт_место_выдачи" in normalized and normalized["Паспорт_место_выдачи"]:
        place = normalized["Паспорт_место_выдачи"]
        place = re.sub(r'\bг\.([А-Яа-яЁё])', r'г. \1', place)
        place = re.sub(r'\s*(?:выдан|дата\s*выдачи|с\s*\d{2}\.\d{2}\.\d{4}|от\s*\d{2}\.\d{2}\.\d{4}|регистрация|дата\s*рождения).*', '', place, flags=re.IGNORECASE)
        normalized["Паспорт_место_выдачи"] = place.strip()
        logger.debug(f"Очищено место выдачи паспорта: {normalized['Паспорт_место_выдачи']}")
        logger.handlers[0].flush()

    # Нормализация адреса регистрации
    if "Адрес_регистрации" in normalized and normalized["Адрес_регистрации"]:
        address = normalized["Адрес_регистрации"]
        address = re.sub(r'\s*Код\s*подразделения\s*\d{3}-\d{3}\b', '', address, flags=re.IGNORECASE)
        address = re.sub(r'\bдом\.?\s*(\d+)', r'дом. \1', address, flags=re.IGNORECASE)
        address = re.sub(r'\bд\.?\s*(\d+)', r'д. \1', address, flags=re.IGNORECASE)
        address = re.sub(r'\bкв\.?\s*(\d+)', r'кв. \1', address, flags=re.IGNORECASE)
        address = re.sub(r'\bпос\.?\s*([А-Яа-яЁё]+)', r'пос. \1', address, flags=re.IGNORECASE)
        for key, value in PROTECTED_STREET_NAMES.items():
            address = re.sub(rf'(ул\.?\s*){key}', rf'\1{value}', address, flags=re.IGNORECASE)
        for key, value in COMPOSITE_CITIES.items():
            address = re.sub(rf'\b{key}\b', value, address, flags=re.IGNORECASE)
        for key, value in CITY_NOMINATIVE.items():
            address = re.sub(rf'\b{key}\b', value, address, flags=re.IGNORECASE)
        address = re.sub(r'\bкв\s+артира\b', 'квартира', address, flags=re.IGNORECASE)
        address = re.sub(r'\s+', ' ', address).strip()
        words = address.split()
        formatted_address = []
        for i, word in enumerate(words):
            if word.lower() in SMALL_WORDS or word.lower() in {'ул.', 'д.', 'кв.', 'б-р'}:
                formatted_address.append(word.lower())
            else:
                formatted_address.append(word.capitalize())
        address = ' '.join(formatted_address)
        address = re.sub(r'\bДом\.(\s|$)', r'дом.\1', address, flags=re.IGNORECASE)
        address = re.sub(r'\.\s*$', '', address)
        normalized["Адрес_регистрации"] = address
        logger.debug(f"Нормализован адрес регистрации: {normalized['Адрес_регистрации']}")
        logger.handlers[0].flush()

    # Нормализация автомобиля
    if "Автомобиль" in normalized and normalized["Автомобиль"]:
        vehicle = normalized["Автомобиль"].strip()
        parts = vehicle.split(maxsplit=1)
        if len(parts) > 1:
            brand, number = parts
            brand = brand.strip()
            brand_lower = brand.lower()
            # Специальная обработка для Mercedes
            if brand_lower == "mercedes":
                normalized_brand = "Mercedes"
            else:
                normalized_brand = CAR_BRANDS.get(brand_lower, brand.title())
            number = re.sub(r'\s+', '', number).upper()
            vehicle = f"{normalized_brand} {number}"
        else:
            vehicle = vehicle.strip().upper()
        normalized["Автомобиль"] = vehicle

    # Нормализация прицепа
    if "Прицеп" in normalized and normalized["Прицеп"]:
        trailer = normalized["Прицеп"].strip()
        parts = trailer.split(maxsplit=1)
        if len(parts) > 1:
            brand, number = parts
            brand = brand.strip()
            brand_lower = brand.lower()
            normalized_brand = TRAILER_BRANDS.get(brand_lower, brand.title())
            number = re.sub(r'\s+', '', number).upper()
            trailer = f"{normalized_brand} {number}"
        else:
            trailer = trailer.strip().upper()
        normalized["Прицеп"] = trailer

    return normalized
