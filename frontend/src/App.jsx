import React, { useState, useEffect, useRef } from 'react';
import './index.css';

const API_URL = 'https://pythonmaxxing.onrender.com';

function App() {
  const [gameMode, setGameMode] = useState('menu');
  const [level, setLevel] = useState(null);
  const [question, setQuestion] = useState(null);
  const [userCode, setUserCode] = useState('');
  const [result, setResult] = useState(null);
  const [score, setScore] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const [timeLimit, setTimeLimit] = useState(120);
  const [timeRemaining, setTimeRemaining] = useState(120);
  const [selectedLevels, setSelectedLevels] = useState([1, 2, 3, 4, 5, 6]);
  const [timedModeActive, setTimedModeActive] = useState(false);

  const textareaRef = useRef(null);

  useEffect(() => {
    if (gameMode === 'play') {
      fetchQuestion();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameMode]);

  useEffect(() => {
    if (question && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [question]);

  useEffect(() => {
    if (!timedModeActive) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          setTimedModeActive(false);
          setGameMode('timed-results');
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timedModeActive]);

  const fetchQuestion = async (selectedLevel = null) => {
    setLoading(true);
    setUserCode('');
    setResult(null);

    let url = `${API_URL}/api/question`;
    if (selectedLevel) {
      url += `?level=${selectedLevel}`;
    } else if (timedModeActive && selectedLevels.length > 0) {
      const randomLevel = selectedLevels[Math.floor(Math.random() * selectedLevels.length)];
      url += `?level=${randomLevel}`;
    }

    try {
      const response = await fetch(url);
      const data = await response.json();
      setQuestion(data);
      setLevel(data.level);
    } catch (error) {
      console.error('Error fetching question:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!userCode.trim() || !question) return;

    try {
      const response = await fetch(`${API_URL}/api/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: userCode,
          id: question.id,
        }),
      });

      const data = await response.json();
      setResult(data);
      setTotal(total + 1);

      if (data.correct) {
        setScore(score + 1);
      }
    } catch (error) {
      console.error('Error checking answer:', error);
      setResult({ error: 'Error submitting answer' });
    }
  };

  const handleNextQuestion = () => {
    if (result?.correct) {
      if (timedModeActive) {
        fetchQuestion();
      } else {
        fetchQuestion(level);
      }
    }
  };

  const startTimedMode = () => {
    if (selectedLevels.length === 0) return;
    setScore(0);
    setTotal(0);
    setTimeRemaining(timeLimit);
    setTimedModeActive(true);
    setGameMode('play');
  };

  const toggleLevel = (l) => {
    setSelectedLevels((prev) =>
      prev.includes(l) ? prev.filter((x) => x !== l) : [...prev, l]
    );
  };

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (result?.correct && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        handleNextQuestion();
      }
    };
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result, level]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="app">
      <header className="header">
        <h1>PythonMaxxing</h1>
        {gameMode === 'play' && (
          <div className="score">
            {timedModeActive ? (
              <>
                Score: {score}/{total} | Time: {formatTime(timeRemaining)}
              </>
            ) : (
              <>Score: {score}/{total}</>
            )}
          </div>
        )}
      </header>

      <main className="main">
        {gameMode === 'menu' && (
          <div className="menu">
            <h2>Select Game Mode</h2>
            <button className="mode-btn" onClick={() => setGameMode('play')}>
              Normal Mode
            </button>
            <button className="mode-btn" onClick={() => setGameMode('timed-setup')}>
              Timed Mode
            </button>
          </div>
        )}

        {gameMode === 'timed-setup' && (
          <div className="timed-setup">
            <h2>Timed Mode Setup</h2>

            <div className="time-setting">
              <label>Time Limit (seconds):</label>
              <input
                type="number"
                min="10"
                max="600"
                step="10"
                value={timeLimit}
                onChange={(e) => setTimeLimit(parseInt(e.target.value))}
              />
              <p>({Math.floor(timeLimit / 60)}m {timeLimit % 60}s)</p>
            </div>

            <div className="level-selection">
              <label>Select Levels:</label>
              <div className="checkbox-group">
                {[1, 2, 3, 4, 5, 6].map((l) => (
                  <label key={l} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedLevels.includes(l)}
                      onChange={() => toggleLevel(l)}
                    />
                    Level {l}
                  </label>
                ))}
              </div>
            </div>

            <div className="setup-buttons">
              <button
                className="start-btn"
                onClick={startTimedMode}
                disabled={selectedLevels.length === 0}
              >
                Start
              </button>
              <button className="back-btn" onClick={() => setGameMode('menu')}>
                Back
              </button>
            </div>
          </div>
        )}

        {gameMode === 'play' && (
          <>
            {loading ? (
              <div className="loading">Loading...</div>
            ) : question ? (
              <div className="question-container">
                <div className="level-badge">Level {question.level}</div>
                <p className="prompt">{question.prompt}</p>

                <div className="context">
                  <h3>Context:</h3>
                  {Object.entries(question.context_display).map(([key, value]) => (
                    <div key={key} className="context-item">
                      <code>{key} = {value}</code>
                    </div>
                  ))}
                </div>

                <div className="input-section">
                  <textarea
                    ref={textareaRef}
                    className="code-input"
                    value={userCode}
                    onChange={(e) => setUserCode(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                    placeholder="Enter your Python code here..."
                    disabled={result?.correct}
                  />

                  {!result?.correct && (
                    <button
                      className="submit-btn"
                      onClick={handleSubmit}
                      disabled={!userCode.trim()}
                    >
                      Submit
                    </button>
                  )}
                </div>

                {result && (
                  <div className={`result ${result.correct ? 'correct' : 'incorrect'}`}>
                    {result.correct ? (
                      <>
                        <h3>✓ Correct</h3>
                        <button className="next-btn" onClick={handleNextQuestion}>
                          Next
                        </button>
                      </>
                    ) : (
                      <>
                        <h3>✗ Incorrect</h3>
                        {result.error ? (
                          <p className="error-msg">Error: {result.error}</p>
                        ) : (
                          <>
                            <p>
                              <strong>Expected:</strong> <code>{result.expected}</code>
                            </p>
                            <p>
                              <strong>Got:</strong> <code>{result.user_result}</code>
                            </p>
                          </>
                        )}
                        <button className="retry-btn" onClick={() => setResult(null)}>
                          Try Again
                        </button>
                      </>
                    )}
                  </div>
                )}

                {!timedModeActive && (
                  <div className="level-selector">
                    <p>Select level:</p>
                    <div className="level-buttons">
                      {[1, 2, 3, 4, 5, 6].map((l) => (
                        <button
                          key={l}
                          className={`level-btn ${level === l ? 'active' : ''}`}
                          onClick={() => fetchQuestion(l)}
                        >
                          {l}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {!timedModeActive && (
                  <button className="menu-btn" onClick={() => setGameMode('menu')}>
                    Back to Menu
                  </button>
                )}
              </div>
            ) : (
              <p>Error loading question</p>
            )}
          </>
        )}

        {gameMode === 'timed-results' && (
          <div className="results-screen">
            <h2>Time's Up!</h2>
            <div className="final-score">
              <p>Final Score: {score}/{total}</p>
              <p>Accuracy: {total > 0 ? ((score / total) * 100).toFixed(1) : 0}%</p>
            </div>
            <button className="menu-btn" onClick={() => setGameMode('menu')}>
              Back to Menu
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
