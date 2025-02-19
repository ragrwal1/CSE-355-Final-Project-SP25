import pygame
import sys
import math
from randomDFA import randomDFA

def calculate_positions(states, start_state, screen_width, screen_height):
    """Distributes states evenly in a circular pattern, ensuring that
    the start state is at the vertical center and the leftmost point of the circle,
    with the entire DFA being center justified."""
    center_x, center_y = screen_width // 2, screen_height // 2
    radius = min(screen_width, screen_height) // 3

    # Reorder states so that the start state comes first.
    if start_state in states:
        idx = states.index(start_state)
        ordered_states = states[idx:] + states[:idx]
    else:
        ordered_states = states

    positions = {}
    num_states = len(ordered_states)
    for i, state in enumerate(ordered_states):
        # With an offset of math.pi, the first state (i.e. the start state) is placed at the leftmost point.
        angle = (2 * math.pi * i) / num_states + math.pi
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        positions[state] = (x, y)
    return positions

def draw_arrow(surface, start, end, color, arrow_width=2):
    """Draws a directed arrow from start to end."""
    pygame.draw.line(surface, color, start, end, arrow_width)
    dx, dy = end[0] - start[0], end[1] - start[1]
    angle = math.atan2(dy, dx)
    arrow_length = 10
    arrow_angle = math.pi / 6  # 30 degrees

    x1 = end[0] - arrow_length * math.cos(angle - arrow_angle)
    y1 = end[1] - arrow_length * math.sin(angle - arrow_angle)
    x2 = end[0] - arrow_length * math.cos(angle + arrow_angle)
    y2 = end[1] - arrow_length * math.sin(angle + arrow_angle)

    pygame.draw.line(surface, color, end, (x1, y1), arrow_width)
    pygame.draw.line(surface, color, end, (x2, y2), arrow_width)

def draw_self_loop(surface, pos, state_radius, color, arrow_width=2):
    """
    Draw a half-circle arc above the given state (pos),
    and place an arrow at the left end of that arc.
    """
    x, y = pos
    loop_radius = 20  # How large the self-loop arc should be

    # The bounding rect for the arc is centered horizontally on the state,
    # but moved up so the arc is above the state circle.
    # The top of the bounding box is at (y - state_radius - 2*loop_radius)
    # because we want enough space above the state to see the arc clearly.
    bounding_rect = pygame.Rect(
        x - loop_radius,
        y - state_radius - 2 * loop_radius,
        2 * loop_radius,
        2 * loop_radius
    )

    # Draw a half-circle from 0 to π (0 to 180 degrees).
    # In pygame's arc coordinates, 0 radians is to the right, and angles increase counter-clockwise.
    start_angle = 0
    end_angle = math.pi
    pygame.draw.arc(surface, color, bounding_rect, start_angle, end_angle, arrow_width)

    #
    # Draw the arrowhead at the end of the arc (i.e., the left side at angle = π).
    #
    arrow_angle = math.pi  # leftmost point on the arc
    arrow_x = x - loop_radius
    # The arc is centered at y - state_radius - loop_radius vertically
    arrow_y = (y - state_radius - 2 * loop_radius) + loop_radius

    # For a circle, a tangent at angle θ is θ + π/2. 
    # So if the arc ends at angle π, its tangent is π + π/2 = 3π/2 (straight down).
    tangent_angle = arrow_angle + math.pi / 2

    arrow_len = 10
    arrow_opening = math.pi / 6  # 30° on each side

    x1 = arrow_x - arrow_len * math.cos(tangent_angle - arrow_opening)
    y1 = arrow_y - arrow_len * math.sin(tangent_angle - arrow_opening)
    x2 = arrow_x - arrow_len * math.cos(tangent_angle + arrow_opening)
    y2 = arrow_y - arrow_len * math.sin(tangent_angle + arrow_opening)

    # Draw the two arrowhead lines.
    pygame.draw.line(surface, color, (arrow_x, arrow_y), (x1, y1), arrow_width)
    pygame.draw.line(surface, color, (arrow_x, arrow_y), (x2, y2), arrow_width)

def generate_dfa(alphabet, min_length, max_length):
    """
    Dummy function that takes an alphabet, a minimum length, and a maximum length.
    Returns a DFA with an extra field 'regex'.
    For simplicity, we return a static DFA whose transitions use the first two letters of the alphabet.
    """
    # Use only the first two letters of a dummy alphabet.
    alphabet = "abcde"  # Example alphabet
    min_length = 15
    max_length = 20
    new_dfa = randomDFA(alphabet, min_length, max_length)
    print(new_dfa)
    return new_dfa

def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Modular DFA Visualization")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # --- Initial DFA definition ---
    dfa = {
        "start_state": 3,
        "accept_states": [0],
        "transitions": {
            0: {'a': 1, 'b': 1, 'c': 0, 'd': 1},
            1: {'a': 1, 'b': 1, 'c': 1, 'd': 1},
            2: {'a': 1, 'b': 1, 'c': 0, 'd': 1},
            3: {'a': 0, 'b': 1, 'c': 2, 'd': 1},
        },
        "regex": "(cc|a)c*"
    }
    
    state_radius = 30
    states = list(dfa["transitions"].keys())
    positions = calculate_positions(states, dfa["start_state"], screen_width, screen_height)
    
    current_state = dfa["start_state"]
    input_text = ""
    
    # Define the reload button (positioned at top-right)
    reload_button_rect = pygame.Rect(screen_width - 150, 20, 100, 40)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check for key presses for the DFA input.
            elif event.type == pygame.KEYDOWN:
                # Handle backspace: remove the last character and recalc the state.
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                    current_state = dfa["start_state"]
                    for c in input_text:
                        transitions = dfa["transitions"][current_state]
                        matched = None
                        # Do a case-insensitive match.
                        for key in transitions:
                            if key.lower() == c.lower():
                                matched = key
                                break
                        if matched is not None:
                            current_state = transitions[matched]
                else:
                    char = event.unicode  # Preserve the character's case.
                    # Allow letters (both cases) and numbers.
                    if char in "01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
                        input_text += char
                        transitions = dfa["transitions"][current_state]
                        matched = None
                        # Find a transition that matches the input character case-insensitively.
                        for key in transitions:
                            if key.lower() == char.lower():
                                matched = key
                                break
                        if matched is not None:
                            current_state = transitions[matched]

            # Check for mouse clicks to handle the reload button.
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if reload_button_rect.collidepoint(event.pos):
                    dfa = generate_dfa("abcd", 1, 5)
                    # Recalculate states and positions from the new DFA.
                    states = list(dfa["transitions"].keys())
                    positions = calculate_positions(states, dfa["start_state"], screen_width, screen_height)
                    current_state = dfa["start_state"]
                    input_text = ""
                    
        screen.fill((255, 255, 255))  # White background

        # Draw the DFA transitions as arrows or self loops.
        arrow_color = (0, 0, 0)
        for state, transitions in dfa["transitions"].items():
            for symbol, target in transitions.items():
                # Check if the transition is a self loop.
                if state == target:
                    draw_self_loop(screen, positions[state], state_radius, arrow_color)
                else:
                    start = positions[state]
                    end = positions[target]
                    dx, dy = end[0] - start[0], end[1] - start[1]
                    dist = math.hypot(dx, dy)
                    if dist == 0:
                        dist = 1
                    ux, uy = dx / dist, dy / dist
                    start_pos = (start[0] + ux * state_radius, start[1] + uy * state_radius)
                    end_pos = (end[0] - ux * state_radius, end[1] - uy * state_radius)
                    draw_arrow(screen, start_pos, end_pos, arrow_color)

        # Draw state circles with labels.
        for state, pos in positions.items():
            pygame.draw.circle(screen, (0, 0, 255), pos, state_radius, 2)
            label = font.render(str(state), True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=pos))
        
        # Highlight the current state with a distinct visual cue.
        if current_state == dfa["start_state"]:
            marker_color = (255, 165, 0)  # Orange for the start state.
        elif "accept_states" in dfa and current_state in dfa["accept_states"]:
            marker_color = (0, 255, 0)    # Green for accept states.
        elif "dead_states" in dfa and current_state in dfa["dead_states"]:
            marker_color = (128, 128, 128)  # Gray for dead states.
        else:
            marker_color = (255, 0, 0)    # Red for a normal state.
        
        pygame.draw.circle(screen, marker_color, positions[current_state], state_radius // 2)

        # Display the input text.
        text_box_rect = pygame.Rect(50, screen_height - 50, screen_width - 100, 40)
        pygame.draw.rect(screen, (200, 200, 200), text_box_rect)
        input_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(input_surface, (text_box_rect.x + 5, text_box_rect.y + 5))
        
        # Display the regex if available.
        regex_str = dfa.get("regex", "")
        if regex_str:
            regex_surface = font.render("Regex: " + regex_str, True, (0, 0, 0))
            screen.blit(regex_surface, (50, 20))
        
        # Draw the reload button.
        pygame.draw.rect(screen, (180, 180, 180), reload_button_rect)
        reload_text = font.render("Reload", True, (0, 0, 0))
        screen.blit(reload_text, reload_text.get_rect(center=reload_button_rect.center))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()