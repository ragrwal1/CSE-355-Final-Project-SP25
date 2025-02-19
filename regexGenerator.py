import random

def generate_balanced_regex(alphabet, min_length, max_length):
    """
    Generate a balanced regex string using the given alphabet.
    The regex will contain:
      - Literals (characters from 'alphabet')
      - Kleene stars (*)
      - Unions (|)
      - Concatenations
      - Some grouping, but minimal deep nesting.

    The final regex string will have a length between min_length and max_length.
    
    Parameters:
      alphabet (str): A string containing characters from the allowed alphabet.
      min_length (int): Minimum length of the generated regex.
      max_length (int): Maximum length of the generated regex.
    
    Returns:
      str: A randomly generated regex string.
    """
    if min_length > max_length:
        raise ValueError("min_length must be less than or equal to max_length")

    max_depth = 3  # A reasonable depth for structured but readable regexes

    def gen_regex(depth=0):
        if depth >= max_depth:
            return random.choice(alphabet)  # Base case: return a literal
        
        r = random.random()
        
        if r < 0.6:
            # 60% chance: Return a literal character.
            return random.choice(alphabet)
        elif r < 0.75:
            # 15% chance: Apply Kleene star to a simple literal or short expression.
            subexpr = random.choice(alphabet) if random.random() < 0.7 else gen_regex(depth + 1)
            return f"{subexpr}*"
        elif r < 0.9:
            # 15% chance: Create a union between two simple expressions.
            left = random.choice(alphabet) if random.random() < 0.5 else gen_regex(depth + 1)
            right = random.choice(alphabet) if random.random() < 0.5 else gen_regex(depth + 1)
            return f"({left}|{right})"
        else:
            # 10% chance: Concatenation of two subexpressions.
            return gen_regex(depth + 1) + gen_regex(depth + 1)

    # Try generating candidates until one fits the length criteria.
    for _ in range(1000):
        candidate = gen_regex(0)
        if min_length <= len(candidate) <= max_length:
            return candidate

    # Fallback: Adjust candidate to satisfy the constraints.
    candidate = gen_regex(0)
    if len(candidate) > max_length:
        candidate = candidate[:max_length]
    while len(candidate) < min_length:
        candidate += random.choice(alphabet)
    return candidate

# Example usage:
if __name__ == "__main__":
    alphabet = "abcd"  # Example alphabet
    min_len = 10
    max_len = 20


    regex_string = generate_balanced_regex(alphabet, min_len, max_len)
    print(regex_string)