#!/usr/bin/env python3
"""
Module: regex_module.py

This module provides functionality for generating regular expressions (regexes)
using optimized weighted probabilities. An orchestrator can supply a configuration
dictionary (containing keys such as 'alphabet', 'min_length', 'max_length',
'num_optimizations', etc.). 

The orchestrator workflow is as follows:
  1. Call optimize_weights_from_config(config) to obtain the optimal weights.
     If config contains 'num_optimizations' > 1, multiple optimization runs will
     be performed and the weights averaged.
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

# -----------------------------------------------------------------------------
# Global Pattern for 4+ consecutive letters
# -----------------------------------------------------------------------------

LETTER_PATTERN = re.compile(r"[a-zA-Z]{4,}")

# -----------------------------------------------------------------------------
# Global Helper Function: is_valid
# -----------------------------------------------------------------------------

def is_valid(regex: str, params) -> bool:
    """
    Validate a regex string based on criteria defined by params.

    Checks:
      - The regex is not empty.
      - Its length is between params.min_length and params.max_length.
      - It contains between 1 and 2 Kleene stars (and no consecutive stars).
      - It contains no more than two union operators.
      - It does not contain triple parentheses.
      - It does not have 4+ consecutive letters.
      - It contains a literal run of sufficient length (using params.literal_run_pattern).
      - It contains at least one set of parentheses.
    """
    if not regex:
        return False
    L = len(regex)
    if L < params.min_length or L > params.max_length:
        return False

    # Count stars and union operators.
    star_count = regex.count('*')
    if star_count < 1 or star_count > 2:
        return False
    if regex.count('|') > 2:
        return False

    # Check for triple parentheses or consecutive stars.
    if "(((" in regex or ")))" in regex or "**" in regex:
        return False

    # Check for 4+ consecutive letters.
    if LETTER_PATTERN.search(regex):
        return False

    # Check for the required literal run.
    if not params.literal_run_pattern.search(regex):
        return False

    # Fast check for the presence of at least one parenthesis.
    if "(" not in regex:
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
# Optimization from Config (with num_optimizations)
# -----------------------------------------------------------------------------

def optimize_weights_from_config(config: dict) -> dict:
    """
    Given a configuration dictionary, optimize the literal probability and return
    the corresponding weights for regex components.

    If 'num_optimizations' is provided in the config and is greater than 1,
    multiple optimization runs are performed and the weights are averaged.
    Optionally, a plot and sample regexes can be generated.
    """
    params = RegexParams(config['alphabet'], config['min_length'], config['max_length'])
    trials = config.get('trials', 1000)
    precision = config.get('precision', 0.001)
    num_optimizations = config.get('num_optimizations', 1)
    show_plot = config.get('show_plot', False)
    num_samples = config.get('num_samples', 15)
    
    if num_optimizations <= 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            optimal_literal = optimize_literal_weight(params, tolerance=precision, trials=trials, executor=executor)
        weights = get_weights(optimal_literal)
    else:
        literal_weights = []
        star_weights = []
        union_weights = []
        concat_weights = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            for _ in tqdm(range(num_optimizations), desc="Running optimizations"):
                optimal_literal = optimize_literal_weight(params, tolerance=precision, trials=trials, executor=executor)
                optimal_weights = get_weights(optimal_literal)
                literal_weights.append(optimal_weights['literal'])
                star_weights.append(optimal_weights['star'])
                union_weights.append(optimal_weights['union'])
                concat_weights.append(optimal_weights['concat'])
        avg_literal = sum(literal_weights) / len(literal_weights)
        avg_star = sum(star_weights) / len(star_weights)
        avg_union = sum(union_weights) / len(union_weights)
        avg_concat = sum(concat_weights) / len(concat_weights)
        weights = {
            'literal': avg_literal,
            'star': avg_star,
            'union': avg_union,
            'concat': avg_concat
        }
        if show_plot:
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
            plt.title(f'Rolling Average of Weights Over {num_optimizations} Runs')
            plt.legend()
            plt.show()
        
        # Optionally generate sample regexes:
        generate_sample_regexes(params, weights, num_samples=num_samples)
        
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
        'alphabet': "abc",         # Example alphabet
        'min_length': 5,
        'max_length': 10,
        'trials': 1000,            # Trials used during weight optimization
        'num_optimizations': 40,   # Number of optimization runs
        'precision': 0.05,        # Tolerance for binary search in optimization
        'show_plot': True,         # Whether to show the plot of rolling averages
        'num_samples': 30,         # Number of sample regexes to generate after optimization
        'literal_prob': 0.5         # Initial literal probability (can be overridden by optimization)
    }
    
    # Orchestrator Step 1: Optimize weights based on the config.
    optimized_weights = optimize_weights_from_config(CONFIG)
    print("Optimized Weights:", optimized_weights)
    
    # Orchestrator Step 2: Generate a single regex.
    regex = generate_regex(CONFIG, optimized_weights)
    print("Generated Regex:", regex)
    
    # Orchestrator Step 3 (Optional): Generate multiple regexes.
    regexes = generate_regexes(CONFIG, optimized_weights, count=5)
    print("Generated Regexes:")
    for r in regexes:
        print(r)