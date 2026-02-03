from typing import List, Dict, Optional
import aiohttp
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SubredditSuggestion:
    name: str
    subscribers: int
    description: str
    relevance_score: float

class SubredditSearchService:
    """Service for finding relevant subreddits when exact match fails"""
    
    def __init__(self):
        self.user_agent = "TechRelevanceAnalyzer/1.0 (Educational Purpose)"
        
        # Common tech term mappings for quick suggestions
        self.tech_mappings = {
            'ai': ['artificial', 'MachineLearning', 'singularity', 'artificialinteligence', 'deeplearning'],
            'python': ['Python', 'learnpython', 'pythontips', 'Pythonprojects', 'pythongamedev'],
            'javascript': ['javascript', 'learnjavascript', 'node', 'reactjs', 'vuejs', 'angular'],
            'webdev': ['webdev', 'web_design', 'webdevelopment', 'fullstack', 'frontend', 'backend'],
            'machine learning': ['MachineLearning', 'learnmachinelearning', 'deeplearning', 'computervision'],
            'data science': ['datascience', 'learn_datascience', 'datasets', 'dataisbeautiful'],
            'cybersecurity': ['cybersecurity', 'netsec', 'hacking', 'privacy', 'crypto'],
            'blockchain': ['CryptoCurrency', 'Bitcoin', 'ethereum', 'blockchain', 'CryptoTechnology'],
            'cloud': ['aws', 'azure', 'googlecloud', 'devops', 'sysadmin'],
            'mobile': ['androiddev', 'iosdev', 'reactnative', 'flutterdev', 'mobiledev'],
            'game dev': ['gamedev', 'Unity3D', 'unrealengine', 'indiegaming', 'gamedevelopment'],
            'database': ['database', 'sql', 'nosql', 'mongodb', 'postgresql'],
            'devops': ['devops', 'aws', 'azure', 'docker', 'kubernetes'],
            'ui ux': ['ui_design', 'UXDesign', 'web_design', 'graphic_design', 'Figma'],
        }
    
    async def search_subreddits(self, query: str, limit: int = 5) -> List[SubredditSuggestion]:
        """
        Search for relevant subreddits based on query
        
        Args:
            query: Search term
            limit: Maximum number of suggestions to return
            
        Returns:
            List of subreddit suggestions with relevance scores
        """
        suggestions = []
        
        # 1. Try exact mappings first
        mapping_suggestions = self._get_mapping_suggestions(query)
        suggestions.extend(mapping_suggestions)
        
        # 2. Try Reddit's search API if no good mappings found
        if len(suggestions) < limit:
            api_suggestions = await self._search_reddit_api(query, limit - len(suggestions))
            suggestions.extend(api_suggestions)
        
        # 3. Sort by relevance and return top results
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        return suggestions[:limit]
    
    def _get_mapping_suggestions(self, query: str) -> List[SubredditSuggestion]:
        """Get suggestions from predefined tech mappings"""
        suggestions = []
        query_lower = query.lower()
        
        # Direct mapping
        if query_lower in self.tech_mappings:
            for sub_name in self.tech_mappings[query_lower]:
                suggestion = SubredditSuggestion(
                    name=sub_name,
                    subscribers=0,  # Will be fetched later if needed
                    description=f"Related to {query}",
                    relevance_score=0.9  # High relevance for direct mapping
                )
                suggestions.append(suggestion)
        
        # Partial matching
        for term, subreddits in self.tech_mappings.items():
            if query_lower in term or term in query_lower:
                for sub_name in subreddits:
                    suggestion = SubredditSuggestion(
                        name=sub_name,
                        subscribers=0,
                        description=f"Related to {term}",
                        relevance_score=0.7  # Medium relevance for partial match
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    async def _search_reddit_api(self, query: str, limit: int) -> List[SubredditSuggestion]:
        """Search Reddit's API for subreddits"""
        suggestions = []
        
        try:
            # Search for subreddits containing the query
            url = f"https://www.reddit.com/subreddits/search.json"
            params = {
                'q': query,
                'limit': limit * 2,  # Get more results to filter
                'type': 'sr'
            }
            headers = {'User-Agent': self.user_agent}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        children = data.get('data', {}).get('children', [])
                        
                        for child in children:
                            sub_data = child.get('data', {})
                            name = sub_data.get('display_name', '')
                            
                            if name and self._is_tech_related(name, sub_data.get('public_description', '')):
                                suggestion = SubredditSuggestion(
                                    name=name,
                                    subscribers=sub_data.get('subscribers', 0),
                                    description=sub_data.get('public_description', ''),
                                    relevance_score=self._calculate_relevance(query, name, sub_data.get('public_description', ''))
                                )
                                suggestions.append(suggestion)
                    
        except Exception as e:
            logger.error(f"Error searching Reddit API: {str(e)}")
        
        return suggestions
    
    def _is_tech_related(self, name: str, description: str) -> bool:
        """Check if a subreddit is technology-related"""
        tech_keywords = [
            'programming', 'coding', 'developer', 'software', 'tech', 'technology',
            'computer', 'data', 'ai', 'machine learning', 'web', 'mobile', 'app',
            'python', 'javascript', 'java', 'react', 'node', 'database', 'cloud',
            'devops', 'cybersecurity', 'blockchain', 'crypto', 'gamedev', 'ui',
            'ux', 'design', 'algorithm', 'api', 'framework', 'library'
        ]
        
        text_to_check = (name + ' ' + description).lower()
        
        # Check if any tech keywords are present
        for keyword in tech_keywords:
            if keyword in text_to_check:
                return True
        
        return False
    
    def _calculate_relevance(self, query: str, name: str, description: str) -> float:
        """Calculate relevance score for a subreddit suggestion"""
        query_lower = query.lower()
        name_lower = name.lower()
        desc_lower = description.lower()
        
        score = 0.0
        
        # Exact name match
        if query_lower == name_lower:
            score += 1.0
        
        # Query in name
        elif query_lower in name_lower:
            score += 0.8
        
        # Name in query
        elif name_lower in query_lower:
            score += 0.6
        
        # Query in description
        if query_lower in desc_lower:
            score += 0.4
        
        # Partial word matches
        query_words = query_lower.split()
        for word in query_words:
            if word in name_lower:
                score += 0.2
            if word in desc_lower:
                score += 0.1
        
        # Bonus for subscriber count (logarithmic scaling)
        # This would require fetching actual subscriber data
        
        return min(score, 1.0)
    
    async def get_subreddit_info(self, subreddit_name: str) -> Optional[Dict]:
        """Get detailed information about a specific subreddit"""
        try:
            url = f"https://www.reddit.com/r/{subreddit_name}/about.json"
            headers = {'User-Agent': self.user_agent}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {})
        except Exception as e:
            logger.error(f"Error fetching subreddit info for {subreddit_name}: {str(e)}")
        
        return None
