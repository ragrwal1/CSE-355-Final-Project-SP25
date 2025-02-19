Your idea, formally restated:

The proposed game for your theoretical computer science class project involves an interactive exploration of regular expressions and finite automata. The game mechanics are as follows:
	1.	Random Regex Generation: A semi-comprehensible regex is randomly generated.
	2.	Graphical NFA Representation: An NFA corresponding to the regex is generated, but the visualization lacks labels—only nodes and arrows are visible.
	3.	User Interaction via Typing: The user is placed at a starting node on the NFA. They have a text input box where they can type characters.
	4.	State Traversal Mechanism:
	•	As the user types, their character traverses the graphical NFA.
	•	If they enter a dead state (a state with no valid transitions for the given input), their input string is moved to a history sidebar and flagged red.
	•	If they reach an accepting state, they can choose to submit their string to the history sidebar with a green flag.
	•	If they do not reach an accept state and are still in a valid state, they can submit their string to the history sidebar with a grey flag.
	5.	Limited Attempts: The user has a finite number of attempts to experiment with strings and observe how they traverse the NFA.
	6.	Winning Condition: To win the level, the user must correctly determine the original regex that generated the NFA.

Feasibility Analysis:
	•	Technical Complexity: The project is feasible but involves multiple components:
	•	Regex generation and parsing
	•	Graphical NFA rendering
	•	Interactive state traversal
	•	Input handling and history tracking
	•	Tools & Implementation: The game could be implemented using JavaScript (React, D3.js for visualization) or Python (Flask with a front-end framework like Pygame or a web-based solution).
	•	Educational Value: This game effectively teaches regular expressions, finite automata, and state transitions interactively.

It is a solid concept, and with the right approach, it is definitely feasible. Would you like help planning out the technical stack or structuring the development process?