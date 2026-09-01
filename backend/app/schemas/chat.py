from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict, Any

class ChatQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, strip_whitespace=True)
    session_id: Optional[UUID4] = None

class ChatResponse(BaseModel):
    message: str
    provider: str
    timestamp: str
    status: str
    intent: Optional[str] = None
    structured_data: Optional[List[Dict[str, Any]]] = None
    record_count: Optional[int] = None
