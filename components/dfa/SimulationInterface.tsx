import React, { useState, useEffect } from 'react';
import { DFA } from '@/lib/types';
import DFAVisualizer from '@/components/dfa-visualizer';
import { validateRegex } from '@/lib/challengeService';
import { describeDFA, generateTestStrings, simulateString } from '@/lib/dfaUtils';

interface SimulationInterfaceProps {
  dfa: DFA;
  solution: string;
  maxAttempts?: number;
  onSolved: (solved: boolean, attemptsUsed: number) => void;
  problemIndex: number;
  status?: { solved: boolean; attemptsUsed: number } | null;
}

const SimulationInterface: React.FC<SimulationInterfaceProps> = ({
  dfa,
  solution,
  maxAttempts = 3,
  onSolved,
  problemIndex,
  status,
}) => {
  const [regexInput, setRegexInput] = useState('');
  const [attempts, setAttempts] = useState(0);
  const [feedback, setFeedback] = useState<'correct' | 'incorrect' | null>(null);
  const [showSolution, setShowSolution] = useState(false);
  const [testStrings, setTestStrings] = useState<string[]>([]);
  const [testInput, setTestInput] = useState('');
  const [testResult, setTestResult] = useState<boolean | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  
  useEffect(() => {
    setRegexInput('');
    setTestInput('');
    setTestResult(null);
    
    if (status) {
      setAttempts(status.attemptsUsed);
      if (status.solved) {
        setFeedback('correct');
      } else if (status.attemptsUsed >= maxAttempts) {
        setFeedback('incorrect');
        setShowSolution(true);
      } else {
        setFeedback(null);
        setShowSolution(false);
      }
    } else {
      setAttempts(0);
      setFeedback(null);
      setShowSolution(false);
    }
    
    setTestStrings(generateTestStrings(dfa));
  }, [dfa, problemIndex, status, maxAttempts]);

  const handleRegexSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (attempts >= maxAttempts) {
      setFeedback('incorrect');
      return;
    }

    const isCorrect = validateRegex(regexInput, solution);
    setFeedback(isCorrect ? 'correct' : 'incorrect');
    
    const newAttempts = attempts + 1;
    setAttempts(newAttempts);
    
    if (isCorrect) {
      onSolved(true, newAttempts);
    } else if (newAttempts >= maxAttempts) {
      onSolved(false, newAttempts);
    }
  };

  const handleGiveUp = () => {
    setShowSolution(true);
    onSolved(false, maxAttempts);
  };
  
  const handleTestString = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!testInput.trim()) return;
    
    const result = simulateString(dfa, testInput);
    setTestResult(result);
  };
  
  const handleTestExample = (example: string) => {
    setTestInput(example);
    const result = simulateString(dfa, example);
    setTestResult(result);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="w-full h-64 border rounded-lg bg-secondary/30 overflow-hidden">
        <DFAVisualizer dfa={dfa} />
      </div>
      
      <div className="flex gap-2 items-center">
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm bg-secondary/50 px-3 py-1 rounded-md"
        >
          {showDetails ? 'Hide Details' : 'Show DFA Details'}
        </button>
        <span className="text-sm text-muted-foreground">
          View formal definition and test strings
        </span>
      </div>
      
      {showDetails && (
        <div className="p-4 border rounded-md bg-secondary/10">
          <h3 className="text-lg font-medium mb-3">DFA Details</h3>
          <pre className="bg-secondary/20 p-3 rounded text-sm font-mono overflow-x-auto">{describeDFA(dfa)}</pre>
          
          <div className="mt-4">
            <h4 className="font-medium mb-2">Test Strings</h4>
            <p className="text-sm text-muted-foreground mb-2">
              These strings should be accepted by the DFA. Click to test them.
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {testStrings.map((str, index) => (
                <button
                  key={index}
                  onClick={() => handleTestExample(str)}
                  className="px-2 py-1 bg-secondary/30 hover:bg-secondary/50 rounded text-sm font-mono"
                >
                  {str || '(empty string)'}
                </button>
              ))}
            </div>
            
            <form onSubmit={handleTestString} className="flex gap-2">
              <input
                type="text"
                value={testInput}
                onChange={(e) => setTestInput(e.target.value)}
                className="flex-1 px-3 py-2 border rounded-md font-mono"
                placeholder="Enter test string..."
              />
              <button
                type="submit"
                className="px-3 py-2 bg-secondary text-secondary-foreground rounded-md"
              >
                Test
              </button>
            </form>
            
            {testResult !== null && (
              <div className={`mt-2 p-2 rounded-md ${
                testResult 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-200' 
                  : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-200'
              }`}>
                <p className="text-sm">
                  <span className="font-mono">{testInput || '(empty string)'}</span> is 
                  {testResult ? ' accepted ✓' : ' rejected ✗'} by this DFA
                </p>
              </div>
            )}
          </div>
        </div>
      )}
      
      <form onSubmit={handleRegexSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="regex-input" className="text-sm font-medium">
            Enter Regular Expression
          </label>
          <div className="flex gap-2">
            <input
              id="regex-input"
              type="text"
              value={regexInput}
              onChange={(e) => setRegexInput(e.target.value)}
              className="flex-1 px-3 py-2 border rounded-md"
              placeholder="Type your regex solution..."
              disabled={feedback === 'correct' || showSolution}
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
              disabled={feedback === 'correct' || showSolution || !regexInput.trim()}
            >
              Submit
            </button>
          </div>
        </div>
        
        <div className="flex justify-between items-center">
          <div className="text-sm">
            Attempts: {attempts}/{maxAttempts}
          </div>
          
          {!showSolution && feedback !== 'correct' && (
            <button
              type="button"
              onClick={handleGiveUp}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Give Up
            </button>
          )}
        </div>
        
        {feedback && (
          <div className={`p-4 rounded-md ${
            feedback === 'correct' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {feedback === 'correct' 
              ? 'Correct! Well done.' 
              : `Incorrect. ${attempts >= maxAttempts ? 'No more attempts left.' : 'Try again.'}`}
          </div>
        )}
        
        {showSolution && (
          <div className="p-4 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-md">
            <p>The correct solution is: <code className="font-mono bg-blue-200 dark:bg-blue-800 px-1 rounded">{solution}</code></p>
          </div>
        )}
      </form>
    </div>
  );
};

export default SimulationInterface; 