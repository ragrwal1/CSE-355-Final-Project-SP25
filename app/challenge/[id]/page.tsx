'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getChallengeSet, getChallengeProgress, saveChallengeProgress } from '@/lib/challengeService';
import SimulationInterface from '@/components/dfa/SimulationInterface';
import { ChallengeSet, ProblemStatus } from '@/lib/types';
import Link from 'next/link';

export default function ChallengePage() {
  const params = useParams();
  const router = useRouter();
  const challengeId = params.id as string;
  
  const [challengeSet, setChallengeSet] = useState<ChallengeSet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentProblemIndex, setCurrentProblemIndex] = useState(0);
  const [problemStatuses, setProblemStatuses] = useState<ProblemStatus[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [showSummary, setShowSummary] = useState(false);

  useEffect(() => {
    const fetchChallengeSet = async () => {
      try {
        const data = await getChallengeSet(challengeId);
        if (!data) {
          setError('Challenge not found. Please check the code and try again.');
          setLoading(false);
          return;
        }
        
        setChallengeSet(data);
        
        // Get progress from localStorage
        const progress = getChallengeProgress(challengeId);
        if (progress) {
          // Ensure we have status entries for all problems
          const fullStatuses = new Array(data.regexSolutions.length).fill(null).map((_, index) => 
            progress.problemStatuses[index] || { solved: false, attemptsUsed: 0 }
          );
          
          setProblemStatuses(fullStatuses);
          
          // Check if all problems have been attempted
          const allAttempted = fullStatuses.every(status => 
            status.solved || status.attemptsUsed >= (data.configs.guessesPerProblem || 3)
          );
          
          // Check if all problems are solved
          const allSolved = fullStatuses.every(status => status.solved);
          
          setIsCompleted(allAttempted);
          setShowSummary(allAttempted);
        } else {
          // Initialize empty progress
          const emptyStatuses = new Array(data.regexSolutions.length).fill(null).map(() => ({
            solved: false,
            attemptsUsed: 0
          }));
          setProblemStatuses(emptyStatuses);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to load challenge. Please try again later.');
        setLoading(false);
      }
    };

    fetchChallengeSet();
  }, [challengeId]);

  const handleProblemSolved = (solved: boolean, attemptsUsed: number) => {
    if (!challengeSet) return;
    
    const newStatuses = [...problemStatuses];
    newStatuses[currentProblemIndex] = { solved, attemptsUsed };
    setProblemStatuses(newStatuses);
    
    // Save progress to localStorage
    saveChallengeProgress(challengeId, currentProblemIndex, { solved, attemptsUsed });
    
    // Check if all problems have been attempted (either solved or max attempts reached)
    const allAttempted = newStatuses.every((status, index) => 
      status.solved || status.attemptsUsed >= (challengeSet.configs.guessesPerProblem || 3)
    );
    
    if (allAttempted) {
      setIsCompleted(true);
      
      // Automatically show the summary if this was the last problem
      if (currentProblemIndex === challengeSet.regexSolutions.length - 1) {
        setShowSummary(true);
      }
    }
  };

  const navigateToProblem = (index: number) => {
    setCurrentProblemIndex(index);
  };

  const handleNextProblem = () => {
    if (challengeSet && currentProblemIndex < challengeSet.regexSolutions.length - 1) {
      setCurrentProblemIndex(currentProblemIndex + 1);
    }
  };

  const handlePreviousProblem = () => {
    if (currentProblemIndex > 0) {
      setCurrentProblemIndex(currentProblemIndex - 1);
    }
  };
  
  const handleShowSummary = () => {
    setShowSummary(true);
  };
  
  const handleHideSummary = () => {
    setShowSummary(false);
  };

  if (loading) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="animate-pulse">
          <div className="h-8 bg-secondary/50 rounded-md w-1/2 mx-auto mb-4"></div>
          <div className="h-64 bg-secondary/30 rounded-md w-full mb-8"></div>
          <div className="h-10 bg-secondary/50 rounded-md w-3/4 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="bg-red-100 dark:bg-red-900 p-6 rounded-lg">
          <h2 className="text-2xl font-bold text-red-800 dark:text-red-200 mb-4">Error</h2>
          <p className="text-red-700 dark:text-red-300 mb-6">{error}</p>
          <Link 
            href="/"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
          >
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  if (showSummary && challengeSet) {
    const solvedCount = problemStatuses.filter(status => status.solved).length;
    const totalProblems = challengeSet.regexSolutions.length;
    const percentage = Math.round((solvedCount / totalProblems) * 100);
    
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12">
        <div className={`p-8 rounded-lg text-center ${
          percentage >= 70 
            ? 'bg-green-100 dark:bg-green-900' 
            : percentage >= 40 
              ? 'bg-yellow-100 dark:bg-yellow-900' 
              : 'bg-red-100 dark:bg-red-900'
        }`}>
          <h2 className="text-3xl font-bold mb-6">Challenge Summary</h2>
          <div className="mb-8">
            <p className="text-lg mb-2">
              You've completed the challenge!
            </p>
            {challengeSet.name && (
              <p className="font-medium">
                Challenge: {challengeSet.name}
              </p>
            )}
            
            <div className="mt-4 inline-flex items-center px-4 py-2 rounded-full bg-white dark:bg-gray-800">
              <span className="text-xl font-bold">{solvedCount}/{totalProblems}</span>
              <span className="ml-2">problems solved correctly</span>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg mb-8 text-left">
            <h3 className="text-xl font-medium mb-4 text-center">Your Results</h3>
            <div className="space-y-4">
              {problemStatuses.map((status, index) => (
                <div 
                  key={index} 
                  className={`flex justify-between items-center p-3 border-b last:border-0 ${
                    status.solved 
                      ? 'bg-green-50 dark:bg-green-900/30' 
                      : status.attemptsUsed >= (challengeSet.configs.guessesPerProblem || 3)
                        ? 'bg-red-50 dark:bg-red-900/30'
                        : ''
                  }`}
                >
                  <div>
                    <span className="font-medium">Problem {index + 1}</span>
                    <div className="text-sm text-muted-foreground mt-1">
                      {challengeSet.regexSolutions[index]}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm">
                      {status.attemptsUsed} attempt{status.attemptsUsed !== 1 ? 's' : ''}
                    </span>
                    <span className={`font-medium px-2 py-1 rounded-md ${
                      status.solved 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}>
                      {status.solved ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="text-center text-sm text-muted-foreground mb-6">
            Take a screenshot of this page if you need to submit your results
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleHideSummary}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md"
            >
              Back to Problems
            </button>
            <Link 
              href="/"
              className="px-4 py-2 border border-primary text-primary hover:bg-primary/10 rounded-md"
            >
              Return to Home
            </Link>
            <Link 
              href="/practice"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
            >
              Try Infinite Practice
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!challengeSet) {
    return null;
  }

  return (
    <div className="container max-w-4xl mx-auto px-4 py-12">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {challengeSet.name || `Challenge: ${challengeId}`}
            </h1>
            {challengeSet.description && (
              <p className="text-muted-foreground">{challengeSet.description}</p>
            )}
          </div>
          <div className="flex gap-2">
            {isCompleted && (
              <button
                onClick={handleShowSummary}
                className="px-3 py-1 bg-primary text-primary-foreground text-sm rounded-md"
              >
                Show Summary
              </button>
            )}
            <Link 
              href="/"
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Home
            </Link>
          </div>
        </div>
        
        <div className="flex items-center justify-between bg-secondary/30 p-4 rounded-md">
          <div className="text-sm font-medium">
            Problem {currentProblemIndex + 1} of {challengeSet.regexSolutions.length}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handlePreviousProblem}
              disabled={currentProblemIndex === 0}
              className="p-2 rounded-md hover:bg-secondary disabled:opacity-50"
            >
              Previous
            </button>
            
            <div className="flex gap-1">
              {challengeSet.regexSolutions.map((_, index) => {
                const status = problemStatuses[index];
                let buttonClass = `w-8 h-8 rounded-full flex items-center justify-center text-sm`;
                
                if (index === currentProblemIndex) {
                  buttonClass += ' bg-primary text-primary-foreground';
                } else if (status?.solved) {
                  buttonClass += ' bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
                } else if (status?.attemptsUsed >= (challengeSet.configs.guessesPerProblem || 3)) {
                  buttonClass += ' bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
                } else {
                  buttonClass += ' bg-secondary/50 hover:bg-secondary';
                }
                
                return (
                  <button
                    key={index}
                    onClick={() => navigateToProblem(index)}
                    className={buttonClass}
                  >
                    {index + 1}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={handleNextProblem}
              disabled={currentProblemIndex === challengeSet.regexSolutions.length - 1}
              className="p-2 rounded-md hover:bg-secondary disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
      
      {challengeSet.dfas[currentProblemIndex] && challengeSet.regexSolutions[currentProblemIndex] && (
        <SimulationInterface
          key={`problem-${currentProblemIndex}`} // Add a key to force component recreation when changing problems
          dfa={challengeSet.dfas[currentProblemIndex]}
          solution={challengeSet.regexSolutions[currentProblemIndex]}
          maxAttempts={challengeSet.configs.guessesPerProblem}
          onSolved={handleProblemSolved}
          problemIndex={currentProblemIndex}
          status={problemStatuses[currentProblemIndex]}
        />
      )}
    </div>
  );
} 