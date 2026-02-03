import React, { useState } from 'react';
import RiverFeed from './components/RiverFeed';
import SearchInput from './components/SearchInput';
import './App.css';

function App() {
  const [subreddit, setSubreddit] = useState('technology');
  const [isLoading, setIsLoading] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(true);

  const handleSubredditChange = (newSubreddit) => {
    setSubreddit(newSubreddit);
  };

  const handleLoadingChange = (loading) => {
    setIsLoading(loading);
  };

  const toggleTheme = () => {
    setIsDarkTheme(!isDarkTheme);
  };

  return (
    <div className={`App ${isDarkTheme ? 'dark-theme' : 'light-theme'}`}>
      <header className="App-header">
        <div className="header-content">
          <span className="penguin-icon">🐧</span>
          <h1>Pengwhisp</h1>
        </div>
        <button 
          className="theme-toggle-button"
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {isDarkTheme ? '☀️' : '🌙'}
        </button>
      </header>
      
      <main className="App-main">
        <SearchInput 
          onSubredditChange={handleSubredditChange}
          isLoading={isLoading}
        />
        
        <RiverFeed 
          subreddit={subreddit}
          onLoadingChange={handleLoadingChange}
        />
      </main>
      
      <footer className="App-footer">
        <p>Powered by Reddit API • VADER Sentiment Analysis • Tech Keyword Detection</p>
      </footer>
    </div>
  );
}

export default App;
