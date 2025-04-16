import { ChallengeSet, DFA, ChallengeProgress, ProblemStatus } from './types';
import { validateDFA, matchesRegexPattern } from './dfaUtils';

// Mock challenge data (simulating database/API response)
const mockChallenges: Record<string, ChallengeSet> = {
  'DFA101': {
    id: 'DFA101',
    name: 'DFA Basics',
    description: 'A beginner-friendly set of DFA challenges',
    regexSolutions: ['a*b', '(a|b)*abb', 'a*b*'],
    dfas: [
      {
        regex: 'a*b',
        alphabet: ['a', 'b'],
        states: ['q0', 'q1', 'q2'],
        start: 'q0',
        accept: ['q1'],
        transitions: {
          q0: { a: 'q0', b: 'q1' },
          q1: { a: 'q2', b: 'q2' },
          q2: { a: 'q2', b: 'q2' }
        }
      },
      {
        regex: '(a|b)*abb',
        alphabet: ['a', 'b'],
        states: ['q0', 'q1', 'q2', 'q3'],
        start: 'q0',
        accept: ['q3'],
        transitions: {
          q0: { a: 'q1', b: 'q0' },
          q1: { a: 'q1', b: 'q2' },
          q2: { a: 'q1', b: 'q3' },
          q3: { a: 'q1', b: 'q0' }
        }
      },
      {
        regex: 'a*b*',
        alphabet: ['a', 'b'],
        states: ['q0', 'q1'],
        start: 'q0',
        accept: ['q0', 'q1'],
        transitions: {
          q0: { a: 'q0', b: 'q1' },
          q1: { a: 'q0', b: 'q1' }
        }
      }
    ],
    configs: {
      guessesPerProblem: 3
    }
  },
  'DFA102': {
    id: 'DFA102',
    name: 'Advanced DFA Challenges',
    description: 'More complex DFA to regex conversions',
    regexSolutions: ['(ab)*', 'a(a|b)*b', 'a*ba*'],
    dfas: [
      {
        regex: '(ab)*',
        alphabet: ['a', 'b'],
        states: ['q0', 'q1'],
        start: 'q0',
        accept: ['q0'],
        transitions: {
          q0: { a: 'q1', b: '' },
          q1: { a: '', b: 'q0' }
        }
      },
      {
        regex: 'a(a|b)*b',
        alphabet: ['a', 'b'],
        states: ['q0', 'q1', 'q2', 'q3'],
        start: 'q0',
        accept: ['q3'],
        transitions: {
          q0: { a: 'q1', b: '' },
          q1: { a: 'q1', b: 'q1' },
          q2: { a: '', b: 'q3' },
          q3: { a: '', b: '' }
        }
      },
      {
        regex: 'a*ba*',
        alphabet: ['a', 'b'],
        states: ['q0', 'q1', 'q2'],
        start: 'q0',
        accept: ['q2'],
        transitions: {
          q0: { a: 'q0', b: 'q1' },
          q1: { a: 'q2', b: '' },
          q2: { a: 'q2', b: '' }
        }
      }
    ],
    configs: {
      guessesPerProblem: 2
    }
  }
};

// DFA Templates for random generation
const dfaTemplates = [
  {
    name: 'Basic: Ends with character',
    generator: (config: { alphabet: string[] }): DFA => {
      const endChar = config.alphabet[Math.floor(Math.random() * config.alphabet.length)];
      const regex = `.*${endChar}`;
      
      return {
        regex,
        alphabet: [...config.alphabet],
        states: ['q0', 'q1'],
        start: 'q0',
        accept: ['q1'],
        transitions: {
          q0: Object.fromEntries(config.alphabet.map(char => [
            char, char === endChar ? 'q1' : 'q0'
          ])),
          q1: Object.fromEntries(config.alphabet.map(char => [
            char, char === endChar ? 'q1' : 'q0'
          ]))
        }
      };
    }
  },
  {
    name: 'Contains substring',
    generator: (config: { alphabet: string[] }): DFA => {
      const chars = config.alphabet;
      const firstChar = chars[Math.floor(Math.random() * chars.length)];
      const secondChar = chars[Math.floor(Math.random() * chars.length)];
      const regex = `.*${firstChar}${secondChar}.*`;
      
      return {
        regex,
        alphabet: [...chars],
        states: ['q0', 'q1', 'q2'],
        start: 'q0',
        accept: ['q2'],
        transitions: {
          q0: Object.fromEntries(chars.map(char => [
            char, char === firstChar ? 'q1' : 'q0'
          ])),
          q1: Object.fromEntries(chars.map(char => [
            char, char === secondChar ? 'q2' : char === firstChar ? 'q1' : 'q0'
          ])),
          q2: Object.fromEntries(chars.map(char => [
            char, 'q2'
          ]))
        }
      };
    }
  },
  {
    name: 'Even number of character',
    generator: (config: { alphabet: string[] }): DFA => {
      const targetChar = config.alphabet[Math.floor(Math.random() * config.alphabet.length)];
      const regex = `(${targetChar}${targetChar})*([^${targetChar}])*`;
      
      return {
        regex,
        alphabet: [...config.alphabet],
        states: ['q0', 'q1'],
        start: 'q0',
        accept: ['q0'],
        transitions: {
          q0: Object.fromEntries(config.alphabet.map(char => [
            char, char === targetChar ? 'q1' : 'q0'
          ])),
          q1: Object.fromEntries(config.alphabet.map(char => [
            char, char === targetChar ? 'q0' : 'q1'
          ]))
        }
      };
    }
  }
];

// Get a specific challenge set by ID
export const getChallengeSet = async (challengeId: string): Promise<ChallengeSet | null> => {
  console.log(`Fetching challenge set with ID: ${challengeId}`);
  // In a real app, this would fetch from an API or database
  return mockChallenges[challengeId] || null;
};

// Create a new challenge set (simulated)
export const createChallengeSet = async (challengeSet: Omit<ChallengeSet, 'id'>): Promise<string> => {
  console.log('Creating new challenge set:', challengeSet);
  
  // Validate all DFAs
  const invalidDfaIndex = challengeSet.dfas.findIndex(dfa => !validateDFA(dfa));
  if (invalidDfaIndex !== -1) {
    throw new Error(`Invalid DFA at index ${invalidDfaIndex}`);
  }
  
  // In a real app, this would send to an API/database and return a real ID
  const id = `CHALLENGE_${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
  
  // In a real implementation, we would store this in the database
  // For now, we'll just simulate success
  // mockChallenges[id] = { ...challengeSet, id };
  
  return id;
};

// Local storage utility functions for challenge progress
export const saveChallengeProgress = (challengeId: string, problemIndex: number, status: ProblemStatus): void => {
  if (typeof window === 'undefined') return; // Skip on server
  
  const storageKey = `challenge_progress_${challengeId}`;
  const existingProgress = localStorage.getItem(storageKey);
  
  let progress: ChallengeProgress;
  
  if (existingProgress) {
    progress = JSON.parse(existingProgress);
    if (!progress.problemStatuses[problemIndex]) {
      progress.problemStatuses[problemIndex] = status;
    } else {
      progress.problemStatuses[problemIndex] = {
        ...progress.problemStatuses[problemIndex],
        ...status
      };
    }
  } else {
    progress = {
      challengeId,
      problemStatuses: []
    };
    progress.problemStatuses[problemIndex] = status;
  }
  
  localStorage.setItem(storageKey, JSON.stringify(progress));
};

export const getChallengeProgress = (challengeId: string): ChallengeProgress | null => {
  if (typeof window === 'undefined') return null; // Skip on server
  
  const storageKey = `challenge_progress_${challengeId}`;
  const progress = localStorage.getItem(storageKey);
  
  if (!progress) return null;
  
  return JSON.parse(progress);
};

// Utility to save challenge codes to localStorage
export const saveRecentChallengeCode = (code: string): void => {
  if (typeof window === 'undefined') return; // Skip on server
  
  const codes = getRecentChallengeCodes();
  if (!codes.includes(code)) {
    codes.push(code);
    localStorage.setItem('recent_challenge_codes', JSON.stringify(codes));
  }
};

export const getRecentChallengeCodes = (): string[] => {
  if (typeof window === 'undefined') return []; // Skip on server
  
  const codes = localStorage.getItem('recent_challenge_codes');
  return codes ? JSON.parse(codes) : [];
};

// Practice mode configuration types
export interface DFAGenerationConfig {
  alphabet: string[];
  complexity: 'easy' | 'medium' | 'hard';
  templateIndex?: number; // If specified, uses this template; otherwise random
}

// Default practice configuration
export const defaultPracticeConfig: DFAGenerationConfig = {
  alphabet: ['a', 'b'],
  complexity: 'easy'
};

// Generate a random DFA for infinite practice
export const generateRandomDFA = (config: DFAGenerationConfig = defaultPracticeConfig): DFA => {
  // Use a specific template if provided, otherwise random
  const templateIndex = config.templateIndex !== undefined
    ? config.templateIndex
    : Math.floor(Math.random() * dfaTemplates.length);
  
  // Use the template to generate a DFA
  const template = dfaTemplates[templateIndex];
  try {
    const dfa = template.generator(config);
    
    // Validate the generated DFA
    if (!validateDFA(dfa)) {
      throw new Error('Generated DFA is invalid');
    }
    
    return dfa;
  } catch (error) {
    console.error('Error generating DFA:', error);
    
    // Fallback to a simple template from the mock data
    const templates = Object.values(mockChallenges).flatMap(challenge => challenge.dfas);
    const randomIndex = Math.floor(Math.random() * templates.length);
    return templates[randomIndex];
  }
};

// Get all available DFA templates for the UI
export const getDFATemplates = () => {
  return dfaTemplates.map((template, index) => ({
    id: index,
    name: template.name
  }));
};

// Validate a regex solution
export const validateRegex = (input: string, solution: string): boolean => {
  // In a real implementation, this would do proper regex comparison
  // For now, just do a simple string comparison
  
  // Basic normalization (remove whitespace)
  const normalizedInput = input.trim().replace(/\s+/g, '');
  const normalizedSolution = solution.trim().replace(/\s+/g, '');
  
  // Try exact matching first
  if (normalizedInput === normalizedSolution) {
    return true;
  }
  
  // For future: could add more sophisticated comparison here
  
  return false;
}; 