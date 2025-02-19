import pygame
import sys
import math

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

def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Modular DFA Visualization")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Define an example DFA.
    # Four fields:
    # - "start_state": the starting state.
    # - "accept_states": list of one or more accept states.
    # - "dead_states": list of states with no exits.
    # - "transitions": the state transition dictionary.
    dfa = {
        "start_state": 0,
        "accept_states": [1, 2],
        "dead_states": [3],
        "transitions": {
            0: {'A': 1, 'B': 2, '0': 3},
            1: {'A': 1, 'B': 3},
            2: {'A': 3, 'B': 2},
            3: {}  # Dead state (no transitions)
        }
    }
    
    state_radius = 30
    states = list(dfa["transitions"].keys())
    positions = calculate_positions(states, dfa["start_state"], screen_width, screen_height)
    
    current_state = dfa["start_state"]
    input_text = ""
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Handle backspace: remove the last character and recalc the state.
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                    current_state = dfa["start_state"]
                    for c in input_text:
                        if c in dfa["transitions"][current_state]:
                            current_state = dfa["transitions"][current_state][c]
                        else:
                            break
                else:
                    char = event.unicode.upper()
                    if char in "01ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        input_text += char
                        if char in dfa["transitions"][current_state]:
                            current_state = dfa["transitions"][current_state][char]

        screen.fill((255, 255, 255))  # White background

        # Draw transitions as arrows.
        arrow_color = (0, 0, 0)
        for state, transitions in dfa["transitions"].items():
            for symbol, target in transitions.items():
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
        elif current_state in dfa["accept_states"]:
            marker_color = (0, 255, 0)    # Green for accept states.
        elif current_state in dfa["dead_states"]:
            marker_color = (128, 128, 128)  # Gray for dead states.
        else:
            marker_color = (255, 0, 0)    # Red for a normal state.
        
        pygame.draw.circle(screen, marker_color, positions[current_state], state_radius // 2)

        # Display the input text.
        text_box_rect = pygame.Rect(50, screen_height - 50, screen_width - 100, 40)
        pygame.draw.rect(screen, (200, 200, 200), text_box_rect)
        input_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(input_surface, (text_box_rect.x + 5, text_box_rect.y + 5))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()