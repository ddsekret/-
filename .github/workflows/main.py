import logging
from typing import Tuple, Dict
from .personal_data import parse_personal_data
from .passport import extract_passport_data
from .vehicle import extract_vehicle_data
from .address import extract_address_data

logger = logging.getLogger(__name__)

def parse_by_keywords(text: str, is_driver_data: bool = False) -> Tuple[bool, Dict]:
    logger.debug(f"MAIN: Parsing text: {text[:100]}...")
    result = {}
    try:
        if is_driver_data:
            result.update(parse_personal_data(text))
            result.update(extract_passport_data(text))
            result.update(extract_vehicle_data(text))
            result.update(extract_address_data(text))
        else:
            logger.debug("MAIN: Non-driver data parsing requested, returning empty dict")
            return False, {}
        
        if not result or all(v is None for v in result.values()):
            logger.debug("MAIN: No valid data extracted, returning empty dict")
            return False, {}
        
        logger.debug(f"MAIN: Result: {result}")
        return True, result
    except Exception as e:
        logger.error(f"MAIN: Error parsing text: {str(e)}")
        return False, {}