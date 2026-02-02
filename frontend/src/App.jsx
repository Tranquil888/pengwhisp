import React, { useState } from 'react';
import RiverFeed from './components/RiverFeed';
import SearchInput from './components/SearchInput';
import './App.css';

function App() {
  const [subreddit, setSubreddit] = useState('technology');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubredditChange = (newSubreddit) => {
    setSubreddit(newSubreddit);
  };

  const handleLoadingChange = (loading) => {
    setIsLoading(loading);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Tech Relevance & Sentiment Analyzer</h1>
        <p>Analyze technology trends and sentiment from Reddit</p>
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
