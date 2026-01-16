from typing import List, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    account_id: str
    role: Literal["creator", "commenter"]
    first_seen: datetime

class GraphEdge(BaseModel):
    from_node: str  # commenter
    to_node: str    # creator
    comment_count: int = 0
    like_count: int = 0
    first_interaction: datetime
    last_interaction: datetime
    recency_weight: float = Field(..., ge=0.0, le=1.0)

class EngagementGraph(BaseModel):
    window: Literal["24h", "7d", "30d"]
    nodes: Dict[str, GraphNode] = Field(default_factory=dict)
    edges: List[GraphEdge] = Field(default_factory=list)
    status: Literal["OK", "INCONCLUSIVE"]
    built_at: datetime = Field(default_factory=datetime.utcnow)
