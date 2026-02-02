# Tech Relevance & Sentiment Analyzer

A clean MVP web application that analyzes technology relevance and sentiment from Reddit sources, displaying the most important posts in a "river" feed.

## 🎯 Project Goal

Surface what technologies are currently relevant while filtering out low-signal noise from Reddit discussions.

## ✨ Features

- **Reddit Integration**: Fetches posts from any subreddit via public API
- **Sentiment Analysis**: Uses VADER to classify sentiment (positive/neutral/negative)
- **Tech Relevance Detection**: Identifies technology keywords and frameworks
- **Importance Scoring**: Ranks posts by engagement, recency, and tech relevance
- **River Feed**: Clean, vertical feed sorted by importance
- **No Authentication**: Simple, accessible interface
- **Responsive Design**: Works on desktop and mobile

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **Reddit Service**: Fetches posts with rate limiting
- **Sentiment Service**: VADER sentiment analysis
- **Relevance Service**: Tech keyword detection
- **River Service**: Importance scoring and filtering
- **Simple Caching**: In-memory cache with TTL

### Frontend (React)
- **SearchInput**: Subreddit selection with suggestions
- **RiverFeed**: Main feed display with loading states
- **PostCard**: Individual post with sentiment and tech tags
- **API Client**: Axios-based communication with backend

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will be available at `http://localhost:3000`

## 📊 How It Works

### 1. Data Ingestion
- Fetches latest posts from Reddit via `https://www.reddit.com/r/{subreddit}/new.json`
- Respects rate limits with custom User-Agent
- Handles errors and retries automatically

### 2. Text Processing
- Combines title and body text
- Normalizes text (lowercase, removes URLs, keeps hashtags/mentions)
- Deduplicates posts using content hashing

### 3. Analysis
- **Sentiment**: VADER sentiment analysis (-1 to +1 scale)
- **Tech Relevance**: Keyword matching across 6 categories
- **Importance**: Weighted scoring of engagement + recency + tech relevance

### 4. River Logic
- Filters posts below importance threshold
- Sorts by importance score (descending)
- Displays top posts in clean feed format

## 🎨 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **VADER**: Sentiment analysis library
- **aiohttp**: Async HTTP client for Reddit API
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern UI framework
- **Axios**: HTTP client for API calls
- **CSS3**: Modern styling with gradients and animations

## 📁 Project Structure

```
tech-relevance-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── services/            # Business logic
│   │   │   ├── reddit_service.py
│   │   │   ├── sentiment_service.py
│   │   │   ├── relevance_service.py
│   │   │   └── river_service.py
│   │   ├── utils/               # Utilities
│   │   │   ├── text_processing.py
│   │   │   └── config.py
│   │   └── cache.py             # Simple caching
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── SearchInput.jsx
│   │   │   ├── RiverFeed.jsx
│   │   │   └── PostCard.jsx
│   │   ├── services/
│   │   │   └── api.js          # API client
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── README.md
└── README.md                    # This file
```

## 🔧 Configuration

### Tech Keywords
Located in `backend/app/utils/config.py`:
- AI/ML: tensorflow, pytorch, machine learning, etc.
- Frameworks: react, django, fastapi, etc.
- Languages: python, javascript, rust, etc.
- Tools: docker, kubernetes, aws, etc.
- Concepts: microservices, devops, cicd, etc.

### Importance Scoring
Weights in `backend/app/utils/config.py`:
- Engagement (score + comments): 40%
- Recency: 30%
- Tech relevance: 20%
- Sentiment bonus: 10%

## 🚀 Future Enhancements

### Planned Features
- **X (Twitter) Integration**: Modular addition of Twitter data source
- **Embedding-based Relevance**: Replace keyword matching with ML embeddings
- **Advanced Clustering**: Group similar posts automatically
- **User Preferences**: Customizable filters and weights
- **Historical Analysis**: Track tech trends over time
- **Real-time Updates**: WebSocket integration for live updates

### Production Improvements
- **Redis Caching**: Replace in-memory cache with Redis
- **Database**: PostgreSQL for persistent storage
- **Authentication**: User accounts and preferences
- **Rate Limiting**: More sophisticated API rate limiting
- **Monitoring**: Application performance monitoring

## 🧪 Testing

### Backend
```bash
cd backend
python -m pytest tests/
```

### Frontend
```bash
cd frontend
npm test
```

## 📄 API Documentation

### GET `/api/river`
Fetch river feed from Reddit

**Parameters:**
- `source`: "reddit" (currently only Reddit supported)
- `name`: Subreddit name (e.g., "technology", "programming")
- `limit`: Maximum posts to return (default: 50)

**Response:**
```json
{
  "posts": [
    {
      "id": "post_id",
      "text": "Post content...",
      "url": "https://reddit.com/r/subreddit/comments/post_id",
      "importance_score": 0.85,
      "sentiment_label": "positive",
      "sentiment_score": 0.42,
      "tech_tags": ["python", "machine learning"],
      "created_at": "2024-01-15T10:30:00",
      "score": 1250,
      "comments": 45
    }
  ],
  "source": "reddit",
  "name": "technology"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is for educational purposes. Please respect Reddit's API terms of service.

## 🙏 Acknowledgments

- Reddit for providing the public API
- VADER sentiment analysis team
- FastAPI and React communities
