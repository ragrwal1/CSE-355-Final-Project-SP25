import random
import math

# === 1. Regex Parser ===
class RegexParser:
    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0

    def parse(self):
        return self.parse_union()

    def parse_union(self):
        node = self.parse_concat()
        while self.pos < len(self.pattern) and self.pattern[self.pos] == '|':
            self.pos += 1
            right = self.parse_concat()
            node = ('union', node, right)
        return node

    def parse_concat(self):
        nodes = []
        while self.pos < len(self.pattern) and self.pattern[self.pos] not in ')|':
            nodes.append(self.parse_repeat())
        if not nodes:
            return ('epsilon',)
        node = nodes[0]
        for n in nodes[1:]:
            node = ('concat', node, n)
        return node

    def parse_repeat(self):
        node = self.parse_atom()
        while self.pos < len(self.pattern) and self.pattern[self.pos] == '*':
            self.pos += 1
            node = ('star', node)
        return node

    def parse_atom(self):
        if self.pattern[self.pos] == '(':
            self.pos += 1
            node = self.parse_union()
            if self.pos >= len(self.pattern) or self.pattern[self.pos] != ')':
                raise ValueError("Mismatched parentheses")
            self.pos += 1
            return node
        else:
            c = self.pattern[self.pos]
            self.pos += 1
            return ('lit', c)

# === 2. Thompson's Construction (Regex -> NFA) ===

state_id = 0
def new_state():
    global state_id
    s = state_id
    state_id += 1
    return s

def add_transition(trans, s, symbol, t):
    if s not in trans:
        trans[s] = {}
    if symbol not in trans[s]:
        trans[s][symbol] = set()
    trans[s][symbol].add(t)

def combine_transitions(t1, t2):
    result = {}
    for d in (t1, t2):
        for s, mapping in d.items():
            if s not in result:
                result[s] = {}
            for symbol, targets in mapping.items():
                if symbol not in result[s]:
                    result[s][symbol] = set()
                result[s][symbol] |= targets
    return result

def build_nfa(node):
    if node[0] == 'lit':
        s = new_state()
        t = new_state()
        trans = {}
        add_transition(trans, s, node[1], t)
        if t not in trans:
            trans[t] = {}
        return s, t, trans
    elif node[0] == 'epsilon':
        s = new_state()
        t = new_state()
        trans = {}
        add_transition(trans, s, None, t)
        if t not in trans:
            trans[t] = {}
        return s, t, trans
    elif node[0] == 'concat':
        s1, t1, trans1 = build_nfa(node[1])
        s2, t2, trans2 = build_nfa(node[2])
        add_transition(trans1, t1, None, s2)
        trans = combine_transitions(trans1, trans2)
        return s1, t2, trans
    elif node[0] == 'union':
        s = new_state()
        t = new_state()
        s1, t1, trans1 = build_nfa(node[1])
        s2, t2, trans2 = build_nfa(node[2])
        trans = {}
        add_transition(trans, s, None, s1)
        add_transition(trans, s, None, s2)
        add_transition(trans, t1, None, t)
        add_transition(trans, t2, None, t)
        trans = combine_transitions(trans, trans1)
        trans = combine_transitions(trans, trans2)
        if t not in trans:
            trans[t] = {}
        return s, t, trans
    elif node[0] == 'star':
        s = new_state()
        t = new_state()
        s1, t1, trans1 = build_nfa(node[1])
        trans = {}
        add_transition(trans, s, None, s1)
        add_transition(trans, s, None, t)
        add_transition(trans, t1, None, s1)
        add_transition(trans, t1, None, t)
        trans = combine_transitions(trans, trans1)
        if t not in trans:
            trans[t] = {}
        return s, t, trans
    else:
        raise ValueError("Unknown node type: " + node[0])

def epsilon_closure(trans, states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        if s in trans and None in trans[s]:
            for nxt in trans[s][None]:
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
    return closure

# === 3. Subset Construction (NFA -> DFA) ===
def nfa_to_dfa(nfa_start, nfa_accept, trans, alphabet):
    dfa_states = {}
    dfa_transitions = {}
    start_set = frozenset(epsilon_closure(trans, {nfa_start}))
    dfa_states[start_set] = 0
    start_state = 0
    unmarked = [start_set]
    next_state_id = 1
    dead_state = None

    while unmarked:
        current = unmarked.pop(0)
        current_id = dfa_states[current]
        dfa_transitions[current_id] = {}
        for symbol in alphabet:
            move_set = set()
            for s in current:
                if s in trans and symbol in trans[s]:
                    move_set |= trans[s][symbol]
            closure = epsilon_closure(trans, move_set)
            if not closure:
                if dead_state is None:
                    dead_state = next_state_id
                    next_state_id += 1
                    dfa_transitions[dead_state] = {}
                dfa_transitions[current_id][symbol] = dead_state
            else:
                closure_f = frozenset(closure)
                if closure_f not in dfa_states:
                    dfa_states[closure_f] = next_state_id
                    next_state_id += 1
                    unmarked.append(closure_f)
                dfa_transitions[current_id][symbol] = dfa_states[closure_f]
    return dfa_transitions, start_state, dfa_states, dead_state

def get_accept_states(dfa_states, nfa_accept):
    accept_states = set()
    for state_set, dfa_id in dfa_states.items():
        if nfa_accept in state_set:
            accept_states.add(dfa_id)
    return accept_states

# === 4. DFA Minimization using Partition Refinement ===
def minimize_dfa(dfa_transitions, start_state, accept_states, alphabet):
    # First, collect all states.
    states = set(dfa_transitions.keys())
    for s in list(dfa_transitions.keys()):
        for symbol in alphabet:
            states.add(dfa_transitions[s][symbol])
    # Ensure every state has a complete transition for each symbol.
    for s in states:
        if s not in dfa_transitions:
            dfa_transitions[s] = {}
        for symbol in alphabet:
            if symbol not in dfa_transitions[s]:
                dfa_transitions[s][symbol] = s  # self loop if undefined

    # Initial partition: accepting and non-accepting states.
    F = set(accept_states)
    nonF = states - F
    P = []
    if F:
        P.append(F)
    if nonF:
        P.append(nonF)
    W = list(P)

    # Refine partitions.
    while W:
        A = W.pop()
        for symbol in alphabet:
            X = {s for s in states if dfa_transitions[s][symbol] in A}
            new_P = []
            for Y in P:
                inter = Y & X
                diff = Y - X
                if inter and diff:
                    new_P.append(inter)
                    new_P.append(diff)
                    if Y in W:
                        W.remove(Y)
                        W.append(inter)
                        W.append(diff)
                    else:
                        if len(inter) <= len(diff):
                            W.append(inter)
                        else:
                            W.append(diff)
                else:
                    new_P.append(Y)
            P = new_P

    # Build new state mapping: each block becomes one state.
    new_state_map = {}
    for i, block in enumerate(P):
        for s in block:
            new_state_map[s] = i

    # Build new transitions.
    new_transitions = {}
    for i, block in enumerate(P):
        new_transitions[i] = {}
        rep = next(iter(block))
        for symbol in alphabet:
            new_transitions[i][symbol] = new_state_map[dfa_transitions[rep][symbol]]
            
    new_start_state = new_state_map[start_state]
    new_accept_states = {new_state_map[s] for s in F}
    return new_transitions, new_start_state, new_accept_states

# === 5. Regex-to-DFA Converter Function (with Minimization and Dead State Reporting) ===
def regex_to_dfa(regex, alphabet):
    """
    Converts a given regular expression into a minimized DFA.
    
    Returns a dictionary with the following keys:
      - "start_state": the starting state (an integer)
      - "accept_states": a list of accept state numbers
      - "dead_states": a list of dead state numbers (if any)
      - "transitions": a dict mapping each state to its transitions
      - "regex": the original regex string
    """
    parser = RegexParser(regex)
    tree = parser.parse()
    global state_id
    state_id = 0  # Reset state counter for a new conversion.
    nfa_start, nfa_accept, nfa_trans = build_nfa(tree)
    dfa_transitions, start_state, dfa_state_map, dead_state = nfa_to_dfa(nfa_start, nfa_accept, nfa_trans, alphabet)
    accept_states = get_accept_states(dfa_state_map, nfa_accept)
    
    # Ensure that if a dead state exists, its transitions are self loops.
    if dead_state is not None:
        for symbol in alphabet:
            dfa_transitions[dead_state][symbol] = dead_state

    # Minimize the DFA (this process will merge equivalent states)
    min_transitions, min_start_state, min_accept_states = minimize_dfa(dfa_transitions, start_state, accept_states, alphabet)
    
    # Identify dead state(s) in the minimized DFA.
    # A dead state is non-accepting and for every symbol transitions to itself.
    dead_states = [s for s, trans in min_transitions.items() 
                   if s not in min_accept_states and all(target == s for target in trans.values())]
    
    return {
        "start_state": min_start_state,
        "accept_states": list(min_accept_states),
        "dead_states": dead_states,
        "transitions": min_transitions,
        "regex": regex
    }

# === 6. Example Usage ===
if __name__ == "__main__":
    # Example regular expression and alphabet.
    regex_string = "(cc|a)c*"
    alphabet = "abcd"
    
    dfa = regex_to_dfa(regex_string, alphabet)

    # Print the minimized DFA in the required format.
    print("dfa = {")
    print(f"    \"start_state\": {dfa['start_state']},")
    print(f"    \"accept_states\": {dfa['accept_states']},")
    print(f"    \"dead_states\": {dfa['dead_states']},")
    print("    \"transitions\": {")
    for state, trans in sorted(dfa["transitions"].items()):
        print(f"        {state}: {trans},")
    print("    },")
    print(f"    \"regex\": \"{dfa['regex']}\"")
    print("}")