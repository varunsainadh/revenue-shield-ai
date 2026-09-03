from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CopilotQueryRequest(BaseModel):
    query: str

class CopilotQueryResponse(BaseModel):
    query: str
    answer: str
    insights: List[str]
    suggested_actions: List[str]
    context_data: Optional[Dict[str, Any]] = None
