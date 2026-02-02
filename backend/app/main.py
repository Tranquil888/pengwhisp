from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
import re

from .models import RiverResponse, Post
from .services.reddit_service import RedditService
from .services.sentiment_service import SentimentService
from .services.relevance_service import RelevanceService
from .services.river_service import RiverService
from .cache import Cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_subreddit(name: str) -> str:
    """Validate and sanitize subreddit name"""
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="Subreddit name cannot be empty")
    
    # Remove whitespace and convert to lowercase
    sanitized = name.strip().lower()
    
    # Validate format (alphanumeric, underscores, hyphens only, max 21 chars)
    if not re.match(r'^[a-z0-9_-]{1,21}$', sanitized):
        raise HTTPException(
            status_code=400, 
            detail="Invalid subreddit name. Must be 1-21 characters, alphanumeric, underscores, or hyphens only"
        )
    
    # Block reserved/invalid names
    reserved_names = {'www', 'api', 'blog', 'help', 'info', 'mod', 'moderators', 'i', 'me', 'r'}
    if sanitized in reserved_names:
        raise HTTPException(status_code=400, detail=f"'{sanitized}' is a reserved subreddit name")
    
    return sanitized

# Initialize FastAPI app
app = FastAPI(
    title="Tech Relevance & Sentiment Analyzer",
    description="Analyzes technology relevance and sentiment from Reddit sources",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cache = Cache()
reddit_service = RedditService()
sentiment_service = SentimentService()
relevance_service = RelevanceService()
river_service = RiverService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tech Relevance & Sentiment Analyzer API"}

@app.get("/api/river", response_model=RiverResponse)
async def get_river(
    source: str = "reddit",
    name: str = "technology",
    limit: int = 50
):
    """
    Get river feed from specified source and subreddit/community.
    
    Args:
        source: Data source (currently only "reddit" supported)
        name: Subreddit or community name
        limit: Maximum number of posts to return
    
    Returns:
        RiverResponse with filtered and scored posts
    """
    if source.lower() != "reddit":
        raise HTTPException(status_code=400, detail="Currently only 'reddit' source is supported")
    
    # Validate and sanitize subreddit name
    validated_name = validate_subreddit(name)
    
    # Validate limit
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    try:
        # Check cache first
        cache_key = f"{source}:{validated_name}"
        cached_posts = cache.get(cache_key)
        
        if cached_posts:
            logger.info(f"Returning cached posts for {cache_key}")
            return RiverResponse(posts=cached_posts[:limit], source=source, name=validated_name)
        
        # Fetch fresh data
        logger.info(f"Fetching posts from r/{validated_name}")
        reddit_posts = await reddit_service.fetch_posts(validated_name)
        
        if not reddit_posts:
            raise HTTPException(status_code=404, detail=f"No posts found for subreddit '{validated_name}'")
        
        # Process posts
        processed_posts = []
        for post in reddit_posts:
            # Analyze sentiment
            sentiment = sentiment_service.analyze_sentiment(post.text)
            
            # Detect tech relevance
            tech_tags = relevance_service.extract_tech_tags(post.text)
            
            # Calculate importance score
            importance = river_service.calculate_importance(
                post, sentiment, tech_tags
            )
            
            # Create processed post
            processed_post = Post(
                id=post.id,
                text=post.text,
                url=post.url,
                importance_score=importance,
                sentiment_label=sentiment.label,
                sentiment_score=sentiment.score,
                tech_tags=tech_tags,
                created_at=post.created_at,
                score=post.score,
                comments=post.comments
            )
            
            processed_posts.append(processed_post)
        
        # Filter by importance threshold and sort
        filtered_posts = river_service.filter_and_sort(processed_posts)
        
        # Cache the results
        cache.set(cache_key, filtered_posts)
        
        return RiverResponse(
            posts=filtered_posts[:limit],
            source=source,
            name=validated_name
        )
        
    except Exception as e:
        logger.error(f"Error processing river request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
