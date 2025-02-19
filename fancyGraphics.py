import pygame, sys, math, random

def main():
    pygame.init()
    # Increase window size for an epic feel.
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("NFA Visualization - AAA Edition")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 48)

    # Define the NFA.
    # State 0 is the initial state.
    # Transitions: 0 --A--> 1, 0 --B--> 2, 1 --A--> 1, 1 --B--> 3,
    # 2 --A--> 3, 2 --B--> 2, 3 has no transitions (dead state)
    nfa = {
        0: {'A': 1, 'B': 2},
        1: {'A': 1, 'B': 3},
        2: {'A': 3, 'B': 2},
        3: {}  # dead state
    }

    # Positions for states (feel free to adjust for extra flair)
    positions = {
        0: (150, 300),
        1: (400, 150),
        2: (400, 450),
        3: (650, 300)
    }
    state_radius = 40

    # --- Animation Variables ---
    # Logical state (which state we’re in) and the animated position (for smooth movement)
    logical_state = 0
    player_pos = pygame.math.Vector2(positions[logical_state])
    is_animating = False
    animation_start = pygame.math.Vector2(0, 0)
    animation_end = pygame.math.Vector2(0, 0)
    animation_duration = 0.5  # seconds to move between states
    animation_elapsed = 0.0

    # Shake effect (for invalid transitions)
    shake_timer = 0.0
    shake_duration = 0.5
    shake_magnitude = 10

    # User input text
    input_text = ""

    # --- Particle System ---
    particles = []  # list of Particle objects

    class Particle:
        def __init__(self, pos, vel, life, color):
            self.pos = pygame.math.Vector2(pos)
            self.vel = pygame.math.Vector2(vel)
            self.life = life
            self.max_life = life
            self.color = color

        def update(self, dt):
            self.pos += self.vel * dt
            self.life -= dt

        def draw(self, surface):
            if self.life > 0:
                alpha = max(0, int(255 * (self.life / self.max_life)))
                surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(surf, self.color + (alpha,), (2, 2), 2)
                surface.blit(surf, (self.pos.x - 2, self.pos.y - 2))

    def spawn_particles(pos, direction):
        # Spawn a burst of particles at pos, along the given direction (with some random spread).
        for _ in range(20):
            angle = math.atan2(direction.y, direction.x) + random.uniform(-0.5, 0.5)
            speed = random.uniform(50, 150)
            vel = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed
            life = random.uniform(0.5, 1.0)
            color = (255, 215, 0)  # gold-ish
            particles.append(Particle(pos, vel, life, color))

    # --- Background Starfield ---
    stars = []
    for _ in range(100):
        star = {
            "pos": pygame.math.Vector2(random.uniform(0, screen_width), random.uniform(0, screen_height)),
            "speed": random.uniform(10, 30),
            "size": random.uniform(1, 3)
        }
        stars.append(star)

    def update_stars(dt):
        for star in stars:
            star["pos"].x -= star["speed"] * dt
            if star["pos"].x < 0:
                star["pos"].x = screen_width
                star["pos"].y = random.uniform(0, screen_height)

    def draw_stars(surface):
        for star in stars:
            pygame.draw.circle(surface, (255, 255, 255), (int(star["pos"].x), int(star["pos"].y)), int(star["size"]))

    def draw_background(surface):
        # A deep-space, dark blue background with stars.
        surface.fill((10, 10, 30))
        draw_stars(surface)

    # --- Animated Dashed Arrow Drawing ---
    def draw_animated_arrow(surface, start, end, color, time_offset, arrow_width=3):
        dash_length = 10
        gap_length = 5
        total_dash = dash_length + gap_length
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        # Create an offset to animate dashes sliding along the line.
        offset = (time_offset * 100) % total_dash  
        num_dashes = int(dist / total_dash) + 1
        for i in range(num_dashes):
            start_offset = i * total_dash + offset
            dash_start = (start[0] + math.cos(angle) * start_offset, start[1] + math.sin(angle) * start_offset)
            dash_end = (start[0] + math.cos(angle) * min(start_offset + dash_length, dist),
                        start[1] + math.sin(angle) * min(start_offset + dash_length, dist))
            pygame.draw.line(surface, color, dash_start, dash_end, arrow_width)
        # Draw a stylized arrowhead at the end.
        arrow_length = 15
        arrow_angle = math.pi / 6
        x1 = end[0] - arrow_length * math.cos(angle - arrow_angle)
        y1 = end[1] - arrow_length * math.sin(angle - arrow_angle)
        x2 = end[0] - arrow_length * math.cos(angle + arrow_angle)
        y2 = end[1] - arrow_length * math.sin(angle + arrow_angle)
        pygame.draw.line(surface, color, end, (x1, y1), arrow_width)
        pygame.draw.line(surface, color, end, (x2, y2), arrow_width)

    # --- Draw States with a Glowing, Pulsating Effect ---
    def draw_state(surface, state, pos, is_active, time_elapsed):
        base_color = (0, 0, 255)
        glow_color = (0, 0, 255)
        if is_active:
            # Create a pulsating glow.
            pulsate = 1 + 0.3 * math.sin(time_elapsed * 5)
            glow_radius = int(state_radius * 1.5 * pulsate)
            # Draw multiple concentric circles with decreasing alpha.
            for i in range(glow_radius, state_radius, -4):
                if glow_radius != state_radius:
                    alpha = int(255 * (i - state_radius) / (glow_radius - state_radius))
                else:
                    alpha = 255
                s = pygame.Surface((i*2, i*2), pygame.SRCALPHA)
                pygame.draw.circle(s, glow_color + (alpha,), (i, i), i)
                surface.blit(s, (pos[0] - i, pos[1] - i))
        # Main state circle.
        pygame.draw.circle(surface, base_color, pos, state_radius, 3)
        label = font.render(str(state), True, (255, 255, 255))
        label_rect = label.get_rect(center=pos)
        surface.blit(label, label_rect)

    # --- Fancy Text Input Box with an Animated Border ---
    def draw_text_box(surface, text, rect, time_elapsed):
        pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=10)
        r = int(128 + 127 * math.sin(time_elapsed * 2))
        g = int(128 + 127 * math.sin(time_elapsed * 3))
        b = int(128 + 127 * math.sin(time_elapsed * 4))
        border_color = (r, g, b)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=10)
        text_surf = font.render(text, True, (255, 255, 255))
        surface.blit(text_surf, (rect.x + 10, rect.y + (rect.height - text_surf.get_height()) // 2))

    # Global time accumulator.
    time_elapsed = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        time_elapsed += dt
        
        # --- Handle Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Allow backspace to remove last character and reset state.
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                    logical_state = 0
                    player_pos = pygame.math.Vector2(positions[logical_state])
                    is_animating = False
                else:
                    char = event.unicode.upper()
                    if char in ['A', 'B']:
                        # Only process new input if not already animating.
                        if not is_animating:
                            if char in nfa[logical_state]:
                                input_text += char
                                # Prepare for a smooth animated transition.
                                new_state = nfa[logical_state][char]
                                animation_start = pygame.math.Vector2(positions[logical_state])
                                animation_end = pygame.math.Vector2(positions[new_state])
                                is_animating = True
                                animation_elapsed = 0.0
                                # Spawn a particle burst along the direction of movement.
                                direction = animation_end - animation_start
                                if direction.length() != 0:
                                    direction = direction.normalize()
                                spawn_particles(animation_start, direction)
                                logical_state = new_state  # update logical state immediately
                            else:
                                # No valid transition? Append the letter and trigger a shake effect.
                                input_text += char
                                shake_timer = shake_duration

        # --- Update Animations ---
        if is_animating:
            animation_elapsed += dt
            t = min(animation_elapsed / animation_duration, 1)
            # Ease-out interpolation.
            t = 1 - (1 - t) * (1 - t)
            player_pos = animation_start.lerp(animation_end, t)
            if animation_elapsed >= animation_duration:
                is_animating = False
                player_pos = pygame.math.Vector2(animation_end)

        # Shake offset if an invalid key was pressed.
        shake_offset = pygame.math.Vector2(0, 0)
        if shake_timer > 0:
            shake_timer -= dt
            shake_offset.x = shake_magnitude * math.sin(time_elapsed * 30) * (shake_timer / shake_duration)
            shake_offset.y = shake_magnitude * math.cos(time_elapsed * 30) * (shake_timer / shake_duration)

        # --- Update Particles ---
        for p in particles:
            p.update(dt)
        particles = [p for p in particles if p.life > 0]

        # --- Update Starfield ---
        update_stars(dt)

        # --- Drawing ---
        draw_background(screen)

        # Draw all transitions as animated dashed arrows.
        arrow_color = (200, 200, 200)
        for state, transitions in nfa.items():
            for symbol, target in transitions.items():
                start = pygame.math.Vector2(positions[state])
                end = pygame.math.Vector2(positions[target])
                direction = (end - start)
                if direction.length() == 0:
                    continue
                direction.normalize_ip()
                start_pos = start + direction * state_radius
                end_pos = end - direction * state_radius
                draw_animated_arrow(screen, start_pos, end_pos, arrow_color, time_elapsed)

        # Draw state circles with glowing effects.
        for state, pos in positions.items():
            draw_state(screen, state, pos, state == logical_state, time_elapsed)

        # Draw particle effects.
        for p in particles:
            p.draw(screen)

        # Draw the “player” token (a red circle) with shake added.
        red_color = (255, 50, 50)
        final_pos = (int(player_pos.x + shake_offset.x), int(player_pos.y + shake_offset.y))
        pygame.draw.circle(screen, red_color, final_pos, state_radius // 2)

        # Draw the text input box at the bottom.
        text_box_rect = pygame.Rect(50, screen_height - 70, screen_width - 100, 50)
        draw_text_box(screen, input_text, text_box_rect, time_elapsed)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()