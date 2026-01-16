from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .domain import Platform

class RawComment(BaseModel):
    id: str
    text: str
    timestamp: datetime
    author_id: str
    like_count: int = 0
    reply_count: int = 0
    is_pinned: bool = False

class RawPost(BaseModel):
    id: str
    platform: Platform
    url: str
    caption: Optional[str] = None
    timestamp: datetime
    like_count: int
    comment_count: int
    share_count: Optional[int] = 0
    view_count: Optional[int] = 0
    media_urls: List[str] = Field(default_factory=list)
    is_video: bool = False
    comments: List[RawComment] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Platform specific raw metadata")

class RawProfile(BaseModel):
    handle: str
    platform: Platform
    follower_count: int
    following_count: int
    post_count: int
    bio: Optional[str] = None
    profile_pic_url: Optional[str] = None
    is_verified: bool = False
    external_url: Optional[str] = None
    posts: List[RawPost] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
