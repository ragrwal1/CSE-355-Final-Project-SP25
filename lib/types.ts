export interface DFA {
  regex: string
  alphabet: string[]
  states: string[]
  start: string
  accept: string[]
  transitions: Record<string, Record<string, string>>
}

export interface ChallengeSet {
  id: string
  regexSolutions: string[]
  dfas: DFA[]
  configs: {
    guessesPerProblem?: number
    // Other configs like time limits could be added
  }
  // Optional metadata
  name?: string
  description?: string
}

export interface ProblemStatus {
  solved: boolean
  attemptsUsed: number
}

export interface ChallengeProgress {
  challengeId: string
  problemStatuses: ProblemStatus[]
}
