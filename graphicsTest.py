import pygame
import sys
import math
from randomDFA import randomDFA  # Ensure this module is available in your project

def calculate_positions(states, start_state, screen_width, screen_height):
    """Distributes states evenly in a circular pattern, ensuring that
    the start state is at the vertical center and the leftmost point of the circle,
    with the entire DFA being center justified."""
    center_x, center_y = screen_width // 2, screen_height // 2
    radius = min(screen_width, screen_height) // 3

    if start_state in states:
        idx = states.index(start_state)
        ordered_states = states[idx:] + states[:idx]
    else:
        ordered_states = states

    positions = {}
    num_states = len(ordered_states)
    for i, state in enumerate(ordered_states):
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
    loop_radius = 20

    bounding_rect = pygame.Rect(
        x - loop_radius,
        y - state_radius - 2 * loop_radius,
        2 * loop_radius,
        2 * loop_radius
    )

    start_angle = 0
    end_angle = math.pi
    pygame.draw.arc(surface, color, bounding_rect, start_angle, end_angle, arrow_width)

    # Draw the arrow on the left side of the arc
    arrow_angle = math.pi  
    arrow_x = x - loop_radius
    arrow_y = (y - state_radius - 2 * loop_radius) + loop_radius

    tangent_angle = arrow_angle + math.pi / 2
    arrow_len = 10
    arrow_opening = math.pi / 6

    x1 = arrow_x - arrow_len * math.cos(tangent_angle - arrow_opening)
    y1 = arrow_y - arrow_len * math.sin(tangent_angle - arrow_opening)
    x2 = arrow_x - arrow_len * math.cos(tangent_angle + arrow_opening)
    y2 = arrow_y - arrow_len * math.sin(tangent_angle + arrow_opening)

    pygame.draw.line(surface, color, (arrow_x, arrow_y), (x1, y1), arrow_width)
    pygame.draw.line(surface, color, (arrow_x, arrow_y), (x2, y2), arrow_width)

def generate_dfa(alphabet, min_length, max_length):
    """
    Dummy function that returns a DFA with an extra field 'regex'.
    For simplicity, we return a static DFA whose transitions use the first few letters.
    """
    alphabet = "abcde"  # Example alphabet
    min_length = 15
    max_length = 20
    new_dfa = randomDFA()
    print(new_dfa)
    return new_dfa

def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    sidebar_width = 220
    main_area_width = screen_width - sidebar_width
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
    positions = calculate_positions(states, dfa["start_state"], main_area_width, screen_height)
    current_state = dfa["start_state"]
    
    # Input-related variables and history.
    input_text = ""
    history = []  # Each entry will be (submitted_string, final_marker_color)
    
    # Define UI elements.
    text_box_rect = pygame.Rect(50, screen_height - 50, main_area_width - 150, 40)
    enter_button_rect = pygame.Rect(text_box_rect.right + 10, text_box_rect.y, 80, 40)
    reload_button_rect = pygame.Rect(main_area_width - 150, 20, 100, 40)
    
    def draw_screen(override_marker_pos=None):
        screen.fill((255, 255, 255))
        
        # --- Draw DFA transitions ---
        arrow_color = (0, 0, 0)
        for state, transitions in dfa["transitions"].items():
            for symbol, target in transitions.items():
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
        
        # --- Draw state circles and labels ---
        for state, pos in positions.items():
            pygame.draw.circle(screen, (0, 0, 255), pos, state_radius, 2)
            label = font.render(str(state), True, (0, 0, 0))
            screen.blit(label, label.get_rect(center=pos))
        
        # --- Draw the marker (the little character) ---
        marker_pos = override_marker_pos if override_marker_pos is not None else positions[current_state]
        if current_state == dfa["start_state"]:
            marker_color = (255, 165, 0)  # Orange
        elif "accept_states" in dfa and current_state in dfa["accept_states"]:
            marker_color = (0, 255, 0)    # Green
        elif "dead_states" in dfa and current_state in dfa["dead_states"]:
            marker_color = (128, 128, 128)  # Gray
        else:
            marker_color = (255, 0, 0)    # Red
        pygame.draw.circle(screen, marker_color, marker_pos, state_radius // 2)
        
        # --- Draw the text input box ---
        pygame.draw.rect(screen, (200, 200, 200), text_box_rect)
        input_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(input_surface, (text_box_rect.x + 5, text_box_rect.y + 5))
        
        # --- Draw the Enter button ---
        pygame.draw.rect(screen, (180, 180, 180), enter_button_rect)
        enter_text = font.render("Enter", True, (0, 0, 0))
        screen.blit(enter_text, enter_text.get_rect(center=enter_button_rect.center))
        
        # --- Draw the Reload button ---
        pygame.draw.rect(screen, (180, 180, 180), reload_button_rect)
        reload_text = font.render("Reload", True, (0, 0, 0))
        screen.blit(reload_text, reload_text.get_rect(center=reload_button_rect.center))
        
        # --- Display the regex if available ---
        regex_str = dfa.get("regex", "")
        if regex_str:
            regex_surface = font.render("Regex: " + regex_str, True, (0, 0, 0))
            screen.blit(regex_surface, (50, 20))
        
        # --- Draw the sidebar for history ---
        sidebar_rect = pygame.Rect(main_area_width, 0, sidebar_width, screen_height)
        pygame.draw.rect(screen, (230, 230, 230), sidebar_rect)
        history_title = font.render("History", True, (0, 0, 0))
        screen.blit(history_title, (main_area_width + 10, 10))
        y_offset = 50
        for entry in history:
            entry_text, entry_color = entry
            entry_surface = font.render(entry_text, True, (0, 0, 0))
            screen.blit(entry_surface, (main_area_width + 10, y_offset))
            pygame.draw.circle(screen, entry_color, (main_area_width + 10 + entry_surface.get_width() + 20, 
                                                      y_offset + entry_surface.get_height() // 2), 10)
            y_offset += entry_surface.get_height() + 10

    def animate_transition(from_state, to_state):
        nonlocal current_state
        start_pos = positions[from_state]
        end_pos = positions[to_state]
        steps = 20
        for i in range(1, steps + 1):
            interp_x = start_pos[0] + (end_pos[0] - start_pos[0]) * i / steps
            interp_y = start_pos[1] + (end_pos[1] - start_pos[1]) * i / steps
            draw_screen(override_marker_pos=(int(interp_x), int(interp_y)))
            pygame.display.flip()
            pygame.time.delay(20)
        current_state = to_state

    def animate_self_loop(state, steps=20):
        """Animate the marker along a self loop arc for the given state."""
        pos = positions[state]
        x, y = pos
        loop_radius = 20  # should match the radius in draw_self_loop
        
        # Compute the center of the arc
        # The bounding rect in draw_self_loop is defined as:
        #   (x - loop_radius, y - state_radius - 2*loop_radius, 2*loop_radius, 2*loop_radius)
        # so the center of the arc is:
        center = (x, y - state_radius - loop_radius)
        
        start_angle = 0
        end_angle = math.pi

        for i in range(steps + 1):
            t = i / steps
            theta = start_angle + t * (end_angle - start_angle)
            marker_x = center[0] + loop_radius * math.cos(theta)
            marker_y = center[1] + loop_radius * math.sin(theta)
            draw_screen(override_marker_pos=(int(marker_x), int(marker_y)))
            pygame.display.flip()
            pygame.time.delay(20)

    def animate_string(input_str):
        nonlocal current_state
        # Restart at the DFA's start state.
        current_state = dfa["start_state"]
        draw_screen()
        pygame.display.flip()
        pygame.time.delay(300)
        # Process each character in the submitted string.
        for char in input_str:
            transitions = dfa["transitions"][current_state]
            matched = None
            # Look for a matching transition (case-insensitive).
            for key in transitions:
                if key.lower() == char.lower():
                    matched = key
                    break
            if matched is not None:
                next_state = transitions[matched]
                if current_state == next_state:
                    animate_self_loop(current_state)
                else:
                    animate_transition(current_state, next_state)
            else:
                # Ignore characters not in the DFA's alphabet.
                continue
        # Determine the final state's marker color.
        if current_state == dfa["start_state"]:
            marker_color = (255, 165, 0)
        elif "accept_states" in dfa and current_state in dfa["accept_states"]:
            marker_color = (0, 255, 0)
        elif "dead_states" in dfa and current_state in dfa["dead_states"]:
            marker_color = (128, 128, 128)
        else:
            marker_color = (255, 0, 0)
        return marker_color

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if input_text != "":
                        final_color = animate_string(input_text)
                        history.append((input_text, final_color))
                        input_text = ""
                else:
                    input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if enter_button_rect.collidepoint(event.pos):
                    if input_text != "":
                        final_color = animate_string(input_text)
                        history.append((input_text, final_color))
                        input_text = ""
                elif reload_button_rect.collidepoint(event.pos):
                    dfa = generate_dfa("abcd", 1, 5)
                    states = list(dfa["transitions"].keys())
                    positions = calculate_positions(states, dfa["start_state"], main_area_width, screen_height)
                    current_state = dfa["start_state"]
                    input_text = ""
        
        draw_screen()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()