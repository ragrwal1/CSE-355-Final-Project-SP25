from regex_to_DFA import regex_to_dfa
from regexGenerator import optimize_weights_from_config, generate_regex

import json
import hashlib

# -----------------------------------------------------------------------------
# Configuration Dictionary for Regex Generation
# -----------------------------------------------------------------------------
CONFIG = {
        'alphabet': "abc",         # Example alphabet
        'min_length': 4,
        'max_length': 7,
        'precision': 0.01,         # Tolerance for binary search in optimization
        'show_plot': False,         # Whether to show the plot of rolling averages
        'stability_threshold': 0.001  # New parameter: threshold for determining stability
    }

# Global variables to cache the configuration hash and optimized weights
_cached_config_hash = None
_cached_weights = None

def get_config_hash(config):
    """
    Compute and return a hash of the configuration dictionary.
    """
    config_str = json.dumps(config, sort_keys=True)
    return hashlib.md5(config_str.encode('utf-8')).hexdigest()

def get_optimized_weights(config):
    """
    Retrieve optimized weights based on the provided config.
    Only perform weight optimization if the configuration has changed.
    """
    global _cached_config_hash, _cached_weights
    current_hash = get_config_hash(config)
    if _cached_config_hash != current_hash:
        _cached_weights = optimize_weights_from_config(config)
        _cached_config_hash = current_hash
    return _cached_weights

def randomDFA():
    """
    Generate a random DFA by:
      1. Optimizing regex generation weights (if config has changed).
      2. Generating a valid regex using the new regexGenerator.
      3. Converting the regex to a DFA using regex_to_dfa.
    """
    weights = get_optimized_weights(CONFIG)
    regex = generate_regex(CONFIG, weights)
    dfa = regex_to_dfa(regex, CONFIG['alphabet'])
    print(f"Generated regex: {regex}")
    print(f"Equivalent DFA: {dfa}")
    return dfa

if __name__ == "__main__":
    randomDFA()