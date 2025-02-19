import random
import re
import time
from tqdm import tqdm

# --- Generation Code with Weights ---

def generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights, max_depth=3):
    """
    Generate a regex string using branch probabilities provided by `weights`.

    weights is a dict with keys:
       - 'literal'
       - 'star'
       - 'union'
       - 'concat'
    that sum to 1.
    """
    def gen_regex(depth=0):
        if depth >= max_depth:
            return random.choice(alphabet)  # base case: return a literal
        
        r = random.random()
        # Determine branch based on cumulative probability
        if r < weights['literal']:
            # Literal branch
            return random.choice(alphabet)
        elif r < weights['literal'] + weights['star']:
            # Kleene star branch
            subexpr = random.choice(alphabet) if random.random() < 0.7 else gen_regex(depth + 1)
            return f"{subexpr}*"
        elif r < weights['literal'] + weights['star'] + weights['union']:
            # Union branch
            left = random.choice(alphabet) if random.random() < 0.5 else gen_regex(depth + 1)
            right = random.choice(alphabet) if random.random() < 0.5 else gen_regex(depth + 1)
            return f"({left}|{right})"
        else:
            # Concatenation branch
            return gen_regex(depth + 1) + gen_regex(depth + 1)

    return gen_regex(0)

# --- is_valid Function (modifiable) ---

def is_valid(regex, min_length, max_length):
    """
    Check if the regex meets the constraints.
      - Length within min_length and max_length.
      - Contains at least one Kleene star.
      - Contains no more than two union ('|') operators.
      - Does not have triple parentheses.
      - Does not have 4+ consecutive letters.
    """
    if not regex:
        return False
    if len(regex) < min_length or len(regex) > max_length:
        return False
    if regex.count('*') < 1:
        return False
    if regex.count('|') > 2:
        return False
    if "(((" in regex or ")))" in regex:
        return False
    if re.search(r"[a-zA-Z]{4,}", regex):
        return False
    return True

# --- Evaluation Function ---

def evaluate_weights(weights, alphabet, min_length, max_length, trials=1000):
    """
    Run `trials` attempts to generate a regex and return the number of valid regexes.
    Progress is logged with tqdm.
    """
    valid_count = 0
    for _ in tqdm(range(trials), desc="Evaluating weights", leave=False):
        regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
        if is_valid(regex, min_length, max_length):
            valid_count += 1
    return valid_count

# --- Weight Helper ---

def get_weights(literal_prob):
    """
    Given a literal probability `literal_prob`, distribute the remaining probability among:
      - star: 50% of remaining,
      - union: 30% of remaining,
      - concat: 20% of remaining.
    This ensures all weights sum to 1.
    """
    remaining = 1 - literal_prob
    return {
        'literal': literal_prob,
        'star': remaining * 0.5,
        'union': remaining * 0.3,
        'concat': remaining * 0.2
    }

# --- Optimization Function ---

def optimize_literal_weight(alphabet, min_length, max_length, low=0.1, high=0.9, tolerance=0.01, delta=0.01, trials=1000):
    """
    Optimize the literal probability (x) in [low, high] that maximizes
    the number of valid regexes generated out of `trials` attempts.
    
    Uses finite-difference derivative estimation and binary search.
    """
    def f(x):
        weights = get_weights(x)
        return evaluate_weights(weights, alphabet, min_length, max_length, trials)

    start_time = time.time()
    iteration = 0
    while high - low > tolerance:
        iteration += 1
        mid = (low + high) / 2

        # Evaluate function at mid ± delta
        f_mid_plus = f(mid + delta)
        f_mid_minus = f(mid - delta)
        derivative = (f_mid_plus - f_mid_minus) / (2 * delta)
        
        # Log iteration details
        print(f"Iteration {iteration}: x = {mid:.4f}, f(mid+delta) = {f_mid_plus}, f(mid-delta) = {f_mid_minus}, derivative = {derivative:.2f}")

        # Adjust search range based on derivative sign
        if derivative > 0:
            # Increasing function: optimum is to the right.
            low = mid
        else:
            # Decreasing function: optimum is to the left.
            high = mid

    optimal_x = (low + high) / 2
    total_time = time.time() - start_time
    print(f"\nOptimization completed in {total_time:.2f} seconds. Optimal literal weight: {optimal_x:.4f}")
    return optimal_x

# --- Generate 15 Sample Regexes Using Best Weights ---

def generate_sample_regexes(alphabet, min_length, max_length, weights, num_samples=15):
    """
    Generate and print `num_samples` regex strings using the optimal weights.
    """
    print("\nGenerated Sample Regexes:\n")
    count = 0
    skips = 0
    while count < num_samples:
        regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
        if len(regex) >= min_length:
            print(regex)
            count += 1
        else:
            skips += 1
    print(f"\nTotal skips: {skips}")

# --- Main Runner ---

if __name__ == "__main__":
    alphabet = "abcde"   # Example alphabet
    min_length = 15
    max_length = 20
    trials = 1000

    print("Starting optimization to find the best literal weight...\n")
    optimal_literal = optimize_literal_weight(alphabet, min_length, max_length, trials=trials)
    optimal_weights = get_weights(optimal_literal)
    
    print("\nOptimal Weights Found:")
    for branch, weight in optimal_weights.items():
        print(f"  {branch}: {weight:.4f}")

    # Generate 15 sample regexes using the best weights
    generate_sample_regexes(alphabet, min_length, max_length, optimal_weights, num_samples=15)