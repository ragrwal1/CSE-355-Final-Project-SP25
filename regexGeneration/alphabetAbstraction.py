#most advanced weights abstraction to generate weights
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import numba
from numba import njit, int32, float64
from numba.typed import List

# =============================================================================
# NUMBA–Accelerated Helper: Weights (as a tuple)
# =============================================================================
@njit
def get_weights(literal_prob):
    # Returns a tuple: (literal, star, union, concat)
    remaining = 1.0 - literal_prob
    return (literal_prob, remaining * 0.5, remaining * 0.3, remaining * 0.2)

# =============================================================================
# NUMBA–Accelerated Token Generator
# =============================================================================
@njit
def gen_regex_tokens(num_literals, weights, max_depth, depth):
    """
    Recursively generate a token–sequence (as a numba.typed.List of int32)
    representing a regex, and the probability of having generated it.
    
    Grammar productions (with weights):
      R → literal
      R → ( R )*            [STAR production: apply a Kleene star to a subexpression]
      R → ( R | R )         [UNION production: left and right, each chosen via a 50/50 mix]
      R → R R               [Concatenation production]
    
    In our token encoding:
      - Literal tokens are in [0, num_literals–1].
      - STAR is coded as: num_literals
      - UNION is coded as: num_literals + 1
      - LPAR is coded as: num_literals + 2
      - RPAR is coded as: num_literals + 3
    """
    # Create an empty typed list for tokens.
    tokens = List.empty_list(numba.int32)
    
    # Define operator codes.
    STAR  = num_literals
    UNION = num_literals + 1
    LPAR  = num_literals + 2
    RPAR  = num_literals + 3

    # Unpack weight tuple.
    literal_weight = weights[0]
    star_weight    = weights[1]
    union_weight   = weights[2]
    concat_weight  = weights[3]
    
    # Base case: if maximum recursion depth is reached, produce a literal.
    if depth >= max_depth:
        literal = np.random.randint(0, num_literals)
        tokens.append(literal)
        return tokens, literal_weight / num_literals

    r = np.random.rand()
    cumulative_literal = literal_weight
    cumulative_star    = cumulative_literal + star_weight
    cumulative_union   = cumulative_star + union_weight
    # The remaining branch is concatenation.
    
    if r < cumulative_literal:
        # Literal production.
        literal = np.random.randint(0, num_literals)
        tokens.append(literal)
        return tokens, literal_weight / num_literals

    elif r < cumulative_star:
        # STAR production.
        # Decide between recursing (30% chance) or simply a literal (70% chance)
        r_star = np.random.rand()
        sub_tokens = List.empty_list(numba.int32)
        sub_prob = 0.0
        if r_star > 0.7:
            sub_tokens, sub_prob = gen_regex_tokens(num_literals, weights, max_depth, depth + 1)
            option_prob = 0.3 * sub_prob
        else:
            literal = np.random.randint(0, num_literals)
            sub_tokens.append(literal)
            option_prob = 0.7 * (1.0 / num_literals)
        # Concatenate subexpression tokens and then add STAR.
        for t in sub_tokens:
            tokens.append(t)
        tokens.append(STAR)
        return tokens, star_weight * option_prob

    elif r < cumulative_union:
        # UNION production.
        # Left side:
        r_left = np.random.rand()
        left_tokens = List.empty_list(numba.int32)
        left_prob = 0.0
        if r_left > 0.5:
            left_tokens, left_prob = gen_regex_tokens(num_literals, weights, max_depth, depth + 1)
            left_prob = 0.5 * left_prob
        else:
            literal = np.random.randint(0, num_literals)
            left_tokens.append(literal)
            left_prob = 0.5 * (1.0 / num_literals)
        # Right side:
        r_right = np.random.rand()
        right_tokens = List.empty_list(numba.int32)
        right_prob = 0.0
        if r_right > 0.5:
            right_tokens, right_prob = gen_regex_tokens(num_literals, weights, max_depth, depth + 1)
            right_prob = 0.5 * right_prob
        else:
            literal = np.random.randint(0, num_literals)
            right_tokens.append(literal)
            right_prob = 0.5 * (1.0 / num_literals)
        # Build token sequence: LPAR, left, UNION, right, RPAR.
        tokens.append(LPAR)
        for t in left_tokens:
            tokens.append(t)
        tokens.append(UNION)
        for t in right_tokens:
            tokens.append(t)
        tokens.append(RPAR)
        return tokens, union_weight * left_prob * right_prob

    else:
        # Concatenation production.
        first_tokens, first_prob = gen_regex_tokens(num_literals, weights, max_depth, depth + 1)
        second_tokens, second_prob = gen_regex_tokens(num_literals, weights, max_depth, depth + 1)
        for t in first_tokens:
            tokens.append(t)
        for t in second_tokens:
            tokens.append(t)
        return tokens, concat_weight * first_prob * second_prob

# =============================================================================
# NUMBA–Accelerated Validity Checker (operating on token sequences)
# =============================================================================
@njit
def is_valid_tokens(tokens, min_length, max_length, num_literals):
    n = len(tokens)
    if n < min_length or n > max_length:
        return False

    # Operator codes.
    STAR  = num_literals
    UNION = num_literals + 1
    LPAR  = num_literals + 2
    RPAR  = num_literals + 3

    has_star = False
    union_count = 0
    consecutive_literals = 0
    max_consecutive_literals = 0
    has_consecutive_literals = False

    for i in range(n):
        t = tokens[i]
        if t == STAR:
            has_star = True
            if i > 0 and tokens[i-1] == STAR:
                return False  # no consecutive stars
            consecutive_literals = 0
        elif t == UNION:
            union_count += 1
            consecutive_literals = 0
        elif t == LPAR or t == RPAR:
            consecutive_literals = 0
        else:
            # t is a literal (0 <= t < num_literals)
            consecutive_literals += 1
            if consecutive_literals >= 2:
                has_consecutive_literals = True
            if consecutive_literals > max_consecutive_literals:
                max_consecutive_literals = consecutive_literals
        # Check for triple parentheses (either LPAR or RPAR).
        if i >= 2:
            if tokens[i] == LPAR and tokens[i-1] == LPAR and tokens[i-2] == LPAR:
                return False
            if tokens[i] == RPAR and tokens[i-1] == RPAR and tokens[i-2] == RPAR:
                return False

    if not has_star:
        return False
    if union_count > 2:
        return False
    if max_consecutive_literals >= 4:
        return False
    if not has_consecutive_literals:
        return False

    return True

# =============================================================================
# Simulation: Count Trials to Generate Target Number of Valid Regexes
# =============================================================================
@njit
def simulate_replication_tokens(literal_prob, num_literals, min_length, max_length, target_valid, max_depth):
    weights = get_weights(literal_prob)
    count = 0
    attempts = 0
    while count < target_valid:
        tokens, prob = gen_regex_tokens(num_literals, weights, max_depth, 0)
        attempts += 1
        if is_valid_tokens(tokens, min_length, max_length, num_literals):
            count += 1
    return attempts

# =============================================================================
# Average Trials over Multiple Replications (calls the njitted simulation)
# =============================================================================
def average_trials_tokens(literal_prob, num_literals, min_length, max_length, target_valid, replications, max_depth):
    total = 0.0
    for i in range(replications):
        total += simulate_replication_tokens(literal_prob, num_literals, min_length, max_length, target_valid, max_depth)
    return total / replications

# =============================================================================
# Objective Function: Average number of trials (to be minimized)
# =============================================================================
def objective(literal_prob, num_literals, min_length, max_length, target_valid, replications, max_depth):
    return average_trials_tokens(literal_prob, num_literals, min_length, max_length, target_valid, replications, max_depth)

# =============================================================================
# Golden Section Search Optimization
# =============================================================================
def golden_section_search(num_literals, min_length, max_length, target_valid, replications, max_depth,
                          low=0.1, high=0.9, tol=0.01):
    phi = (1 + math.sqrt(5)) / 2
    resphi = 2 - phi

    c = high - (high - low) * resphi
    d = low + (high - low) * resphi
    fc = objective(c, num_literals, min_length, max_length, target_valid, replications, max_depth)
    fd = objective(d, num_literals, min_length, max_length, target_valid, replications, max_depth)
    
    history = [(c, fc), (d, fd)]
    iteration = 0
    while abs(high - low) > tol:
        iteration += 1
        if fc < fd:
            high = d
            d = c
            fd = fc
            c = high - (high - low) * resphi
            fc = objective(c, num_literals, min_length, max_length, target_valid, replications, max_depth)
            history.append((c, fc))
        else:
            low = c
            c = d
            fc = fd
            d = low + (high - low) * resphi
            fd = objective(d, num_literals, min_length, max_length, target_valid, replications, max_depth)
            history.append((d, fd))
        print(f"Iteration {iteration}: interval=({low:.4f}, {high:.4f}), f(c)={fc:.2f}, f(d)={fd:.2f}")
    
    optimal_x = (low + high) / 2
    optimal_obj = objective(optimal_x, num_literals, min_length, max_length, target_valid, replications, max_depth)
    print(f"\nOptimization complete: optimal literal_prob = {optimal_x:.4f} with average trials = {optimal_obj:.2f}")
    return optimal_x, history

# =============================================================================
# MAIN: PARAMETERS AT END FOR EASY TESTING
# =============================================================================
if __name__ == "__main__":
    # PARAMETERS: Adjust these for testing.
    num_literals = 4         # Alphabet size (e.g. 4 produces literals 0,1,2,3 corresponding to a,b,c,d)
    min_length = 6           # Minimum token length (each token is one character in the final regex)
    max_length = 8           # Maximum token length
    target_valid = 500       # Target number of valid regex samples per replication
    replications = 5         # Number of replications for averaging
    max_depth = max(3, math.ceil(math.log(min_length, 2)) + 1)  # Maximum recursion depth
    # Optimization search interval for literal probability.
    search_low = 0.1
    search_high = 0.9
    tol = 0.01

    start_time = time.time()
    
    # Optimize the literal probability using golden section search.
    optimal_literal_prob, history = golden_section_search(num_literals, min_length, max_length,
                                                          target_valid, replications, max_depth,
                                                          low=search_low, high=search_high, tol=tol)
    # Derive full weight tuple from optimal literal probability.
    optimal_weights = (optimal_literal_prob, (1 - optimal_literal_prob) * 0.5,
                       (1 - optimal_literal_prob) * 0.3, (1 - optimal_literal_prob) * 0.2)
    
    # Print the calculated (optimal) weights.
    print("\nOptimal Weights:")
    print(f"  literal: {optimal_weights[0]:.4f}")
    print(f"  star:    {optimal_weights[1]:.4f}")
    print(f"  union:   {optimal_weights[2]:.4f}")
    print(f"  concat:  {optimal_weights[3]:.4f}")
    
    # Run one replication with the optimal weights to report total attempts.
    total_attempts = simulate_replication_tokens(optimal_literal_prob, num_literals, min_length, max_length,
                                                  target_valid, max_depth)
    print(f"\nWith optimal weights, it took {total_attempts} total trials to generate {target_valid} valid regex samples.")
    
    # Optionally, plot the optimization history.
    history_arr = np.array(history)
    plt.figure(figsize=(8, 5))
    plt.plot(history_arr[:, 0], history_arr[:, 1], 'o-', label='Avg Trials')
    plt.xlabel("Literal Probability")
    plt.ylabel("Avg Trials for 500 Valid Samples")
    plt.title("Optimization History")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    total_time = time.time() - start_time
    print(f"\nTotal optimization time: {total_time:.2f} seconds")