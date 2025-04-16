import { DFA } from './types';

// Sample DFA data for demos and testing
export const dfaData: DFA = {
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
};

// More sample DFAs for testing
export const sampleDFAs: DFA[] = [
  // Ends with 'b'
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
  // Substring 'abb'
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
  // Even number of 'a's
  {
    regex: '(aa)*(bb*aa)*bb*',
    alphabet: ['a', 'b'],
    states: ['q0', 'q1'],
    start: 'q0',
    accept: ['q0'],
    transitions: {
      q0: { a: 'q1', b: 'q0' },
      q1: { a: 'q0', b: 'q1' }
    }
  }
];

export default dfaData;
