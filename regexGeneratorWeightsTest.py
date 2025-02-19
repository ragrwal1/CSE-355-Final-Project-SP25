import random
import re
import time
import math
from tqdm import tqdm

# --- Generation Code with Weights (Length-Aware) ---

def generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights, max_depth=None):
    """
    Generate a regex string using branch probabilities provided by `weights`.
    The generator now uses the min_length to set an appropriate recursion depth
    so that fewer generated regexes are too short.
    
    weights is a dict with keys:
       - 'literal'
       - 'star'
       - 'union'
       - 'concat'
    that sum to 1.
    """
    # Compute a recommended max_depth if not provided.
    if max_depth is None:
        # If you need at least min_length characters and each concatenation roughly doubles
        # the length (base case returns 1 literal), then a logarithmic depth can help.
        max_depth = max(3, math.ceil(math.log(min_length, 2)) + 1)
    
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
            # When possible, try to use a subexpression that is not just a literal
            subexpr = gen_regex(depth + 1) if random.random() > 0.7 else random.choice(alphabet)
            return f"{subexpr}*"
        elif r < weights['literal'] + weights['star'] + weights['union']:
            # Union branch
            left = gen_regex(depth + 1) if random.random() > 0.5 else random.choice(alphabet)
            right = gen_regex(depth + 1) if random.random() > 0.5 else random.choice(alphabet)
            return f"({left}|{right})"
        else:
            # Concatenation branch
            return gen_regex(depth + 1) + gen_regex(depth + 1)
    
    return gen_regex(0)

# --- is_valid Function (unchanged) ---

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

# --- Evaluation Functions ---

def evaluate_weights(weights, alphabet, min_length, max_length, trials=1000):
    """
    Run `trials` attempts to generate a regex and return the number of regexes that are valid
    (i.e. that pass the is_valid test).
    """
    valid_count = 0
    for _ in tqdm(range(trials), desc="Evaluating weights", leave=False):
        regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
        if is_valid(regex, min_length, max_length):
            valid_count += 1
    return valid_count

def evaluate_skip_metric(weights, alphabet, min_length, max_length, target=100):
    """
    Generate regexes until we have produced `target` regexes that meet the min_length requirement.
    Returns the number of extra attempts (skips) required beyond the target.
    """
    count = 0
    attempts = 0
    while count < target:
        regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
        attempts += 1
        if len(regex) >= min_length:
            count += 1
    skips = attempts - target
    return skips

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

# --- Composite Optimization Function ---

def optimize_literal_weight(alphabet, min_length, max_length, low=0.1, high=0.9, tolerance=0.01, delta=0.01, trials=1000):
    """
    Optimize the literal probability (x) in [low, high] that maximizes a composite metric.
    
    The composite metric combines:
      - The fraction of valid regexes generated (using the unchanged is_valid function), and
      - The efficiency in generating regexes that meet the min_length (fewer skips is better).
    
    Composite metric = (valid_count / trials) - (skips / target)
    where target is fixed at 100.
    
    Uses finite-difference derivative estimation and binary search.
    """
    target = 100  # for the skip metric

    def composite_metric(x):
        weights = get_weights(x)
        valid_fraction = evaluate_weights(weights, alphabet, min_length, max_length, trials) / trials
        skip_ratio = evaluate_skip_metric(weights, alphabet, min_length, max_length, target) / target
        return valid_fraction - skip_ratio

    start_time = time.time()
    iteration = 0
    while high - low > tolerance:
        iteration += 1
        mid = (low + high) / 2

        # Evaluate composite metric at mid ± delta
        cm_plus = composite_metric(mid + delta)
        cm_minus = composite_metric(mid - delta)
        derivative = (cm_plus - cm_minus) / (2 * delta)
        
        # For debugging, also get the individual metrics at mid:
        weights_mid = get_weights(mid)
        valid_mid = evaluate_weights(weights_mid, alphabet, min_length, max_length, trials)
        skips_mid = evaluate_skip_metric(weights_mid, alphabet, min_length, max_length, target)
        print(f"Iteration {iteration}: x = {mid:.4f}, valid = {valid_mid}/{trials}, skips = {skips_mid}, composite = {composite_metric(mid):.4f}, derivative = {derivative:.4f}")

        # Adjust search range based on derivative sign
        if derivative > 0:
            # Composite metric is increasing: optimum is to the right.
            low = mid
        else:
            # Composite metric is decreasing: optimum is to the left.
            high = mid

    optimal_x = (low + high) / 2
    total_time = time.time() - start_time
    print(f"\nOptimization completed in {total_time:.2f} seconds. Optimal literal weight: {optimal_x:.4f}")
    return optimal_x

# --- Generate Sample Regexes Using Best Weights ---

def generate_sample_regexes(alphabet, min_length, max_length, weights, num_samples=15):
    """
    Generate and print `num_samples` regex strings using the optimal weights.
    Only regexes with length >= min_length are printed.
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

    import matplotlib.pyplot as plt

    # Initialize lists to store weights
    literal_weights = []
    star_weights = []
    union_weights = []
    concat_weights = []

    # Run the optimization 1000 times
    for _ in tqdm(range(50), desc="Running optimizations"):
        optimal_literal = optimize_literal_weight(alphabet, min_length, max_length, trials=trials)
        optimal_weights = get_weights(optimal_literal)
        
        # Store the weights
        literal_weights.append(optimal_weights['literal'])
        star_weights.append(optimal_weights['star'])
        union_weights.append(optimal_weights['union'])
        concat_weights.append(optimal_weights['concat'])

    # Calculate averages
    avg_literal = sum(literal_weights) / len(literal_weights)
    avg_star = sum(star_weights) / len(star_weights)
    avg_union = sum(union_weights) / len(union_weights)
    avg_concat = sum(concat_weights) / len(concat_weights)

    print("\nAverage Weights After 1000 Runs:")
    print(f"  literal: {avg_literal:.4f}")
    print(f"  star: {avg_star:.4f}")
    print(f"  union: {avg_union:.4f}")
    print(f"  concat: {avg_concat:.4f}")

    # Plot the weights
    plt.figure(figsize=(10, 6))
    plt.plot(literal_weights, label='Literal')
    plt.plot(star_weights, label='Star')
    plt.plot(union_weights, label='Union')
    plt.plot(concat_weights, label='Concat')
    plt.xlabel('Run')
    plt.ylabel('Weight')
    plt.title('Weights Over 1000 Runs')
    plt.legend()
    plt.show()

    # Generate sample regexes using the average weights
    avg_weights = {
        'literal': avg_literal,
        'star': avg_star,
        'union': avg_union,
        'concat': avg_concat
    }

    generate_sample_regexes(alphabet, min_length, max_length, avg_weights)
    