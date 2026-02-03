from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
import re
import aiohttp

from .models import RiverResponse, Post
from .services.reddit_service import RedditService
from .services.sentiment_service import SentimentService
from .services.relevance_service import RelevanceService
from .services.river_service import RiverService
from .services.subreddit_search_service import SubredditSearchService
from .cache import Cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _try_fallback_search(query: str, limit: int) -> List[Post]:
    """
    Try to find posts from related subreddits when exact match fails
    
    Args:
        query: Original search query
        limit: Maximum number of posts to return
        
    Returns:
        List of posts from fallback search or empty list
    """
    try:
        # Search for relevant subreddits
        suggestions = await subreddit_search_service.search_subreddits(query, 3)
        
        if not suggestions:
            logger.info(f"No subreddit suggestions found for query: {query}")
            return []
        
        all_posts = []
        
        # Try to fetch posts from each suggested subreddit
        for suggestion in suggestions:
            try:
                logger.info(f"Trying fallback subreddit: r/{suggestion.name}")
                posts = await reddit_service.fetch_posts(suggestion.name)
                
                if posts:
                    # Process posts for this subreddit
                    for post in posts:
                        sentiment = sentiment_service.analyze_sentiment(post.text)
                        tech_tags = relevance_service.extract_tech_tags(post.text)
                        importance = river_service.calculate_importance(post, sentiment, tech_tags)
                        
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
                        all_posts.append(processed_post)
                    
                    logger.info(f"Found {len(posts)} posts from r/{suggestion.name}")
                    
                    # If we have enough posts, stop searching
                    if len(all_posts) >= limit:
                        break
                        
            except Exception as e:
                logger.warning(f"Error fetching from fallback subreddit r/{suggestion.name}: {str(e)}")
                continue
        
        if all_posts:
            # Sort by importance and return top posts
            all_posts.sort(key=lambda x: x.importance_score, reverse=True)
            logger.info(f"Fallback search found {len(all_posts)} total posts")
            return all_posts
        else:
            logger.info(f"No posts found from any fallback subreddits for query: {query}")
            return []
            
    except Exception as e:
        logger.error(f"Error in fallback search for {query}: {str(e)}")
        return []

async def _is_subreddit_not_found(subreddit_name: str) -> bool:
    """Check if a subreddit exists by making a lightweight request"""
    try:
        url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
        headers = {"User-Agent": "TechRelevanceAnalyzer/1.0 (Educational Purpose)"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 404:
                    return True  # Subreddit not found
                elif response.status == 200:
                    data = await response.json()
                    # Check if subreddit is private/banned
                    if data.get('data', {}).get('over18') is None and not data.get('data'):
                        return True
                    return False  # Subreddit exists
                else:
                    # For other errors, assume it might exist
                    return False
    except Exception as e:
        logger.warning(f"Error checking subreddit existence for {subreddit_name}: {str(e)}")
        return False  # Assume it exists on error

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
subreddit_search_service = SubredditSearchService()

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
            # Check if this is a subreddit not found error vs empty subreddit
            if await _is_subreddit_not_found(validated_name):
                logger.info(f"Subreddit r/{validated_name} not found, trying fallback search")
                
                # Try fallback search
                fallback_posts = await _try_fallback_search(validated_name, limit)
                if fallback_posts:
                    return RiverResponse(
                        posts=fallback_posts[:limit], 
                        source=source, 
                        name=validated_name,
                        search_method="fallback"
                    )
                else:
                    # If no fallback results, provide suggestions
                    suggestions = await subreddit_search_service.search_subreddits(validated_name, 5)
                    suggestion_names = [s.name for s in suggestions]
                    
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Subreddit '{validated_name}' not found. Try one of these related subreddits: {', '.join(suggestion_names)}",
                        headers={"X-Error-Type": "subreddit_not_found_with_suggestions"}
                    )
            else:
                logger.info(f"No posts found in subreddit r/{validated_name}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"No posts found for subreddit '{validated_name}'. The subreddit may exist but have no recent posts.",
                    headers={"X-Error-Type": "no_posts_found"}
                )
        
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
