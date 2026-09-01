import re

def normalize_entity(entity_type: str, raw_text: str) -> str:
    """
    Normalizes an entity string based on its type without destroying its meaning.
    """
    if not raw_text:
        return ""
        
    text = str(raw_text).strip()
    
    if entity_type == "PERSON":
        # Lowercase, remove excess whitespace
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        # Remove common titles for matching purposes (optional, careful not to over-normalize)
        # We will just do basic punctuation strip at the ends
        text = text.strip(".,;")
        return text
        
    elif entity_type == "PHONE":
        # Keep only digits and plus sign
        text = re.sub(r'[^\d+]', '', text)
        # If starts with 0 and length > 10, strip 0 (Indian context often has 0 prefix)
        if text.startswith('0') and len(text) > 10:
            text = text[1:]
        # Standardize +91 prefix
        if text.startswith('91') and len(text) == 12:
            text = '+' + text
        elif len(text) == 10:
            text = '+91' + text
        return text
        
    elif entity_type == "VEHICLE":
        # Remove all whitespace and hyphens, uppercase
        text = text.upper()
        text = re.sub(r'[\s\-]', '', text)
        return text
        
    elif entity_type == "ORGANIZATION":
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip(".,;")
        # Could remove "pvt ltd", "inc" etc, but maybe safer to keep for now
        return text
        
    elif entity_type == "LOCATION":
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip(".,;")
        return text
        
    elif entity_type == "DATE":
        # For dates, normalization might require parsing (e.g. dateutil). 
        # For now, just clean spacing.
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text

    return text
