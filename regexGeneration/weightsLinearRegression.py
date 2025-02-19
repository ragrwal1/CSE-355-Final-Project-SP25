import random
import re
import time
import math
import os
import concurrent.futures
from tqdm import tqdm
import numpy as np
from numba import njit, prange
from concurrent.futures import ThreadPoolExecutor

# Global pattern for 4+ consecutive letters.
LETTER_PATTERN = re.compile(r"[a-zA-Z]{4,}")

# --- Regex generation and validation ---

class RegexParams:
    def __init__(self, alphabet, min_length, max_length):
        self.alphabet = alphabet
        self.min_length = min_length
        self.max_length = max_length
        self.run_length = math.ceil(min_length / 5) + 1
        self.literal_run_pattern = re.compile(r"[a-zA-Z]{" + str(self.run_length) + r",}")
        self.max_depth = max(3, math.ceil(math.log(min_length, 2)) + 1)

    def is_valid(self, regex):
        if not regex:
            return False
        L = len(regex)
        if L < self.min_length or L > self.max_length:
            return False

        star_count = regex.count('*')
        if star_count < 1 or star_count > 2:
            return False
        if regex.count('|') > 2:
            return False

        if "(((" in regex or ")))" in regex or "**" in regex:
            return False

        if LETTER_PATTERN.search(regex):
            return False

        if not self.literal_run_pattern.search(regex):
            return False

        if "(" not in regex:
            return False

        return True

def generate_balanced_regex_with_weights(params, weights):
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

# --- Worker functions for parallel execution ---

def worker_eval_weights(args):
    params, weights = args
    regex = generate_balanced_regex_with_weights(params, weights)
    return 1 if params.is_valid(regex) else 0

def worker_generate_regex(args):
    params, weights = args
    return generate_balanced_regex_with_weights(params, weights)

# --- Evaluation and optimization functions (with prints removed) ---

def evaluate_weights(params, weights, trials=100, executor=None):
    if executor is None:
        valid_count = 0
        for _ in range(trials):
            regex = generate_balanced_regex_with_weights(params, weights)
            if params.is_valid(regex):
                valid_count += 1
        return valid_count
    else:
        args_list = [(params, weights)] * trials
        results = list(executor.map(worker_eval_weights, args_list, chunksize=max(1, trials // 10)))
        return sum(results)

def evaluate_skip_metric(params, weights, target=100, executor=None, batch_size=200):
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

def optimize_literal_weight(params, low=0.1, high=0.9, tolerance=0.01, delta=0.01, trials=100, executor=None):
    target = 100
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
        if derivative > 0:
            low = mid
        else:
            high = mid

    optimal_x = (low + high) / 2
    return optimal_x

def run_optimizations(alphabet, min_length, max_length, trials=100, num_optimizations=10):
    params = RegexParams(alphabet, min_length, max_length)
    literal_weights = []
    star_weights = []
    union_weights = []
    concat_weights = []
    for _ in range(num_optimizations):
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
            optimal_literal = optimize_literal_weight(params, trials=trials, executor=executor)
        optimal_weights = get_weights(optimal_literal)
        literal_weights.append(optimal_weights['literal'])
        star_weights.append(optimal_weights['star'])
        union_weights.append(optimal_weights['union'])
        concat_weights.append(optimal_weights['concat'])
    avg_literal = sum(literal_weights) / len(literal_weights)
    avg_star = sum(star_weights) / len(star_weights)
    avg_union = sum(union_weights) / len(union_weights)
    avg_concat = sum(concat_weights) / len(concat_weights)
    return {'literal': avg_literal, 'star': avg_star, 'union': avg_union, 'concat': avg_concat}

# --- Regression via njit ---

@njit
def compute_regression(X, y):
    # X: (n, p) and y: (n,)
    Xt = X.T
    XtX = np.dot(Xt, X)
    inv_XtX = np.linalg.inv(XtX)
    Xty = np.dot(Xt, y)
    beta = np.dot(inv_XtX, Xty)
    return beta

# --- Grid search wrapper using threading ---

def process_configuration(alphabet, min_length, max_length):
    # Run the optimizations (with reduced trials and num_optimizations)
    weights = run_optimizations(alphabet, min_length, max_length, trials=100, num_optimizations=10)
    result = {
        'alphabet_size': len(alphabet),
        'min_length': min_length,
        'max_length': max_length,
        'literal': weights['literal'],
        'star': weights['star'],
        'union': weights['union'],
        'concat': weights['concat']
    }
    return result

def main():
    # Define grid: alphabets of length 2 to 5; min_length from 5 to 10; max_length = min_length + 5.
    grid = []
    for alphabet in ["ab", "abc", "abcd", "abcde"]:
        for min_length in range(5, 11):
            max_length = min_length + 5
            grid.append((alphabet, min_length, max_length))
    
    # Use a thread pool to process the 24 configurations concurrently.
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_configuration, *cfg): cfg for cfg in grid}
        for fut in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Grid progress"):
            res = fut.result()
            results.append(res)
    
    # Prepare regression data.
    n = len(results)
    X = np.zeros((n, 4))
    literal_y = np.zeros(n)
    star_y = np.zeros(n)
    union_y = np.zeros(n)
    concat_y = np.zeros(n)
    
    for i, rec in enumerate(results):
        # X: intercept, alphabet_size, min_length, max_length.
        X[i, 0] = 1
        X[i, 1] = rec['alphabet_size']
        X[i, 2] = rec['min_length']
        X[i, 3] = rec['max_length']
        literal_y[i] = rec['literal']
        star_y[i] = rec['star']
        union_y[i] = rec['union']
        concat_y[i] = rec['concat']
    
    # Compute regression coefficients for each weight.
    beta_literal = compute_regression(X, literal_y)
    beta_star = compute_regression(X, star_y)
    beta_union = compute_regression(X, union_y)
    beta_concat = compute_regression(X, concat_y)
    
    # Use the regression models to predict weights for the original configuration:
    # alphabet "abc" (size 3), min_length=5, max_length=10.
    X_new = np.array([1, 3, 5, 10])
    pred_literal = np.dot(beta_literal, X_new)
    pred_star = np.dot(beta_star, X_new)
    pred_union = np.dot(beta_union, X_new)
    pred_concat = np.dot(beta_concat, X_new)
    
    # Print regression coefficients and predictions.
    print("Regression Coefficients:")
    print("Literal weight model:", beta_literal)
    print("Star weight model:   ", beta_star)
    print("Union weight model:  ", beta_union)
    print("Concat weight model: ", beta_concat)
    print("\nPredicted weights for input (alphabet 'abc', min_length 5, max_length 10):")
    print("Literal:", pred_literal)
    print("Star:   ", pred_star)
    print("Union:  ", pred_union)
    print("Concat: ", pred_concat)

if __name__ == "__main__":
    main()