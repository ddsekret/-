from .main import parse_by_keywords

def parse_text(text, is_driver_data=True):
    return parse_by_keywords(text, is_driver_data)
