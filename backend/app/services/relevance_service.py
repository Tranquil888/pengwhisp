import re
from typing import List, Set
import logging

from ..utils.config import TECH_KEYWORDS

logger = logging.getLogger(__name__)

class RelevanceService:
    """Service for detecting technology relevance in text"""
    
    def __init__(self):
        # Compile regex patterns for better performance
        self.keyword_patterns = {}
        for category, keywords in TECH_KEYWORDS.items():
            # Create regex pattern for each category
            pattern = r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b'
            self.keyword_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def extract_tech_tags(self, text: str) -> List[str]:
        """
        Extract technology keywords from text and return as tags
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected technology tags
        """
        if not text:
            return []
        
        detected_tags = set()
        text_lower = text.lower()
        
        # Check each category for keyword matches
        for category, pattern in self.keyword_patterns.items():
            matches = pattern.findall(text_lower)
            for match in matches:
                # Normalize the match and add as tag
                tag = match.lower().strip()
                if tag and len(tag) > 1:  # Filter out single characters
                    detected_tags.add(tag)
        
        # Convert to sorted list for consistency
        return sorted(list(detected_tags))
    
    def calculate_tech_relevance_score(self, text: str) -> float:
        """
        Calculate a relevance score based on detected tech keywords
        
        Args:
            text: Input text to analyze
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        tags = self.extract_tech_tags(text)
        
        if not tags:
            return 0.0
        
        # Base score from number of unique tags
        base_score = min(len(tags) / 10.0, 1.0)  # Cap at 10 unique tags
        
        # Bonus for high-value categories (AI/ML, frameworks)
        high_value_categories = ['ai_ml', 'frameworks', 'languages']
        bonus = 0.0
        
        for category, pattern in self.keyword_patterns.items():
            if category in high_value_categories:
                matches = pattern.findall(text.lower())
                if matches:
                    bonus += 0.1 * min(len(set(matches)), 3)  # Cap bonus per category
        
        # Cap total score at 1.0
        return min(base_score + bonus, 1.0)
    
    def get_category_distribution(self, text: str) -> dict:
        """
        Get distribution of detected keywords by category
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with category counts
        """
        distribution = {}
        text_lower = text.lower()
        
        for category, pattern in self.keyword_patterns.items():
            matches = pattern.findall(text_lower)
            unique_matches = set(matches)
            if unique_matches:
                distribution[category] = list(unique_matches)
        
        return distribution
    
    def is_tech_focused(self, text: str, threshold: float = 0.3) -> bool:
        """
        Determine if text is technology-focused
        
        Args:
            text: Input text to analyze
            threshold: Minimum relevance score threshold
            
        Returns:
            True if text is tech-focused
        """
        return self.calculate_tech_relevance_score(text) >= threshold
