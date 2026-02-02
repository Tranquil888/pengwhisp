from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SentimentResult(BaseModel):
    """Sentiment analysis result"""
    label: str  # "positive", "neutral", "negative"
    score: float  # -1 to 1

class RedditPost(BaseModel):
    """Raw Reddit post data"""
    id: str
    title: str
    text: str  # Combined title + body
    url: str
    created_at: datetime
    score: int
    comments: int
    author: str
    subreddit: str

class Post(BaseModel):
    """Processed post with analysis results"""
    id: str
    text: str
    url: str
    importance_score: float
    sentiment_label: str
    sentiment_score: float
    tech_tags: List[str]
    created_at: datetime
    score: int
    comments: int

class RiverResponse(BaseModel):
    """API response for river feed"""
    posts: List[Post]
    source: str
    name: str
    total_count: Optional[int] = None

class RedditRawPost(BaseModel):
    """Raw Reddit API response structure"""
    kind: str
    data: dict
