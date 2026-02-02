import aiohttp
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import hashlib

from ..models import RedditPost
from ..utils.text_processing import TextProcessor

logger = logging.getLogger(__name__)

class RedditService:
    """Service for fetching and processing Reddit posts"""
    
    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.user_agent = "TechRelevanceAnalyzer/1.0 (Educational Purpose)"
        self.rate_limit_delay = 2.0  # seconds between requests
        self.last_request_time = None
        self.text_processor = TextProcessor()
    
    async def _make_request(self, url: str) -> Optional[dict]:
        """Make HTTP request with rate limiting and error handling"""
        # Rate limiting
        if self.last_request_time:
            elapsed = datetime.now().timestamp() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        
        headers = {
            "User-Agent": self.user_agent
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    self.last_request_time = datetime.now().timestamp()
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Subreddit not found: {url}")
                        return None
                    elif response.status == 429:
                        logger.warning("Rate limited, waiting...")
                        await asyncio.sleep(5)
                        return await self._make_request(url)
                    else:
                        logger.error(f"HTTP {response.status}: {url}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _parse_reddit_post(self, post_data: dict, subreddit: str) -> Optional[RedditPost]:
        """Parse raw Reddit post data into RedditPost model"""
        try:
            # Extract post data
            data = post_data.get("data", {}) if isinstance(post_data, dict) and "data" in post_data else post_data
            
            # Skip if post is deleted or removed
            if data.get("removed_by_category") or data.get("selftext") == "[removed]":
                logger.info("Skipping removed/deleted post")
                return None
            
            # Get basic fields
            post_id = data.get("id", "")
            title = data.get("title", "")
            body = data.get("selftext", "")
            
            # Skip posts with no ID or title
            if not post_id or not title:
                logger.warning(f"Skipping post with no ID or title: ID='{post_id}', Title='{title[:30]}'")
                return None
            
            # Create combined text for analysis
            combined_text = self.text_processor.combine_title_body(title, body)
            
            # Create RedditPost object
            reddit_post = RedditPost(
                id=post_id,
                title=title,
                text=combined_text,
                url=f"https://reddit.com{data.get('permalink', '')}",
                created_at=datetime.fromtimestamp(data.get("created_utc", 0)),
                score=data.get("score", 0),
                comments=data.get("num_comments", 0),
                author=data.get("author", ""),
                subreddit=subreddit
            )
            
            logger.info(f"Successfully parsed post: {post_id} - {title[:50]}")
            return reddit_post
            
        except Exception as e:
            logger.error(f"Error parsing Reddit post: {str(e)}")
            return None
    
    async def fetch_posts(self, subreddit: str, limit: int = 100) -> List[RedditPost]:
        """
        Fetch latest posts from a subreddit
        
        Args:
            subreddit: Name of the subreddit
            limit: Maximum number of posts to fetch
            
        Returns:
            List of RedditPost objects
        """
        url = f"{self.base_url}/r/{subreddit}/new.json?limit={limit}"
        
        logger.info(f"Fetching posts from r/{subreddit}")
        response_data = await self._make_request(url)
        
        if not response_data:
            return []
        
        posts = []
        seen_hashes = set()  # For deduplication
        
        try:
            # Extract posts from response
            children = response_data.get("data", {}).get("children", [])
            logger.info(f"Number of children found: {len(children)}")
            
            for i, child in enumerate(children):
                # Skip invalid children
                if not isinstance(child, dict):
                    continue
                
                if "data" not in child:
                    continue
                
                post_data = child["data"]
                
                # Skip empty post data
                if not post_data or not isinstance(post_data, dict):
                    continue
                
                # Skip posts with no ID or title
                if not post_data.get("id") or not post_data.get("title"):
                    continue
                
                reddit_post = self._parse_reddit_post(post_data, subreddit)
                
                if reddit_post:
                    # Deduplicate by content hash
                    content_hash = hashlib.md5(
                        reddit_post.text.encode('utf-8')
                    ).hexdigest()
                    
                    if content_hash not in seen_hashes:
                        seen_hashes.add(content_hash)
                        posts.append(reddit_post)
            
            logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
            return posts
            
        except Exception as e:
            logger.error(f"Error processing Reddit response: {str(e)}")
            return []
