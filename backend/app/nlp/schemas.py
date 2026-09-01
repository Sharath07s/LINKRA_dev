from pydantic import BaseModel
from typing import List, Optional

class ExtractedEntity(BaseModel):
    # PLACEHOLDER
    entity_type: str
    raw_text: str
    confidence: float
