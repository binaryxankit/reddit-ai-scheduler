"""
Data models for Reddit Mastermind content calendar system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum


class ContentType(str, Enum):
    POST = "post"
    REPLY = "reply"


class Persona(BaseModel):
    """Represents a persona with distinct voice and characteristics."""
    name: str
    username: str  # Reddit username (e.g., riley_ops)
    role: str
    voice: str  # Description of writing style
    interests: List[str]
    posting_style: str
    backstory: Optional[str] = None  # Full persona backstory/description


class CompanyInfo(BaseModel):
    """Company information for content generation."""
    name: str
    website: str
    description: str
    target_audience: List[str]
    key_features: List[str]
    domain: str  # Main domain/topic area


class Keyword(BaseModel):
    """A keyword for targeting."""
    keyword_id: str  # e.g., K1, K2
    keyword: str  # e.g., "best ai presentation maker"


class Post(BaseModel):
    """A Reddit post."""
    id: str
    date: datetime
    persona: str
    username: str  # Reddit username
    subreddit: str
    title: str
    content: str
    content_type: ContentType = ContentType.POST
    parent_post_id: Optional[str] = None  # For replies
    parent_comment_id: Optional[str] = None  # For nested replies
    thread_id: Optional[str] = None  # Links posts and replies in same thread
    keyword_ids: List[str] = Field(default_factory=list)  # e.g., ["K1", "K14", "K4"]


class CalendarEntry(BaseModel):
    """A single entry in the content calendar."""
    post_id: Optional[str] = None  # e.g., P1, P2, P3
    comment_id: Optional[str] = None  # e.g., C1, C2, C3
    date: datetime
    time: str
    type: ContentType
    persona: str
    username: str  # Reddit username
    subreddit: str
    title: str
    content: str
    parent_post_id: Optional[str] = None
    parent_comment_id: Optional[str] = None
    thread_id: Optional[str] = None
    keyword_ids: List[str] = Field(default_factory=list)


class ContentCalendar(BaseModel):
    """A weekly content calendar."""
    week_start: datetime
    week_end: datetime
    entries: List[CalendarEntry]
    metadata: Dict = Field(default_factory=dict)


class CalendarRequest(BaseModel):
    """Input request for generating a calendar."""
    company_info: CompanyInfo
    personas: List[Persona]
    subreddits: List[str]
    keywords: List[Keyword]  # Keywords instead of chatgpt_queries
    posts_per_week: int
    week_start: Optional[datetime] = None  # If None, starts from current week


class CalendarResponse(BaseModel):
    """Response containing generated calendar."""
    calendar: ContentCalendar
    quality_score: float
    warnings: List[str] = Field(default_factory=list)

