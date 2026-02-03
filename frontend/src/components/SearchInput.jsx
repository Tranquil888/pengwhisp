import React, { useState } from 'react';
import './SearchInput.css';

const SearchInput = ({ onSubredditChange, isLoading }) => {
  const [inputValue, setInputValue] = useState('technology');
  const [suggestions] = useState([
    'technology', 'programming', 'MachineLearning', 'webdev', 
    'python', 'javascript', 'reactjs', 'datascience', 'AI', 'cloud',
    'cybersecurity', 'blockchain', 'mobile', 'gamedev', 'database'
  ]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSubredditChange(inputValue.trim());
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    if (!isLoading) {
      onSubredditChange(suggestion);
    }
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter subreddit name..."
            className="search-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? 'Loading...' : 'Analyze'}
          </button>
        </div>
      </form>
      
      <div className="suggestions">
        <span className="suggestions-label">Popular:</span>
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => handleSuggestionClick(suggestion)}
            className="suggestion-button"
            disabled={isLoading}
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SearchInput;
