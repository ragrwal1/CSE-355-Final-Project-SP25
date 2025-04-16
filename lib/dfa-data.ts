import type { DFA } from "./types"

export const dfaData: DFA = {
  "regex": "a*(b|c)",
  "alphabet": [
    "a",
    "b",
    "c"
  ],
  "states": [
    "S0",
    "S1",
    "S2",
    "S3"
  ],
  "start": "S0",
  "accept": [
    "S1",
    "S3"
  ],
  "transitions": {
    "S0": {
      "c": "S1",
      "a": "S2",
      "b": "S3"
    },
    "S1": {},
    "S2": {
      "c": "S1",
      "a": "S2",
      "b": "S3"
    },
    "S3": {}
  }
}
