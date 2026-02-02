# Tech Relevance & Sentiment Analyzer - Backend

FastAPI backend for analyzing technology relevance and sentiment from Reddit sources.

## Features

- Reddit post fetching with rate limiting
- Sentiment analysis using VADER
- Technology keyword detection and relevance scoring
- Importance-based filtering for river feed
- Simple in-memory caching
- RESTful API with CORS support

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
cd backend
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET `/`
Health check endpoint

### GET `/api/river`
Get river feed from Reddit

**Query Parameters:**
- `source` (string): Data source (currently only "reddit")
- `name` (string): Subreddit name (default: "technology")
- `limit` (integer): Maximum number of posts to return (default: 50)

**Example:**
```
GET /api/river?source=reddit&name=programming&limit=25
```

**Response:**
```json
{
  "posts": [
    {
      "id": "abc123",
      "text": "Post content...",
      "url": "https://reddit.com/r/programming/comments/abc123",
      "importance_score": 0.85,
      "sentiment_label": "positive",
      "sentiment_score": 0.42,
      "tech_tags": ["python", "machine learning", "tensorflow"],
      "created_at": "2024-01-15T10:30:00",
      "score": 1250,
      "comments": 45
    }
  ],
  "source": "reddit",
  "name": "programming"
}
```

## Architecture

### Services

- **RedditService**: Fetches posts from Reddit API with rate limiting
- **SentimentService**: Performs sentiment analysis using VADER
- **RelevanceService**: Detects technology keywords and relevance
- **RiverService**: Calculates importance scores and filters posts

### Models

- **RedditPost**: Raw Reddit post data
- **Post**: Processed post with analysis results
- **SentimentResult**: Sentiment analysis output
- **RiverResponse**: API response format

### Configuration

Key settings in `app/utils/config.py`:
- Technology keywords by category
- API rate limiting
- Importance scoring weights
- Cache TTL

## Development

The code follows these principles:
- Type hints throughout
- Small, focused functions
- Comprehensive error handling
- Modular, extensible structure
- Clear logging

## Future Enhancements

- Support for X (Twitter) integration
- Embedding-based tech relevance detection
- Redis caching for production
- User authentication and preferences
- Advanced filtering and clustering
