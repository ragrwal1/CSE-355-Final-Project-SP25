'use client';

import { useState, useEffect } from 'react';
import { generateRandomDFA, getDFATemplates, DFAGenerationConfig, defaultPracticeConfig } from '@/lib/challengeService';
import SimulationInterface from '@/components/dfa/SimulationInterface';
import { DFA } from '@/lib/types';
import Link from 'next/link';

export default function PracticePage() {
  const [currentDFA, setCurrentDFA] = useState<DFA | null>(null);
  const [loading, setLoading] = useState(true);
  const [practiceCount, setPracticeCount] = useState(0);
  const [solvedCount, setSolvedCount] = useState(0);
  const [sessionStats, setSessionStats] = useState({
    totalAttempts: 0,
    solvedProblems: 0,
    skippedProblems: 0
  });
  const [dfaTemplates, setDfaTemplates] = useState<{id: number, name: string}[]>([]);
  
  // Configuration state
  const [config, setConfig] = useState<DFAGenerationConfig>(defaultPracticeConfig);
  const [showConfig, setShowConfig] = useState(false);

  // Load templates and a random DFA when the page loads
  useEffect(() => {
    setDfaTemplates(getDFATemplates());
    generateNewProblem();
  }, []);

  const generateNewProblem = () => {
    setLoading(true);
    try {
      const newDfa = generateRandomDFA(config);
      setCurrentDFA(newDfa);
      setPracticeCount(count => count + 1);
    } catch (error) {
      console.error('Failed to generate DFA:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProblemSolved = (solved: boolean, attemptsUsed: number) => {
    setSessionStats(prev => ({
      totalAttempts: prev.totalAttempts + attemptsUsed,
      solvedProblems: solved ? prev.solvedProblems + 1 : prev.solvedProblems,
      skippedProblems: !solved ? prev.skippedProblems + 1 : prev.skippedProblems
    }));

    if (solved) {
      setSolvedCount(count => count + 1);
    }
  };

  const handleSkipProblem = () => {
    setSessionStats(prev => ({
      ...prev,
      skippedProblems: prev.skippedProblems + 1
    }));
    generateNewProblem();
  };
  
  const handleAlphabetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const alphabetStr = e.target.value.trim();
    if (!alphabetStr) return;
    
    // Convert the comma-separated string to an array and remove duplicates
    const alphabet = [...new Set(alphabetStr.split(',').map(char => char.trim()).filter(Boolean))];
    
    setConfig(prev => ({
      ...prev,
      alphabet
    }));
  };
  
  const handleComplexityChange = (complexity: 'easy' | 'medium' | 'hard') => {
    setConfig(prev => ({
      ...prev,
      complexity
    }));
  };
  
  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    
    if (value === 'random') {
      setConfig(prev => ({
        ...prev,
        templateIndex: undefined
      }));
    } else {
      setConfig(prev => ({
        ...prev,
        templateIndex: parseInt(value)
      }));
    }
  };
  
  const handleApplyConfig = () => {
    setShowConfig(false);
    generateNewProblem();
  };

  return (
    <div className="container max-w-4xl mx-auto px-4 py-12">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Infinite Practice Mode</h1>
          <p className="text-muted-foreground">
            Practice with randomly generated DFAs.
          </p>
        </div>
        <Link 
          href="/"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          Return to Home
        </Link>
      </div>
      
      <div className="flex items-center justify-between bg-secondary/30 p-4 rounded-md mb-6">
        <div className="text-sm">
          <span className="font-medium">Problem #{practiceCount}</span>
          {solvedCount > 0 && (
            <span className="ml-4 text-green-600 dark:text-green-400">
              Solved: {solvedCount}
            </span>
          )}
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="px-3 py-1 text-sm bg-secondary/80 text-secondary-foreground rounded"
          >
            {showConfig ? 'Hide Config' : 'Show Config'}
          </button>
          <button
            onClick={handleSkipProblem}
            className="px-3 py-1 text-sm bg-secondary text-secondary-foreground rounded"
          >
            Skip Problem
          </button>
          <button
            onClick={generateNewProblem}
            className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded"
          >
            New Problem
          </button>
        </div>
      </div>
      
      {/* Configuration Panel */}
      {showConfig && (
        <div className="mb-6 p-4 border rounded-md bg-card">
          <h2 className="text-lg font-semibold mb-4">DFA Generation Settings</h2>
          
          <div className="grid gap-4 sm:grid-cols-2 mb-4">
            <div className="space-y-2">
              <label htmlFor="alphabet" className="text-sm font-medium">
                Alphabet (comma-separated)
              </label>
              <input
                id="alphabet"
                type="text"
                defaultValue={config.alphabet.join(',')}
                onChange={handleAlphabetChange}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="e.g., a,b,c"
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="template" className="text-sm font-medium">
                DFA Template
              </label>
              <select
                id="template"
                value={config.templateIndex !== undefined ? config.templateIndex.toString() : 'random'}
                onChange={handleTemplateChange}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="random">Random Template</option>
                {dfaTemplates.map(template => (
                  <option key={template.id} value={template.id.toString()}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="space-y-2 mb-4">
            <label className="text-sm font-medium">Complexity</label>
            <div className="flex gap-3">
              {(['easy', 'medium', 'hard'] as const).map(level => (
                <button
                  key={level}
                  onClick={() => handleComplexityChange(level)}
                  className={`px-3 py-1 rounded ${
                    config.complexity === level 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-secondary/50'
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>
          
          <button
            onClick={handleApplyConfig}
            className="w-full px-3 py-2 bg-primary text-primary-foreground rounded-md font-medium"
          >
            Apply & Generate New Problem
          </button>
        </div>
      )}
      
      {loading ? (
        <div className="animate-pulse">
          <div className="h-64 bg-secondary/30 rounded-md w-full mb-8"></div>
          <div className="h-10 bg-secondary/50 rounded-md w-3/4 mx-auto"></div>
        </div>
      ) : currentDFA ? (
        <SimulationInterface
          dfa={currentDFA}
          solution={currentDFA.regex}
          maxAttempts={3}
          onSolved={handleProblemSolved}
        />
      ) : (
        <div className="text-center p-8 bg-red-100 dark:bg-red-900 rounded-lg">
          <p className="text-red-700 dark:text-red-300">
            Failed to generate a DFA. Please try again.
          </p>
          <button
            onClick={generateNewProblem}
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md"
          >
            Try Again
          </button>
        </div>
      )}
      
      {sessionStats.solvedProblems > 0 && (
        <div className="mt-8 p-4 bg-secondary/20 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Session Statistics</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold">{sessionStats.solvedProblems}</p>
              <p className="text-sm text-muted-foreground">Solved</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{sessionStats.skippedProblems}</p>
              <p className="text-sm text-muted-foreground">Skipped</p>
            </div>
            <div>
              <p className="text-2xl font-bold">
                {sessionStats.solvedProblems > 0 
                  ? (sessionStats.totalAttempts / sessionStats.solvedProblems).toFixed(1) 
                  : '0'}
              </p>
              <p className="text-sm text-muted-foreground">Avg. Attempts</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 