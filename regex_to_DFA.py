import pprint

# === AST Node Classes ===
class Literal:
    def __init__(self, char):
        self.char = char
    def __repr__(self):
        return f"Literal({self.char})"

class Concat:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Concat({self.left}, {self.right})"

class Union:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Union({self.left}, {self.right})"

class Star:
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"Star({self.expr})"

# === A Simple Recursive-Descent Parser ===
#
# Our regexes are “balanced” and use the following grammar:
#
#    expr   := term { term }        # concatenation is implicit
#    term   := factor [ "*" ]
#    factor := literal | "(" expr [ "|" expr ] ")"
#
# (Note that unions are always written with parentheses.)
class RegexParser:
    def __init__(self, pattern):
        self.p = pattern
        self.i = 0

    def parse(self):
        return self.parse_expr()

    def parse_expr(self):
        expr = self.parse_term()
        # Concatenation: while the next character is not a ) or |, keep reading factors.
        while self.i < len(self.p) and self.p[self.i] not in ')|':
            expr = Concat(expr, self.parse_term())
        return expr

    def parse_term(self):
        atom = self.parse_factor()
        # Handle postfix Kleene star.
        while self.i < len(self.p) and self.p[self.i] == '*':
            self.i += 1
            atom = Star(atom)
        return atom

    def parse_factor(self):
        if self.p[self.i] == '(':
            self.i += 1  # consume '('
            expr = self.parse_expr()
            # If a union operator is present, parse the second branch.
            if self.i < len(self.p) and self.p[self.i] == '|':
                self.i += 1  # consume '|'
                right = self.parse_expr()
                expr = Union(expr, right)
            if self.i >= len(self.p) or self.p[self.i] != ')':
                raise Exception("Unmatched parenthesis")
            self.i += 1  # consume ')'
            return expr
        else:
            # Literal character
            c = self.p[self.i]
            self.i += 1
            return Literal(c)

# === Thompson’s Construction: Regex AST -> NFA ===
#
# We represent an NFA as a tuple (start, accept, transitions) where:
#   - states are integers,
#   - transitions is a dict mapping state -> list of (symbol, next_state) pairs,
#   - epsilon-transitions use symbol None.
def new_state(counter):
    s = counter[0]
    counter[0] += 1
    return s

def regex_to_nfa(ast, counter):
    if isinstance(ast, Literal):
        s = new_state(counter)
        e = new_state(counter)
        transitions = {s: [(ast.char, e)], e: []}
        return s, e, transitions

    elif isinstance(ast, Concat):
        s1, e1, t1 = regex_to_nfa(ast.left, counter)
        s2, e2, t2 = regex_to_nfa(ast.right, counter)
        # Add an epsilon from the left accept state to the right start state.
        t1[e1] = t1.get(e1, []) + [(None, s2)]
        # Merge t1 and t2:
        for state, trans in t2.items():
            t1[state] = t1.get(state, []) + trans
        return s1, e2, t1

    elif isinstance(ast, Union):
        s = new_state(counter)
        e = new_state(counter)
        s1, e1, t1 = regex_to_nfa(ast.left, counter)
        s2, e2, t2 = regex_to_nfa(ast.right, counter)
        transitions = {s: [(None, s1), (None, s2)]}
        # Merge transitions from both branches.
        for t in (t1, t2):
            for state, trans in t.items():
                transitions[state] = transitions.get(state, []) + trans
        transitions[e1] = transitions.get(e1, []) + [(None, e)]
        transitions[e2] = transitions.get(e2, []) + [(None, e)]
        if e not in transitions:
            transitions[e] = []
        return s, e, transitions

    elif isinstance(ast, Star):
        s = new_state(counter)
        e = new_state(counter)
        s1, e1, t1 = regex_to_nfa(ast.expr, counter)
        transitions = {s: [(None, s1), (None, e)]}
        for state, trans in t1.items():
            transitions[state] = trans
        transitions[e1] = transitions.get(e1, []) + [(None, s1), (None, e)]
        if e not in transitions:
            transitions[e] = []
        return s, e, transitions

    else:
        raise Exception("Unknown AST node")

# === NFA -> DFA Conversion (Subset Construction) ===

# Compute the epsilon closure of a set of NFA states.
def epsilon_closure(states, trans):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for symbol, ns in trans.get(s, []):
            if symbol is None and ns not in closure:
                closure.add(ns)
                stack.append(ns)
    return closure

# Given a set of states, return all states reachable by a given symbol.
def move(states, symbol, trans):
    result = set()
    for s in states:
        for sym, ns in trans.get(s, []):
            if sym == symbol:
                result.add(ns)
    return result

# Convert the NFA into a DFA. The DFA is returned as a dictionary
# mapping state numbers to a dictionary of transitions.
def nfa_to_dfa(nfa_start, nfa_accept, trans, alphabet):
    start = frozenset(epsilon_closure({nfa_start}, trans))
    dfa = {}
    mapping = {start: 0}  # maps frozenset of NFA states -> DFA state number
    unmarked = [start]
    dfa_state = 1
    while unmarked:
        current = unmarked.pop(0)
        dfa[mapping[current]] = {}
        for a in alphabet:
            target = frozenset(epsilon_closure(move(current, a, trans), trans))
            if not target:
                continue
            if target not in mapping:
                mapping[target] = dfa_state
                dfa_state += 1
                unmarked.append(target)
            dfa[mapping[current]][a] = mapping[target]
    accepts = {mapping[s] for s in mapping if nfa_accept in s}
    return dfa, mapping[start], accepts

# Find all states in the DFA that have no leaving transitions.
def find_dead_states(dfa):
    return {s for s, moves in dfa.items() if len(moves) == 0}

# === Main Function: Regex -> DFA ===
#
# Returns a 4-tuple: (dfa, dfa_start, accept_states, dead_states)
def regex_to_dfa(regex, alph=None):
    parser = RegexParser(regex)
    ast = parser.parse()
    counter = [0]
    nfa_start, nfa_accept, trans = regex_to_nfa(ast, counter)
    # If no alphabet is provided, extract it from the transitions.
    if alph is None:
        alph = set()
        for moves in trans.values():
            for sym, _ in moves:
                if sym is not None:
                    alph.add(sym)
        alph = sorted(list(alph))
    dfa, start, accepts = nfa_to_dfa(nfa_start, nfa_accept, trans, alph)
    dead = find_dead_states(dfa)
    return dfa, start, accepts, dead

# === Example Usage ===
#
# For example, given the regex generated by:
#    ((cd|b*)|c)
#
# a correct output is a DFA (here printed using pprint)
if __name__ == '__main__':
    regex = "((cd|b*)|c)"
    dfa, start, accepts, dead = regex_to_dfa(regex)
    print("dfa =")
    pprint.pprint(dfa)
    print("\n[Start state, Accept states, Dead states] =")
    print([start, accepts, dead])