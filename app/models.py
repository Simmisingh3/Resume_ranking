from pydantic import BaseModel
from typing import List, Dict

class CriteriaRequest(BaseModel):
    criteria: List[str]

class ScoreResponse(BaseModel):
    candidates: List[Dict[str, int]]
