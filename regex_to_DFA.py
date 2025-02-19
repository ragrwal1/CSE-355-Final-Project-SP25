import random
import re
import time
import math
import os
from tqdm import tqdm
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np  # Added for rolling average calculation

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

# --- is_valid Function ---
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
    
    #no more than 1 kleene star in a row
    if "**" in regex:
        return False
    
    # no more than 2 total kleene star 
    if regex.count('*') > 2:
        return False
    
    #calculate round up of minlength/5
    floor = math.ceil(min_length/5) + 1
    # 
    #at least one run of length floor of literals
    if not re.search(r"[a-zA-Z]{"+str(floor)+",}", regex):
        return False
    
    #at least one set of parentheses
    if not re.search(r"\(", regex):
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

# --- Evaluation Functions ---
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
    The search stops when the range is less than 'tolerance' (precision).
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
        if is_valid(regex, min_length, max_length):
            print(regex)
            count += 1
        else:
            skips += 1

        if skips == 1000:
            print("1000 skips reached")
            break
    print(f"\nTotal skips: {skips}")

# --- Composite Runner Function ---
def run_optimizations(alphabet, min_length, max_length, trials, num_optimizations, precision, show_plot=True, num_samples=15):
    """
    Run a series of optimizations using provided parameters.
    Returns a dictionary of average weights.
    
    :param precision: Controls the tolerance (stopping precision) for the binary search in optimization.
    """
    # Lists to store weights over multiple optimization runs.
    literal_weights = []
    star_weights = []
    union_weights = []
    concat_weights = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        for _ in tqdm(range(num_optimizations), desc="Running optimizations"):
            optimal_literal = optimize_literal_weight(alphabet, min_length, max_length, tolerance=precision, trials=trials, executor=executor)
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
    
    if show_plot:
        # --- Plot the Rolling Averages of Weights ---
        runs = np.arange(1, num_optimizations + 1)
        rolling_literal = np.cumsum(literal_weights) / runs
        rolling_star = np.cumsum(star_weights) / runs
        rolling_union = np.cumsum(union_weights) / runs
        rolling_concat = np.cumsum(concat_weights) / runs
        
        plt.figure(figsize=(10, 6))
        plt.plot(runs, rolling_literal, label='Literal Rolling Avg')
        plt.plot(runs, rolling_star, label='Star Rolling Avg')
        plt.plot(runs, rolling_union, label='Union Rolling Avg')
        plt.plot(runs, rolling_concat, label='Concat Rolling Avg')
        plt.xlabel('Optimization Run')
        plt.ylabel('Rolling Average Weight')
        plt.title('Rolling Average of Weights Over {} Runs'.format(num_optimizations))
        plt.legend()
        plt.show()
    
    # Generate sample regexes using the average weights.
    avg_weights = {
        'literal': avg_literal,
        'star': avg_star,
        'union': avg_union,
        'concat': avg_concat
    }
    generate_sample_regexes(alphabet, min_length, max_length, avg_weights, num_samples=num_samples)
    
    return avg_weights

# --- Configurable Parameters (moved to bottom) ---
if __name__ == "__main__":
    # These parameters can be adjusted as needed.
    CONFIG = {
        'alphabet': "abcde",    # Example alphabet
        'min_length': 5,
        'max_length': 6,
        'trials': 500,
        'num_optimizations': 150,  # Number of optimization runs
        'precision': 0.01,         # Precision (tolerance) for binary search in optimization
        'show_plot': True,
        'num_samples': 15          # Number of sample regexes to generate at the end
    }
    
    final_weights = run_optimizations(
        alphabet=CONFIG['alphabet'],
        min_length=CONFIG['min_length'],
        max_length=CONFIG['max_length'],
        trials=CONFIG['trials'],
        num_optimizations=CONFIG['num_optimizations'],
        precision=CONFIG['precision'],
        show_plot=CONFIG['show_plot'],
        num_samples=CONFIG['num_samples']
    )

    print("\nFinal Average Weights:")
    print(final_weights)
    
    print("\nFinal Average Weights:")
    for k, v in final_weights.items():
        print(f"  {k}: {v:.4f}")