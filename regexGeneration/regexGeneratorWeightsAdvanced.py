import random
import re
import time
import math
import os
from tqdm import tqdm
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np

# Global pattern for 4+ consecutive letters (unchanged).
LETTER_PATTERN = re.compile(r"[a-zA-Z]{4,}")

class RegexParams:
    """
    Encapsulates regex generation/validation parameters that do not change
    across calls, such as the fixed alphabet, min/max lengths, and precomputed
    values like run_length, a compiled literal-run regex, and max_depth.
    """
    def __init__(self, alphabet, min_length, max_length):
        self.alphabet = alphabet
        self.min_length = min_length
        self.max_length = max_length
        # Precompute the required literal run length.
        self.run_length = math.ceil(min_length / 5) + 1
        # Precompile the regex for detecting a literal run.
        self.literal_run_pattern = re.compile(r"[a-zA-Z]{" + str(self.run_length) + r",}")
        # Compute maximum recursion depth from min_length.
        self.max_depth = max(3, math.ceil(math.log(min_length, 2)) + 1)

    def is_valid(self, regex):
        """
        Check if regex meets several criteria:
          - Length within min_length and max_length.
          - Contains between 1 and 2 Kleene stars (and no consecutive stars).
          - Contains no more than two union operators.
          - Does not contain triple parentheses.
          - Does not have 4+ consecutive letters.
          - Contains a literal run of sufficient length.
          - Contains at least one set of parentheses.
        """
        if not regex:
            return False
        L = len(regex)
        if L < self.min_length or L > self.max_length:
            return False

        # Count stars and union operators only once.
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
        
        # Use the precompiled literal run pattern.
        if not self.literal_run_pattern.search(regex):
            return False
        
        # Fast check for presence of at least one parenthesis.
        if "(" not in regex:
            return False
        
        return True

def generate_balanced_regex_with_weights(params, weights):
    """
    Generate a regex string using branch probabilities provided by weights.
    Uses precomputed parameters from params (which includes max_depth and alphabet).
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
    remaining = 1 - literal_prob
    return {
        'literal': literal_prob,
        'star': remaining * 0.5,
        'union': remaining * 0.3,
        'concat': remaining * 0.2
    }

# --- Worker Functions Updated to Use Precomputed Params ---
def worker_eval_weights(args):
    params, weights = args
    regex = generate_balanced_regex_with_weights(params, weights)
    return 1 if params.is_valid(regex) else 0

def worker_generate_regex(args):
    params, weights = args
    return generate_balanced_regex_with_weights(params, weights)

# --- Evaluation Functions ---
def evaluate_weights(params, weights, trials=1000, executor=None):
    """
    Run trials to generate a regex and count how many pass is_valid.
    """
    if executor is None:
        valid_count = 0
        for _ in tqdm(range(trials), desc="Evaluating weights", leave=False):
            regex = generate_balanced_regex_with_weights(params, weights)
            if params.is_valid(regex):
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
    Optimize the literal probability in [low, high] that maximizes a composite metric.
    Composite metric = (valid_count / trials) - (skips / target)
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

def generate_sample_regexes(params, weights, num_samples=15):
    print("\nGenerated Sample Regexes:\n")
    count = 0
    skips = 0
    while count < num_samples:
        regex = generate_balanced_regex_with_weights(params, weights)
        if params.is_valid(regex):
            print(regex)
            count += 1
        else:
            skips += 1

        if skips == 1000:
            print("1000 skips reached")
            break
    print(f"\nTotal skips: {skips}")

def run_optimizations(alphabet, min_length, max_length, trials, num_optimizations, precision, show_plot=True, num_samples=15):
    """
    Run a series of optimizations using provided parameters and return average weights.
    """
    # Precompute invariant parameters once.
    params = RegexParams(alphabet, min_length, max_length)
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

    print("\nAverage Weights After {} Runs:".format(num_optimizations))
    print(f"  literal: {avg_literal:.4f}")
    print(f"  star: {avg_star:.4f}")
    print(f"  union: {avg_union:.4f}")
    print(f"  concat: {avg_concat:.4f}")

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
        plt.title('Rolling Average of Weights Over {} Runs'.format(num_optimizations))
        plt.legend()
        plt.show()

    avg_weights = {
        'literal': avg_literal,
        'star': avg_star,
        'union': avg_union,
        'concat': avg_concat
    }
    generate_sample_regexes(params, avg_weights, num_samples=num_samples)
    return avg_weights

# --- Configurable Parameters ---
if __name__ == "__main__":
    CONFIG = {
        'alphabet': "abc",    # Example alphabet
        'min_length': 5,
        'max_length': 10,
        'trials': 1000,
        'num_optimizations': 1000,  # Number of optimization runs
        'precision': 0.001,         # Tolerance for binary search in optimization
        'show_plot': True,
        'num_samples': 30          # Number of sample regexes to generate at the end
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
    for k, v in final_weights.items():
        print(f"  {k}: {v:.4f}")