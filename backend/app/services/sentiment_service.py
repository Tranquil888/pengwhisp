from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict
import logging

from ..models import SentimentResult
from ..utils.config import SENTIMENT_THRESHOLDS

logger = logging.getLogger(__name__)

class SentimentService:
    """Service for sentiment analysis using VADER"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.positive_min = SENTIMENT_THRESHOLDS['positive_min']
        self.negative_max = SENTIMENT_THRESHOLDS['negative_max']
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text using VADER
        
        Args:
            text: Input text to analyze
            
        Returns:
            SentimentResult with label and compound score
        """
        if not text or not text.strip():
            return SentimentResult(label="neutral", score=0.0)
        
        try:
            # Get VADER sentiment scores
            scores = self.analyzer.polarity_scores(text)
            compound_score = scores['compound']
            
            # Determine sentiment label based on compound score
            if compound_score >= self.positive_min:
                label = "positive"
            elif compound_score <= self.negative_max:
                label = "negative"
            else:
                label = "neutral"
            
            return SentimentResult(label=label, score=compound_score)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            # Return neutral sentiment on error
            return SentimentResult(label="neutral", score=0.0)
    
    def get_detailed_scores(self, text: str) -> Dict[str, float]:
        """
        Get detailed VADER sentiment scores
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with all VADER scores
        """
        if not text or not text.strip():
            return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
        
        try:
            return self.analyzer.polarity_scores(text)
        except Exception as e:
            logger.error(f"Error getting detailed sentiment scores: {str(e)}")
            return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
    
    def is_positive(self, text: str, threshold: float = None) -> bool:
        """
        Check if text has positive sentiment
        
        Args:
            text: Input text to analyze
            threshold: Custom threshold (defaults to config value)
            
        Returns:
            True if sentiment is positive
        """
        if threshold is None:
            threshold = self.positive_min
        
        result = self.analyze_sentiment(text)
        return result.label == "positive" and result.score >= threshold
    
    def is_negative(self, text: str, threshold: float = None) -> bool:
        """
        Check if text has negative sentiment
        
        Args:
            text: Input text to analyze
            threshold: Custom threshold (defaults to config value)
            
        Returns:
            True if sentiment is negative
        """
        if threshold is None:
            threshold = self.negative_max
        
        result = self.analyze_sentiment(text)
        return result.label == "negative" and result.score <= threshold
    
    def get_sentiment_distribution(self, texts: list[str]) -> Dict[str, int]:
        """
        Get sentiment distribution for a list of texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Dictionary with counts for each sentiment
        """
        distribution = {"positive": 0, "neutral": 0, "negative": 0}
        
        for text in texts:
            result = self.analyze_sentiment(text)
            distribution[result.label] += 1
        
        return distribution
