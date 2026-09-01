from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ResolutionContext:
    phones: List[str] = field(default_factory=list)
    vehicles: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)
    dates: List[str] = field(default_factory=list)
