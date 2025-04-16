export interface DFA {
  regex: string
  alphabet: string[]
  states: string[]
  start: string
  accept: string[]
  transitions: Record<string, Record<string, string>>
}
