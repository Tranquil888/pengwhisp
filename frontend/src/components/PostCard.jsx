import React, { useState } from 'react';
import './PostCard.css';

const PostCard = ({ post }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

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

  const handleToggleExpand = () => {
    if (isExpanded) {
      setIsExpanded(false);
      setImageLoaded(false);
      setImageError(false);
    } else {
      setIsExpanded(true);
      console.log('Expanding post with image:', {
        has_image: post.has_image,
        image_url: post.image_url,
        thumbnail_url: post.thumbnail_url,
        post_hint: post.post_hint
      });
    }
  };

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  // Function to handle image URL with fallback strategy
  const getImageUrl = (url, thumbnailUrl) => {
    if (!url) return thumbnailUrl;
    return url; // Try direct URL first
  };

  const getFallbackUrl = (thumbnailUrl) => {
    return thumbnailUrl;
  };

  const handleImageError = (e) => {
    console.error('Image failed to load:', {
      src: e.target.src,
      alt: e.target.alt,
      error: e
    });
    
    // If we haven't tried thumbnail yet, try it as fallback
    if (post.thumbnail_url && !e.target.src.includes('thumbnail')) {
      console.log('Trying thumbnail fallback...');
      e.target.src = post.thumbnail_url;
      setImageError(false); // Reset error state to try again
    } else {
      // If both failed, show error
      setImageError(true);
    }
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
      
      {/* Show Full Post Button */}
      {post.has_image && (
        <div className="post-image-toggle">
          <button 
            onClick={handleToggleExpand}
            className="show-full-post-btn"
          >
            {isExpanded ? 'Hide' : 'Show'} Full Post {post.has_image && '🖼️'}
          </button>
        </div>
      )}

      {/* Expanded Image Section */}
      {isExpanded && post.image_url && (
        <div className="post-image-container">
          {!imageLoaded && !imageError && (
            <div className="image-loader">
              <div className="spinner"></div>
              <p>Loading image...</p>
            </div>
          )}
          
          {imageError ? (
            <div className="image-error">
              <p>❌ Failed to load image</p>
              <small>The image may have been removed or is unavailable</small>
              <button 
                onClick={handleToggleExpand}
                className="retry-image-btn"
                style={{ marginTop: '0.5rem', padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
              >
                Try Again
              </button>
            </div>
          ) : (
            <img 
              src={getImageUrl(post.image_url, post.thumbnail_url)}
              alt={post.title}
              onLoad={handleImageLoad}
              onError={handleImageError}
              style={{ display: imageLoaded ? 'block' : 'none' }}
              className="post-image"
            />
          )}
        </div>
      )}
      
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
