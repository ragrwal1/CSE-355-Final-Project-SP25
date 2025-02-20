import pygame
import json
import hashlib

# -----------------------------------------------------------------------------
# Base Configuration Dictionary for Regex Generation
# -----------------------------------------------------------------------------
CONFIG = {
    'alphabet': "abc",         # Example alphabet
    'min_length': 5,
    'max_length': 10,
    'trials': 100,             # Trials used during weight optimization
    'num_optimizations': 40,   # Number of optimization runs
    'precision': 0.05,         # Tolerance for binary search in optimization
    'show_plot': False,       # Whether to show the plot of rolling averages
    'num_samples': 30,         # Number of sample regexes to generate after optimization
    'literal_prob': 0.5        # Initial literal probability (can be overridden by optimization)
}

def run_home_screen():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("DFA Game - Home Screen (Config)")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    large_font = pygame.font.Font(None, 40)
    
    # Work with a copy of the default config so we can modify it.
    config = CONFIG.copy()
    # Create an ordered list of config keys for navigation.
    keys = list(config.keys())
    selected_index = 0  # index of the currently selected option
    
    # Define the "Start Game" button.
    start_button_rect = pygame.Rect(screen_width // 2 - 75, 500, 150, 50)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Signal the main program to quit.
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(keys)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(keys)
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    key = keys[selected_index]
                    # Adjust the value based on its type.
                    if isinstance(config[key], bool):
                        config[key] = not config[key]
                    elif isinstance(config[key], int):
                        config[key] += -1 if event.key == pygame.K_LEFT else 1
                    elif isinstance(config[key], float):
                        config[key] += -0.01 if event.key == pygame.K_LEFT else 0.01
                        config[key] = round(config[key], 2)
                    elif isinstance(config[key], str):
                        # For the 'alphabet', cycle through predefined options.
                        options = ["abc", "abcd", "abcde"]
                        current = config[key]
                        idx = options.index(current) if current in options else 0
                        idx = (idx - 1) % len(options) if event.key == pygame.K_LEFT else (idx + 1) % len(options)
                        config[key] = options[idx]
                elif event.key == pygame.K_RETURN:
                    # Return the configuration when Enter is pressed.
                    return config
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    return config
        
        # --- Rendering the Home Screen ---
        screen.fill((255, 255, 255))  # White background
        
        # Draw the title.
        title_text = large_font.render("DFA Game Configuration", True, (0, 0, 0))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 20))
        
        # Draw instructions.
        instr_text = font.render("Use UP/DOWN to select, LEFT/RIGHT to adjust, Enter or click Start to begin.", True, (0, 0, 0))
        screen.blit(instr_text, (screen_width // 2 - instr_text.get_width() // 2, 70))
        
        # Draw the list of configuration options.
        start_y = 120
        spacing = 30
        for idx, key in enumerate(keys):
            # Highlight the selected option.
            color = (0, 0, 255) if idx == selected_index else (0, 0, 0)
            option_text = f"{key}: {config[key]}"
            text_surface = font.render(option_text, True, color)
            screen.blit(text_surface, (100, start_y + idx * spacing))
        
        # Draw the "Start Game" button.
        pygame.draw.rect(screen, (0, 200, 0), start_button_rect)
        button_text = large_font.render("Start Game", True, (255, 255, 255))
        screen.blit(button_text, button_text.get_rect(center=start_button_rect.center))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    final_config = run_home_screen()
    print("Final configuration:", final_config)
    pygame.quit()