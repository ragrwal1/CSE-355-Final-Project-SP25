#!/usr/bin/env python3
"""
Module: regex_module.py

This module provides functionality for generating regular expressions (regexes)
using optimized weighted probabilities. An orchestrator can supply a configuration
dictionary (containing keys such as 'alphabet', 'min_length', 'max_length', etc.).

The orchestrator workflow is as follows:
  1. Call optimize_weights_from_config(config) to obtain the optimal weights.
     Weight optimization now uses a dynamic convergence criterion based on a
     stability_threshold parameter. Internally, the original trial count, number of
     optimization iterations, and number of sample regexes are used as starting values,
     but extra runs are avoided if the rolling average (and its derivative) has stabilized.
  2. Use generate_regex(config, weights) (or generate_regexes) to generate one or more
     valid regex strings based on the provided configuration and optimized weights.

All underlying math and logic remain the same.
"""

import random
import re
import time
import math
import os
from tqdm import tqdm
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
import sys
import io



# -----------------------------------------------------------------------------
# Global Pattern for 4+ consecutive letters
# -----------------------------------------------------------------------------

LETTER_PATTERN = re.compile(r"[a-zA-Z]{4,}")

# -----------------------------------------------------------------------------
# Global Helper Function: is_valid
# -----------------------------------------------------------------------------

# Precompile the union group regex once.
UNION_GROUP_RE = re.compile(r'\(([^()]*\|[^()]*)\)')

def is_valid(regex: str, params) -> bool:
    """
    Validate a regex string based on criteria defined by params.

    Checks:
      - The regex is not empty and its length is between params.min_length and params.max_length.
      - It contains 1 to 2 '*' characters (and they are not consecutive).
      - It contains no more than two '|' characters.
      - It does not contain triple consecutive '(' or ')' or "**".
      - It does not contain 4+ consecutive letters (using LETTER_PATTERN).
      - It contains a literal run (using params.literal_run_pattern).
      - It contains at least one '('.
      - It does NOT contain a union group (e.g. "(aaa|aaa)") where both sides are the same repeated literal.
    """
    if not regex:
        return False

    L = len(regex)
    if L < params.min_length or L > params.max_length:
        return False

    # Use one pass over the string to count characters and check for disallowed sequences.
    star_count = 0
    pipe_count = 0
    has_paren = False
    prev1 = prev2 = ''
    for c in regex:
        # Count stars and check for consecutive '*' ("**")
        if c == '*':
            star_count += 1
            if prev1 == '*':
                return False
        # Count union operators.
        elif c == '|':
            pipe_count += 1
        # Check for triple consecutive '(' or ')'
        if c == '(':
            has_paren = True
            if prev1 == '(' and prev2 == '(':
                return False
        if c == ')':
            if prev1 == ')' and prev2 == ')':
                return False
        prev2, prev1 = prev1, c

    if star_count not in (1, 2) or pipe_count > 2 or not has_paren:
        return False

    # Additional regex pattern checks.
    if not params.literal_run_pattern.search(regex):
        return False
    if LETTER_PATTERN.search(regex):
        return False

    # Check for union groups of the form (X|Y) where X and Y are each only a repeated literal.
    for m in UNION_GROUP_RE.finditer(regex):
        left, right = m.group(1).split('|', 1)
        if (left and right and 
            left == left[0] * len(left) and 
            right == right[0] * len(right) and 
            left[0] == right[0]):
            return False

    return True

# -----------------------------------------------------------------------------
# Class: RegexParams
# -----------------------------------------------------------------------------

class RegexParams:
    """
    Encapsulates regex generation parameters.
    """
    def __init__(self, alphabet, min_length, max_length):
        self.alphabet = alphabet
        self.min_length = min_length
        self.max_length = max_length
        # Precompute the required literal run length.
        self.run_length = math.ceil(min_length / 5) + 1
        # Precompile the regex for detecting a literal run.
        self.literal_run_pattern = re.compile(r"[a-zA-Z]{" + str(self.run_length) + r",}")
        # Compute maximum recursion depth.
        self.max_depth = max(3, math.ceil(math.log(min_length, 2)) + 1)

# -----------------------------------------------------------------------------
# Regex Generation Functions
# -----------------------------------------------------------------------------

def generate_balanced_regex_with_weights(params, weights):
    """
    Generate a regex string using branch probabilities provided by weights.
    """
    # Precompute cumulative thresholds.
    literal_threshold = weights['literal']
    star_threshold = literal_threshold + weights['star']
    union_threshold = star_threshold + weights['union']
    
    def gen_regex(depth=0):
        if depth >= params.max_depth:
            return random.choice(params.alphabet)
        r = random.random()
        if r < literal_threshold:
            return random.choice(params.alphabet)
        elif r < star_threshold:
            subexpr = gen_regex(depth + 1) if random.random() > 0.7 else random.choice(params.alphabet)
            return f"{subexpr}*"
        elif r < union_threshold:
            left = gen_regex(depth + 1) if random.random() > 0.5 else random.choice(params.alphabet)
            right = gen_regex(depth + 1) if random.random() > 0.5 else random.choice(params.alphabet)
            return f"({left}|{right})"
        else:
            return gen_regex(depth + 1) + gen_regex(depth + 1)
    
    return gen_regex(0)


def blackbox(func, *args, **kwargs):
    """Runs the given function, suppressing all print statements, and returns the function's output."""
    original_stdout = sys.stdout  # Save the original stdout
    sys.stdout = io.StringIO()  # Redirect stdout to suppress prints
    
    try:
        result = func(*args, **kwargs)  # Execute the function
    finally:
        sys.stdout = original_stdout  # Restore stdout
    
    return result

def get_weights(literal_prob):
    """
    Calculate and return a dictionary of weights for regex components.
    """
    remaining = 1 - literal_prob
    return {
        'literal': literal_prob,
        'star': remaining * 0.5,
        'union': remaining * 0.3,
        'concat': remaining * 0.2
    }

# -----------------------------------------------------------------------------
# Worker Functions (for concurrent evaluation)
# -----------------------------------------------------------------------------

def worker_eval_weights(args):
    params, weights = args
    regex = generate_balanced_regex_with_weights(params, weights)
    return 1 if is_valid(regex, params) else 0

def worker_generate_regex(args):
    params, weights = args
    return generate_balanced_regex_with_weights(params, weights)

def checking_averages():
    # Example usage of the optimization functions with moving averages.
    CONFIG = {
        'alphabet': "abcde",
        'min_length': 5,
        'max_length': 10,
        'precision': 0.01,
        'show_plot': False,
        'stability_threshold': 0.001
    }

    params = RegexParams(CONFIG['alphabet'], CONFIG['min_length'], CONFIG['max_length'])
    trials = 1000
    optimal_literals = []

    for _ in tqdm(range(trials), desc="Optimization Runs"):
        optimal_literal = blackbox(optimize_literal_weight, params, tolerance=CONFIG['precision'], trials=500)
        optimal_literals.append(optimal_literal)

    # Compute moving averages (5-run and 10-run)
    runs = np.arange(1, len(optimal_literals) + 1)
    moving_avg_5 = np.convolve(optimal_literals, np.ones(5) / 5, mode='valid')
    moving_avg_10 = np.convolve(optimal_literals, np.ones(10) / 10, mode='valid')

    # Plot results

    #print min max and average at the end
    print("Minimum:", min(optimal_literals))
    print("Maximum:", max(optimal_literals))
    print("Average:", sum(optimal_literals) / len(optimal_literals))

    #print other summary stats
    print("Standard Deviation:", np.std(optimal_literals))
    print("Variance:", np.var(optimal_literals))

    plt.figure(figsize=(12, 6))
    plt.plot(runs, optimal_literals, label='Raw Optimization Values', alpha=0.5)
    plt.plot(runs[4:], moving_avg_5, label='5-Run Moving Average', linestyle='--')
    plt.plot(runs[9:], moving_avg_10, label='10-Run Moving Average', linestyle='--')

    plt.xlabel('Run Number')
    plt.ylabel('Optimized Literal Weight')
    plt.title('Optimization Runs and Moving Averages')
    plt.legend()
    plt.show()

    print("Optimization runs completed.")

# -----------------------------------------------------------------------------
# Evaluation and Optimization Functions
# -----------------------------------------------------------------------------

def evaluate_weights(params, weights, trials=1000, executor=None):
    """
    Run trials to generate regexes and count how many pass the validation check.
    """
    if executor is None:
        valid_count = 0
        for _ in tqdm(range(trials), desc="Evaluating weights", leave=False):
            regex = generate_balanced_regex_with_weights(params, weights)
            if is_valid(regex, params):
                valid_count += 1
        return valid_count
    else:
        args_list = [(params, weights)] * trials
        results = list(executor.map(worker_eval_weights, args_list, chunksize=max(1, trials // 10)))
        return sum(results)

def evaluate_skip_metric(params, weights, target=100, executor=None, batch_size=200):
    """
    Generate regexes until 'target' regexes meeting min_length are produced.
    Returns the number of extra attempts (skips) required.
    """
    count = 0
    attempts = 0
    if executor is None:
        while count < target:
            regex = generate_balanced_regex_with_weights(params, weights)
            attempts += 1
            if len(regex) >= params.min_length:
                count += 1
    else:
        while count < target:
            args_list = [(params, weights)] * batch_size
            regexes = list(executor.map(worker_generate_regex, args_list, chunksize=max(1, batch_size // 4)))
            for regex in regexes:
                attempts += 1
                if len(regex) >= params.min_length:
                    count += 1
                    if count >= target:
                        break
    return attempts - target

def optimize_literal_weight(params, low=0.1, high=0.9, tolerance=0.01, delta=0.01, trials=1000, executor=None):
    """
    Optimize the literal probability that maximizes a composite metric.
    Composite metric = (valid_fraction) - (skip_ratio)
    """
    target = 100
    start_time = time.time()
    iteration = 0

    def composite_metric(x):
        weights = get_weights(x)
        valid_fraction = evaluate_weights(params, weights, trials, executor=executor) / trials
        skip_ratio = evaluate_skip_metric(params, weights, target, executor=executor) / target
        return valid_fraction - skip_ratio

    while high - low > tolerance:
        iteration += 1
        mid = (low + high) / 2
        cm_plus = composite_metric(mid + delta)
        cm_minus = composite_metric(mid - delta)
        derivative = (cm_plus - cm_minus) / (2 * delta)
        cm_mid = composite_metric(mid)
        print(f"Iteration {iteration}: x = {mid:.4f}, composite = {cm_mid:.4f}, derivative = {derivative:.4f}")
        if derivative > 0:
            low = mid
        else:
            high = mid

    optimal_x = (low + high) / 2
    total_time = time.time() - start_time
    print(f"\nOptimization completed in {total_time:.2f} seconds. Optimal literal weight: {optimal_x:.4f}")
    return optimal_x

# -----------------------------------------------------------------------------
# Optimization from Config (using a stability threshold)
# -----------------------------------------------------------------------------

def optimize_weights_from_config(config: dict) -> dict:
    """
    Given a configuration dictionary, optimize the literal probability and return
    the corresponding weights for regex components.

    Instead of fixed parameters for trials, optimization iterations, and sample
    generation, we now use a single stability_threshold parameter. The process
    begins with hard-coded values (initial_trials, max_iterations, and initial_num_samples)
    and dynamically runs additional optimization iterations until the rolling average
    of the optimal literal weight stabilizes (i.e. the difference among the last few
    iterations is less than stability_threshold).
    """
    params = RegexParams(config['alphabet'], config['min_length'], config['max_length'])
    
    # Hard-coded starting parameters
    initial_trials = 1000          # for each binary search in optimize_literal_weight
    max_iterations = 40            # safety maximum number of optimization iterations
    initial_num_samples = 15       # for sample regex generation (if desired)
    precision = config.get('precision', 0.001)
    stability_threshold = config.get('stability_threshold', 0.01)
    show_plot = config.get('show_plot', False)
    
    optimal_literals = []
    iteration = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            iteration += 1
            optimal_literal = optimize_literal_weight(params, tolerance=precision,
                                                      trials=initial_trials, executor=executor)
            optimal_literals.append(optimal_literal)
            print(f"Outer Iteration {iteration}: optimal_literal = {optimal_literal:.4f}")
            # Once we have a window of the last 5 runs, check for stability.
            if iteration >= 5:
                window = optimal_literals[-5:]
                if max(window) - min(window) < stability_threshold:
                    print("Stability threshold reached. Stopping further optimization runs.")
                    break
            if iteration >= max_iterations:
                print("Maximum iterations reached. Stopping further optimization runs.")
                break

    avg_literal = sum(optimal_literals) / len(optimal_literals)
    weights = get_weights(avg_literal)

    if show_plot:
        runs = np.arange(1, len(optimal_literals) + 1)
        rolling_avg = np.cumsum(optimal_literals) / runs

        plt.figure(figsize=(10, 6))
        plt.plot(runs, rolling_avg, label='Literal Weight Rolling Avg')
        plt.xlabel('Optimization Run')
        plt.ylabel('Rolling Average Optimal Literal Weight')
        plt.title(f'Rolling Average over {len(optimal_literals)} Runs')
        plt.legend()
        plt.show()

        # Generate sample regexes for visualization
        generate_sample_regexes(params, weights, num_samples=initial_num_samples)

    return weights

# -----------------------------------------------------------------------------
# Orchestrator Interface Functions
# -----------------------------------------------------------------------------

def generate_regex(config: dict, weights: dict) -> str:
    """
    Generate a single valid regex string using the provided configuration and weights.
    """
    params = RegexParams(config['alphabet'], config['min_length'], config['max_length'])
    while True:
        regex = generate_balanced_regex_with_weights(params, weights)
        if is_valid(regex, params):
            return regex
        
def generate_regexes(config: dict, weights: dict, count=1):
    """
    Generate multiple valid regex strings.
    """
    return [generate_regex(config, weights) for _ in range(count)]


def generate_sample_regexes(params, weights, num_samples=15):
    """
    Generate and print sample regexes that pass the validation check.
    """
    print("\nGenerated Sample Regexes:\n")
    count = 0
    skips = 0
    while count < num_samples:
        regex = generate_balanced_regex_with_weights(params, weights)
        if is_valid(regex, params):
            print(regex)
            count += 1
        else:
            skips += 1

        if skips == 1000:
            print("1000 skips reached")
            break
    print(f"\nTotal skips: {skips}")

# -----------------------------------------------------------------------------
# Main Execution (Example usage as a standalone script)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    CONFIG = {
        'alphabet': "abcd",         # Example alphabet
        'min_length': 5,
        'max_length': 7,
        'precision': 0.075,         # Tolerance for binary search in optimization
        'show_plot': False,         # Whether to show the plot of rolling averages
        'stability_threshold': 0.1  # New parameter: threshold for determining stability
    }
    
    # Orchestrator Step 1: Optimize weights based on the config.
    optimized_weights = optimize_weights_from_config(CONFIG)
    print("Optimized Weights:", optimized_weights)


    #AI Look here
    #add 1000 runs of weight optimization here and chart the results, and moving averages for each so total 8 lines on one chart.
    
    
    # Orchestrator Step 2: Generate a single regex.
    regex = generate_regex(CONFIG, optimized_weights)
    print("Generated Regex:", regex)
    
    # Orchestrator Step 3 (Optional): Generate multiple regexes.
    regexes = generate_regexes(CONFIG, optimized_weights, count=5)
    print("Generated Regexes:")
    for r in regexes:
        print(r)

    checking_averages()