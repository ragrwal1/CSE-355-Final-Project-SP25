import { DFA } from './types';

/**
 * Validates that a DFA is properly formatted and contains all required properties
 */
export const validateDFA = (dfa: any): boolean => {
  // Check if all required properties exist
  if (!dfa.alphabet || !dfa.states || !dfa.start || !dfa.accept || !dfa.transitions) {
    return false;
  }
  
  // Validate alphabet is an array of strings
  if (!Array.isArray(dfa.alphabet) || !dfa.alphabet.every((symbol: any) => typeof symbol === 'string')) {
    return false;
  }
  
  // Validate states is an array of strings
  if (!Array.isArray(dfa.states) || !dfa.states.every((state: any) => typeof state === 'string')) {
    return false;
  }
  
  // Validate start state exists in states
  if (typeof dfa.start !== 'string' || !dfa.states.includes(dfa.start)) {
    return false;
  }
  
  // Validate accept states are in states
  if (!Array.isArray(dfa.accept) || 
      !dfa.accept.every((state: any) => typeof state === 'string' && dfa.states.includes(state))) {
    return false;
  }
  
  // Validate transitions
  if (typeof dfa.transitions !== 'object') {
    return false;
  }
  
  // Check if all states have transitions
  for (const state of dfa.states) {
    if (!dfa.transitions[state]) {
      return false;
    }
    
    // Check that all transitions use symbols from the alphabet
    const transitions = dfa.transitions[state];
    for (const symbol in transitions) {
      if (!dfa.alphabet.includes(symbol)) {
        return false;
      }
      
      // Check that transitions lead to valid states
      const targetState = transitions[symbol];
      if (targetState && !dfa.states.includes(targetState)) {
        return false;
      }
    }
  }
  
  return true;
};

/**
 * Simulates running a string through the DFA to see if it's accepted
 */
export const simulateString = (dfa: DFA, input: string): boolean => {
  let currentState = dfa.start;
  
  // Process each character in the input string
  for (let i = 0; i < input.length; i++) {
    const symbol = input[i];
    
    // Check if the symbol is in the alphabet
    if (!dfa.alphabet.includes(symbol)) {
      return false; // Invalid symbol
    }
    
    // Get the transition for the current state and symbol
    const nextState = dfa.transitions[currentState][symbol];
    
    // If there's no transition defined, the string is rejected
    if (!nextState) {
      return false;
    }
    
    // Move to the next state
    currentState = nextState;
  }
  
  // Check if the final state is an accept state
  return dfa.accept.includes(currentState);
};

/**
 * Creates a simplified DFA description for display
 */
export const describeDFA = (dfa: DFA): string => {
  const alphabetDesc = `Alphabet: {${dfa.alphabet.join(', ')}}`;
  const statesDesc = `States: {${dfa.states.join(', ')}}`;
  const startDesc = `Start state: ${dfa.start}`;
  const acceptDesc = `Accept states: {${dfa.accept.join(', ')}}`;
  
  return `${alphabetDesc}\n${statesDesc}\n${startDesc}\n${acceptDesc}`;
};

/**
 * Generates test strings that should be accepted by the DFA
 */
export const generateTestStrings = (dfa: DFA, maxLength: number = 5, count: number = 3): string[] => {
  const results: string[] = [];
  const alphabet = dfa.alphabet;
  
  // For very simple DFAs, try to include the empty string if it's accepted
  if (dfa.accept.includes(dfa.start)) {
    results.push('');
  }
  
  // Generate random strings and check if they're accepted
  const attemptLimit = 50; // Limit attempts to prevent infinite loops
  let attempts = 0;
  
  while (results.length < count && attempts < attemptLimit) {
    attempts++;
    
    // Generate a random string
    const length = Math.floor(Math.random() * maxLength) + 1;
    let testString = '';
    
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * alphabet.length);
      testString += alphabet[randomIndex];
    }
    
    // Check if the string is accepted and not already in results
    if (simulateString(dfa, testString) && !results.includes(testString)) {
      results.push(testString);
    }
  }
  
  return results;
};

/**
 * Checks if a regex pattern could be a valid solution for the given DFA
 * This is a very simplified implementation and would need much more sophistication
 * for a real-world application
 */
export const matchesRegexPattern = (dfa: DFA, regex: string): boolean => {
  // In a real implementation, this would construct a regex from the pattern
  // and test it against a set of strings that the DFA accepts and rejects
  
  // For now, just compare with the known regex solution (if it exists)
  return dfa.regex === regex;
};

export default {
  validateDFA,
  simulateString,
  describeDFA,
  generateTestStrings,
  matchesRegexPattern
}; 