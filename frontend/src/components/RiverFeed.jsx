import React, { useState, useEffect } from 'react';
import PostCard from './PostCard';
import { fetchRiverFeed } from '../services/api';
import './RiverFeed.css';

const RiverFeed = ({ subreddit, onLoadingChange }) => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [searchMethod, setSearchMethod] = useState('direct');

  useEffect(() => {
    loadPosts();
  }, [subreddit]);

  const loadPosts = async () => {
    if (!subreddit) return;

    setLoading(true);
    setError(null);
    onLoadingChange(true);

    try {
      const response = await fetchRiverFeed('reddit', subreddit, 50);
      setPosts(response.posts || []);
      setSearchMethod(response.search_method || 'direct');
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      setPosts([]);
      setSearchMethod('direct');
    } finally {
      setLoading(false);
      onLoadingChange(false);
    }
  };

  const handleRetry = () => {
    loadPosts();
  };

  const formatLastUpdated = () => {
    if (!lastUpdated) return '';
    const now = new Date();
    const diffInMinutes = Math.floor((now - lastUpdated) / 60000);
    
    if (diffInMinutes < 1) return 'just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const diffInHours = Math.floor(diffInMinutes / 60);
    return `${diffInHours}h ago`;
  };

  if (loading) {
    return (
      <div className="river-feed">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Analyzing r/{subreddit}...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="river-feed">
        <div className="error-container">
          <h3>❌ Error</h3>
          <p>{error}</p>
          <button onClick={handleRetry} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!posts || posts.length === 0) {
    return (
      <div className="river-feed">
        <div className="empty-container">
          <h3>📭 No posts found</h3>
          <p>No relevant posts found in r/{subreddit}</p>
          <p>Try a different subreddit or check if the subreddit exists.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="river-feed">
      <div className="river-header">
        <h2>r/{subreddit} River Feed</h2>
        {searchMethod === 'fallback' && (
          <div className="fallback-indicator">
            <span className="fallback-badge">🔍 Smart Search</span>
            <span className="fallback-text">Found related content from similar subreddits</span>
          </div>
        )}
        <div className="river-stats">
          <span className="post-count">{posts.length} important posts</span>
          {lastUpdated && (
            <span className="last-updated">Updated {formatLastUpdated()}</span>
          )}
        </div>
      </div>

      <div className="posts-container">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      <div className="river-footer">
        <button onClick={loadPosts} className="refresh-button">
          🔄 Refresh
        </button>
        <p className="disclaimer">
          Posts are filtered by importance score based on engagement, recency, and tech relevance.
        </p>
      </div>
    </div>
  );
};

export default RiverFeed;
