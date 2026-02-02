import React from 'react';
import './PostCard.css';

const PostCard = ({ post }) => {
  const getSentimentColor = (label) => {
    switch (label) {
      case 'positive':
        return '#10b981'; // green
      case 'negative':
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const getSentimentIcon = (label) => {
    switch (label) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😞';
      default:
        return '😐';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      return 'just now';
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  const truncateText = (text, maxLength = 300) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).replace(/\s+\S*$/, '') + '...';
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <div className="post-meta">
          <span className="post-score">▲ {post.score}</span>
          <span className="post-comments">💬 {post.comments}</span>
          <span className="post-time">{formatDate(post.created_at)}</span>
        </div>
        <div className="post-importance">
          <span className="importance-score">
            {(post.importance_score * 100).toFixed(1)}%
          </span>
        </div>
      </div>
      
      <div className="post-content">
        <p className="post-text">{truncateText(post.text)}</p>
      </div>
      
      <div className="post-footer">
        <div className="post-tags">
          {post.tech_tags.slice(0, 5).map((tag, index) => (
            <span key={index} className="tech-tag">
              {tag}
            </span>
          ))}
          {post.tech_tags.length > 5 && (
            <span className="tech-tag more">
              +{post.tech_tags.length - 5} more
            </span>
          )}
        </div>
        
        <div className="post-sentiment">
          <span 
            className="sentiment-indicator"
            style={{ color: getSentimentColor(post.sentiment_label) }}
          >
            <span className="sentiment-icon">{getSentimentIcon(post.sentiment_label)}</span>
            <span className="sentiment-label">{post.sentiment_label}</span>
            <span className="sentiment-score">
              ({post.sentiment_score.toFixed(2)})
            </span>
          </span>
        </div>
      </div>
      
      <div className="post-actions">
        <a 
          href={post.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="view-on-reddit"
        >
          View on Reddit →
        </a>
      </div>
    </div>
  );
};

export default PostCard;
