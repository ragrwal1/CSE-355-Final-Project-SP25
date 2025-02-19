import random
import re
import time
import math
import os
from tqdm import tqdm
import concurrent.futures
import matplotlib.pyplot as plt

# Precompile a pattern to detect 4+ consecutive letters.
LETTER_PATTERN = re.compile(r"[a-zA-Z]{4,}")

# --- Generation Code with Weights (Length-Aware) ---
def generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights, max_depth=None):
    """
    Generate a regex string using branch probabilities provided by `weights`.
    The recursion depth is chosen based on min_length to help generate longer regexes.
    """
    if max_depth is None:
        max_depth = max(3, math.ceil(math.log(min_length, 2)) + 1)
    
    def gen_regex(depth=0):
        if depth >= max_depth:
            return random.choice(alphabet)  # base case
        r = random.random()
        # Branch based on cumulative probability.
        if r < weights['literal']:
            return random.choice(alphabet)
        elif r < weights['literal'] + weights['star']:
            subexpr = gen_regex(depth + 1) if random.random() > 0.7 else random.choice(alphabet)
            return f"{subexpr}*"
        elif r < weights['literal'] + weights['star'] + weights['union']:
            left = gen_regex(depth + 1) if random.random() > 0.5 else random.choice(alphabet)
            right = gen_regex(depth + 1) if random.random() > 0.5 else random.choice(alphabet)
            return f"({left}|{right})"
        else:
            return gen_regex(depth + 1) + gen_regex(depth + 1)
    
    return gen_regex(0)

# --- is_valid Function (unchanged functionality, but precompiled pattern) ---
def is_valid(regex, min_length, max_length):
    """
    Check if regex meets the following:
      - Length within min_length and max_length.
      - Contains at least one Kleene star.
      - Contains no more than two union ('|') operators.
      - No triple parentheses.
      - Does not have 4+ consecutive letters.
    """
    if not regex:
        return False
    L = len(regex)
    if L < min_length or L > max_length:
        return False
    if regex.count('*') < 1:
        return False
    if regex.count('|') > 2:
        return False
    if "(((" in regex or ")))" in regex:
        return False
    if LETTER_PATTERN.search(regex):
        return False
    return True

# --- Weight Helper ---
def get_weights(literal_prob):
    remaining = 1 - literal_prob
    return {
        'literal': literal_prob,
        'star': remaining * 0.5,
        'union': remaining * 0.3,
        'concat': remaining * 0.2
    }

# --- Worker Functions for Parallelism ---
def worker_eval_weights(args):
    alphabet, min_length, max_length, weights = args
    regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
    return 1 if is_valid(regex, min_length, max_length) else 0

def worker_generate_regex(args):
    alphabet, min_length, max_length, weights = args
    return generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)

# --- Evaluation Functions (with optional parallel executor) ---
def evaluate_weights(weights, alphabet, min_length, max_length, trials=1000, executor=None):
    """
    Run trials to generate a regex and count how many pass is_valid.
    If an executor is provided, use it to parallelize the work.
    """
    if executor is None:
        valid_count = 0
        for _ in tqdm(range(trials), desc="Evaluating weights", leave=False):
            regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
            if is_valid(regex, min_length, max_length):
                valid_count += 1
        return valid_count
    else:
        args_list = [(alphabet, min_length, max_length, weights)] * trials
        results = list(executor.map(worker_eval_weights, args_list, chunksize=max(1, trials // 10)))
        return sum(results)

def evaluate_skip_metric(weights, alphabet, min_length, max_length, target=100, executor=None, batch_size=200):
    """
    Generate regexes until 'target' regexes meeting min_length are produced.
    Returns the number of extra attempts (skips) required.
    """
    count = 0
    attempts = 0
    if executor is None:
        while count < target:
            regex = generate_balanced_regex_with_weights(alphabet, min_length, max_length, weights)
            attempts += 1
            if len(regex) >= min_length:
                count += 1
    else:
        while count < target:
            args_list = [(alphabet, min_length, max_length, weights)] * batch_size
            regexes = list(executor.map(worker_generate_regex, args_list, chunksize=max(1, batch_size // 4)))
            for regex in regexes:
                attempts += 1
                if len(regex) >= min_length:
                    count += 1
                    if count >= target:
                        break
    return attempts - target

# --- Composite Optimization Function ---
def optimize_literal_weight(alphabet, min_length, max_length, low=0.1, high=0.9, tolerance=0.01, delta=0.01, trials=1000, executor=None):
    """
    Optimize the literal probability (x) in [low, high] that maximizes a composite metric.
    Composite metric = (valid_count / trials) - (skips / target)
    """
    target = 100
    start_time = time.time()
    iteration = 0

    def composite_metric(x):
        weights = get_weights(x)
        valid_fraction = evaluate_weights(weights, alphabet, min_length, max_length, trials, executor=executor) / trials
        skip_ratio = evaluate_skip_metric(weights, alphabet, min_length, max_length, target, executor=executor) / target
        return valid_fraction - skip_ratio

    while high - low > tolerance:
        iteration += 1
        mid = (low + high) / 2
        cm_plus = composite_metric(mid + delta)
        cm_minus = composite_metric(mid - delta)
        derivative = (cm_plus - cm_minus) / (2 * delta)
        cm_mid = composite_metric(mid)
        # Debug print (preserving functionality)
        print(f"Iteration {iteration}: x = {mid:.4f}, composite = {cm_mid:.4f}, derivative = {derivative:.4f}")
        if derivative > 0:
            low = mid
        else:
            high = mid

    optimal_x = (low + high) / 2
    total_time = time.time() - start_time
    print(f"\nOptimization completed in {total_time:.2f} seconds. Optimal literal weight: {optimal_x:.4f}")
    return optimal_x

# --- Generate Sample Regexes Using Best Weights ---
def generate_sample_regexes(alphabet, min_length, max_length, weights, num_samples=15):
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

    # Lists to store weights over multiple optimization runs.
    literal_weights = []
    star_weights = []
    union_weights = []
    concat_weights = []

    num_optimizations = 50  # (Originally 50 runs; change as needed)

    # Create a global process pool to parallelize evaluation functions.
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        for _ in tqdm(range(num_optimizations), desc="Running optimizations"):
            optimal_literal = optimize_literal_weight(alphabet, min_length, max_length, trials=trials, executor=executor)
            optimal_weights = get_weights(optimal_literal)
            literal_weights.append(optimal_weights['literal'])
            star_weights.append(optimal_weights['star'])
            union_weights.append(optimal_weights['union'])
            concat_weights.append(optimal_weights['concat'])

    # Calculate average weights.
    avg_literal = sum(literal_weights) / len(literal_weights)
    avg_star = sum(star_weights) / len(star_weights)
    avg_union = sum(union_weights) / len(union_weights)
    avg_concat = sum(concat_weights) / len(concat_weights)

    print("\nAverage Weights After {} Runs:".format(num_optimizations))
    print(f"  literal: {avg_literal:.4f}")
    print(f"  star: {avg_star:.4f}")
    print(f"  union: {avg_union:.4f}")
    print(f"  concat: {avg_concat:.4f}")

    # Plot the weights over the optimization runs.
    plt.figure(figsize=(10, 6))
    plt.plot(literal_weights, label='Literal')
    plt.plot(star_weights, label='Star')
    plt.plot(union_weights, label='Union')
    plt.plot(concat_weights, label='Concat')
    plt.xlabel('Run')
    plt.ylabel('Weight')
    plt.title('Weights Over {} Runs'.format(num_optimizations))
    plt.legend()
    plt.show()

    # Generate sample regexes using the average weights.
    avg_weights = {
        'literal': avg_literal,
        'star': avg_star,
        'union': avg_union,
        'concat': avg_concat
    }
    generate_sample_regexes(alphabet, min_length, max_length, avg_weights)