"""
Configuration and constants for the Tech Relevance & Sentiment Analyzer
"""

# Technology keywords organized by category
TECH_KEYWORDS = {
    'ai_ml': [
        'artificial intelligence', 'machine learning', 'deep learning', 'neural network',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv', 'nlp', 'computer vision',
        'transformer', 'bert', 'gpt', 'llm', 'chatgpt', 'openai', 'anthropic', 'claude',
        'reinforcement learning', 'supervised learning', 'unsupervised learning',
        'regression', 'classification', 'clustering', 'pandas', 'numpy', 'jupyter'
    ],
    'frameworks': [
        'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt', 'django', 'flask', 'fastapi',
        'express', 'spring', 'laravel', 'rails', 'asp.net', 'blazor', 'flutter', 'swiftui',
        'jetpack compose', 'tailwind', 'bootstrap', 'material ui', 'ant design'
    ],
    'languages': [
        'python', 'javascript', 'typescript', 'rust', 'go', 'java', 'c++', 'c#', 'php',
        'ruby', 'swift', 'kotlin', 'scala', 'haskell', 'elixir', 'dart', 'r', 'matlab',
        'sql', 'html', 'css', 'sass', 'less', 'webpack', 'vite', 'babel'
    ],
    'tools': [
        'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'gitlab', 'github',
        'bitbucket', 'aws', 'azure', 'gcp', 'google cloud', 'vercel', 'netlify', 'heroku',
        'digitalocean', 'linode', 'nginx', 'apache', 'redis', 'postgresql', 'mysql',
        'mongodb', 'elasticsearch', 'kafka', 'rabbitmq', 'graphql', 'rest api'
    ],
    'concepts': [
        'microservices', 'serverless', 'devops', 'ci/cd', 'cicd', 'agile', 'scrum',
        'tdd', 'bdd', 'unit testing', 'integration testing', 'e2e testing', 'code review',
        'refactoring', 'technical debt', 'scalability', 'performance', 'optimization',
        'security', 'authentication', 'authorization', 'oauth', 'jwt', 'encryption',
        'blockchain', 'web3', 'cryptocurrency', 'smart contracts', 'defi'
    ],
    'platforms': [
        'aws', 'azure', 'google cloud', 'gcp', 'firebase', 'supabase', 'airtable',
        'notion', 'slack', 'discord', 'telegram', 'api', 'webhook', 'saas', 'paas', 'iaas'
    ]
}

# API Configuration
API_CONFIG = {
    'rate_limit_delay': 2.0,  # seconds between Reddit requests
    'cache_ttl': 300,  # seconds (5 minutes)
    'max_posts_per_request': 100,
    'importance_threshold': 0.15,  # minimum importance score for river feed (filters low-quality posts)
    'default_subreddit': 'technology'
}

# Importance scoring weights
IMPORTANCE_WEIGHTS = {
    'engagement_weight': 0.15,  # score + comments (reduced)
    'recency_weight': 0.45,     # newer posts get higher weight (increased)
    'tech_relevance_weight': 0.3,  # tech keyword presence (increased)
    'sentiment_weight': 0.1    # sentiment bonus (unchanged)
}

# Sentiment thresholds
SENTIMENT_THRESHOLDS = {
    'positive_min': 0.1,
    'negative_max': -0.1
}

# User agent for Reddit API
USER_AGENT = "TechRelevanceAnalyzer/1.0 (Educational Purpose; +https://github.com/example/tech-relevance-analyzer)"
