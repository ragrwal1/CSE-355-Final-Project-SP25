from regexGenerator import generate_balanced_regex
from regex_to_DFA import regex_to_dfa

def randomDFA(alphabet, min_len, max_len):

    regex_string = generate_balanced_regex(alphabet, min_len, max_len)
    dfa = regex_to_dfa(regex_string, alphabet)
    print(f"Generated regex: {regex_string}")
    print(f"Equivalent DFA: {dfa}")
    return dfa


if __name__ == "__main__":
    alphabet = "abcde"  # Example alphabet
    min_len = 15
    max_len = 20

    randomDFA(alphabet, min_len, max_len)
# Output:
# Generated regex: (a|b|c|d|e)*


