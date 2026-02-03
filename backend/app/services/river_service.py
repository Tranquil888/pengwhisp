from typing import List
from datetime import datetime, timedelta
import math
import logging

from ..models import Post, RedditPost, SentimentResult
from ..utils.config import IMPORTANCE_WEIGHTS, API_CONFIG
from .relevance_service import RelevanceService

logger = logging.getLogger(__name__)

class RiverService:
    """Service for calculating importance scores and filtering river feed"""
    
    def __init__(self):
        self.weights = IMPORTANCE_WEIGHTS
        self.importance_threshold = API_CONFIG['importance_threshold']
        self.relevance_service = RelevanceService()
    
    def calculate_importance(
        self, 
        post: RedditPost, 
        sentiment: SentimentResult, 
        tech_tags: List[str]
    ) -> float:
        """
        Calculate importance score for a post
        
        Args:
            post: RedditPost object
            sentiment: SentimentResult object
            tech_tags: List of detected tech tags
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        try:
            # 1. Engagement score (score + comments)
            engagement_score = self._calculate_engagement_score(post.score, post.comments)
            
            # 2. Recency score (newer posts get higher weight)
            recency_score = self._calculate_recency_score(post.created_at)
            
            # 3. Tech relevance score (presence of tech keywords)
            tech_relevance_score = self._calculate_tech_relevance_score(tech_tags)
            
            # 4. Sentiment score (positive sentiment gets bonus)
            sentiment_score = self._calculate_sentiment_score(sentiment)
            
            # Combine scores using weights
            importance = (
                engagement_score * self.weights['engagement_weight'] +
                recency_score * self.weights['recency_weight'] +
                tech_relevance_score * self.weights['tech_relevance_weight'] +
                sentiment_score * self.weights['sentiment_weight']
            )
            
            # Normalize to 0-1 range
            return min(max(importance, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating importance score: {str(e)}")
            return 0.0
    
    def _calculate_engagement_score(self, score: int, comments: int) -> float:
        """
        Calculate engagement score from Reddit score and comments
        Uses logarithmic scaling to prevent very high scores from dominating
        Comments weighted more heavily to indicate discussion quality
        """
        # Combine score and comments (comments weighted more heavily - increased from 2x to 3x)
        combined_engagement = score + (comments * 3)
        
        if combined_engagement <= 0:
            # Give small base score for new posts with 0 engagement
            return 0.1
        
        # Logarithmic scaling with base 10, but with a minimum score
        log_score = math.log10(max(combined_engagement, 1))
        
        # Normalize to 0-1 range with better scaling for low engagement
        if combined_engagement <= 5:
            # Give reasonable scores for very low engagement (1-5)
            normalized_score = 0.1 + (combined_engagement / 5.0) * 0.3
        elif combined_engagement <= 50:
            # Medium engagement
            normalized_score = 0.4 + ((combined_engagement - 5) / 45.0) * 0.4
        elif combined_engagement <= 200:
            # High engagement - improved scaling
            normalized_score = 0.8 + ((combined_engagement - 50) / 150.0) * 0.15
        else:
            # Very high engagement - use log scaling with better discrimination
            normalized_score = min(0.95 + (log_score / 8.0) * 0.05, 1.0)
        
        # Quality bonus for discussion-heavy posts (high comment-to-upvote ratio)
        if score > 0:
            comment_ratio = comments / score
            if comment_ratio > 2.0:  # More than 2 comments per upvote
                normalized_score = min(normalized_score + 0.05, 1.0)
        
        return normalized_score
    
    def _calculate_recency_score(self, created_at: datetime) -> float:
        """
        Calculate recency score (newer posts get higher weight)
        Slower decay curve with extended high-score window
        """
        now = datetime.now()
        age_hours = (now - created_at).total_seconds() / 3600
        
        if age_hours <= 6:
            return 1.0  # Extended high-score window from 1 hour to 6 hours
        elif age_hours <= 24:
            # Slower linear decay over next 18 hours
            return 1.0 - (age_hours - 6) / 18.0 * 0.3
        elif age_hours <= 72:  # 3 days (extended from 1 week)
            # Even slower decay over the next 2 days
            return 0.7 - (age_hours - 24) / 48.0 * 0.3
        elif age_hours <= 168:  # 1 week
            # Minimal decay for the rest of the week
            return max(0.4 - (age_hours - 72) / 96.0 * 0.2, 0.2)
        else:
            # Minimal score for posts older than 1 week
            return max(0.2 - (age_hours - 168) / 720.0 * 0.1, 0.1)
    
    def _calculate_tech_relevance_score(self, tech_tags: List[str]) -> float:
        """
        Calculate tech relevance score from detected tags
        Smoother scaling with reduced maximum impact
        """
        if not tech_tags:
            return 0.05  # Give small base score instead of 0
        
        # Base score from number of unique tags with smoother scaling
        tag_count = len(tech_tags)
        
        if tag_count == 1:
            tag_score = 0.3  # Single tag gets moderate score
        elif tag_count == 2:
            tag_score = 0.5  # Two tags get good score
        elif tag_count == 3:
            tag_score = 0.7  # Three tags get high score
        elif tag_count <= 5:
            tag_score = 0.85  # 4-5 tags get very high score
        else:
            tag_score = 1.0  # More than 5 tags gets maximum score
        
        # Apply smoother scaling to reduce impact
        return max(tag_score * 0.8, 0.1)  # Scale down and ensure minimum
    
    def _calculate_sentiment_score(self, sentiment: SentimentResult) -> float:
        """
        Calculate sentiment score (positive sentiment gets bonus)
        """
        if sentiment.label == "positive":
            # Positive sentiment gets bonus up to 0.3
            return min(abs(sentiment.score) * 0.3, 0.3)
        elif sentiment.label == "negative":
            # Negative sentiment gets small penalty
            return max(-0.1, sentiment.score * 0.1)
        else:
            # Neutral sentiment gets no bonus or penalty
            return 0.0
    
    def filter_and_sort(self, posts: List[Post]) -> List[Post]:
        """
        Filter posts by importance threshold and sort by importance score
        
        Args:
            posts: List of Post objects with importance scores
            
        Returns:
            Filtered and sorted list of posts
        """
        # Filter by importance threshold
        filtered_posts = [
            post for post in posts 
            if post.importance_score >= self.importance_threshold
        ]
        
        # Sort by importance score (descending)
        filtered_posts.sort(key=lambda x: x.importance_score, reverse=True)
        
        logger.info(f"Filtered {len(posts)} posts to {len(filtered_posts)} important posts")
        
        return filtered_posts
    
    def get_top_posts(self, posts: List[Post], limit: int = 50) -> List[Post]:
        """
        Get top N posts by importance score
        
        Args:
            posts: List of Post objects
            limit: Maximum number of posts to return
            
        Returns:
            Top posts by importance
        """
        filtered_posts = self.filter_and_sort(posts)
        return filtered_posts[:limit]
    
    def get_importance_distribution(self, posts: List[Post]) -> dict:
        """
        Get distribution of importance scores
        
        Args:
            posts: List of Post objects
            
        Returns:
            Dictionary with importance score statistics
        """
        if not posts:
            return {
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'count': 0
            }
        
        scores = [post.importance_score for post in posts]
        scores.sort()
        
        return {
            'mean': sum(scores) / len(scores),
            'median': scores[len(scores) // 2],
            'min': min(scores),
            'max': max(scores),
            'count': len(scores)
        }
