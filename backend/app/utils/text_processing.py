import re
import hashlib
from typing import List

class TextProcessor:
    """Utility class for text processing and normalization"""
    
    def __init__(self):
        # Patterns to clean up text
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.excessive_whitespace = re.compile(r'\s+')
        self.hashtag_pattern = re.compile(r'#(\w+)')
        self.mention_pattern = re.compile(r'@(\w+)')
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by:
        - Converting to lowercase
        - Removing URLs (but keeping hashtags and mentions)
        - Normalizing whitespace
        - Stripping excessive punctuation
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs but keep hashtags and mentions
        text = self.url_pattern.sub(' ', text)
        
        # Normalize whitespace
        text = self.excessive_whitespace.sub(' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def combine_title_body(self, title: str, body: str) -> str:
        """
        Combine title and body text for analysis
        """
        if not title:
            title = ""
        if not body:
            body = ""
        
        # Normalize both parts
        title = self.normalize_text(title)
        body = self.normalize_text(body)
        
        # Combine with separator
        if title and body:
            combined = f"{title}. {body}"
        elif title:
            combined = title
        else:
            combined = body
        
        return combined
    
    def extract_hashtags(self, text: str) -> list[str]:
        """Extract hashtags from text"""
        return self.hashtag_pattern.findall(text.lower())
    
    def extract_mentions(self, text: str) -> list[str]:
        """Extract mentions from text"""
        return self.mention_pattern.findall(text.lower())
    
    def create_content_hash(self, text: str) -> str:
        """Create hash for content deduplication"""
        normalized_text = self.normalize_text(text)
        return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
    
    def truncate_text(self, text: str, max_length: int = 500) -> str:
        """Truncate text to maximum length while preserving word boundaries"""
        if len(text) <= max_length:
            return text
        
        # Find the last space before max_length
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we have a good breaking point
            truncated = truncated[:last_space]
        
        return truncated + "..."
