# Tech Relevance & Sentiment Analyzer - Frontend

React frontend for the Tech Relevance & Sentiment Analyzer web application.

## Features

- Clean, modern UI with river-style feed
- Subreddit search with popular suggestions
- Real-time sentiment indicators
- Technology tag display
- Importance scoring visualization
- Responsive design for mobile and desktop
- Error handling and loading states

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The app will be available at `http://localhost:3000`

**Note:** Make sure the backend server is running on `http://localhost:8000` before starting the frontend.

## Components

### SearchInput
- Subreddit name input field
- Popular subreddit suggestions
- Loading state handling

### RiverFeed
- Main feed display
- Post loading and error handling
- Refresh functionality
- Statistics display

### PostCard
- Individual post display
- Sentiment indicator with emoji
- Technology tags
- Importance score
- Engagement metrics (score, comments)
- Link to original Reddit post

## Styling

The application uses:
- Modern CSS with flexbox and grid
- Gradient backgrounds and hover effects
- Responsive design patterns
- Color-coded sentiment indicators
- Clean typography

## API Integration

The frontend communicates with the backend via:
- `/api/river` endpoint for fetching posts
- Error handling for network issues
- Loading states during API calls
- Automatic retry functionality

## Development

The frontend follows React best practices:
- Functional components with hooks
- Component-based architecture
- Separation of concerns
- Reusable UI components
- Responsive design principles

## Environment Variables

Optional environment variables:
- `REACT_APP_API_URL`: Backend API URL (defaults to http://localhost:8000)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
