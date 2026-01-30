import pygame
import sys
import random
import math

# --- Configuration & Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Neon Palette)
c_BG = (15, 15, 25)           # Deep Space Blue
c_PADDLE = (0, 255, 255)      # Cyan
c_BALL = (255, 255, 255)      # White
c_TEXT = (255, 255, 255)
c_ACCENT = (255, 0, 128)      # Neon Pink

# Brick Gradients
BRICK_COLORS = [
    (255, 50, 50),   # Red
    (255, 120, 0),   # Orange
    (255, 200, 0),   # Gold
    (50, 200, 50),   # Green
    (50, 100, 255),  # Blue
    (150, 50, 255)   # Purple
]

# --- Helper Classes ---

class Star:
    """Background stars for visual appeal"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 2.0)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, (self.brightness, self.brightness, self.brightness), (int(self.x), int(self.y)), self.size)

class Particle:
    """Explosion effect when breaking bricks"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 8)
        self.life = 40
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size -= 0.1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, 200), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))

class FloatingText:
    """Score popups"""
    def __init__(self, x, y, text, font):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.life = 30
        self.dy = -2

    def update(self):
        self.y += self.dy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, self.life * 10)
            txt_surf = self.font.render(self.text, True, c_TEXT)
            txt_surf.set_alpha(alpha)
            surface.blit(txt_surf, (self.x, self.y))

class PowerUp:
    """Falling items"""
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.type = type # "W" for Wide, "L" for Life
        self.dy = 3
        self.color = (50, 255, 50) if type == "W" else (255, 50, 50)

    def update(self):
        self.rect.y += self.dy

    def draw(self, surface, font):
        pygame.draw.circle(surface, self.color, self.rect.center, 15)
        pygame.draw.circle(surface, (255,255,255), self.rect.center, 15, 2)
        txt = font.render(self.type, True, (255,255,255))
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

class Button:
    def __init__(self, text, x, y, w, h, func_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.func_code = func_code
        self.hover = False

    def draw(self, surface, font):
        color = (50, 200, 200) if self.hover else (30, 30, 50)
        border = (255, 255, 255) if self.hover else (100, 100, 100)
        
        # Draw shadow
        pygame.draw.rect(surface, (10, 10, 10), (self.rect.x+5, self.rect.y+5, self.rect.w, self.rect.h), border_radius=10)
        # Draw button
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=10)
        
        txt = font.render(self.text, True, c_TEXT)
        rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

# --- Main Game Class ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Brick Junior Ball")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_big = pygame.font.Font(None, 80)
        self.font_med = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 30)

        # Game Objects
        self.stars = [Star() for _ in range(50)]
        self.state = "MENU" # MENU, PLAYING, PAUSED, GAMEOVER, WIN
        
        # Buttons
        self.buttons = [
            Button("PLAY", SCREEN_WIDTH//2 - 100, 350, 200, 60, "PLAY"),
            Button("QUIT", SCREEN_WIDTH//2 - 100, 430, 200, 60, "QUIT")
        ]
        self.pause_btn = Button("||", SCREEN_WIDTH - 50, 10, 40, 40, "PAUSE")
        self.menu_btn = Button("MENU", SCREEN_WIDTH//2 - 100, 400, 200, 60, "MENU")

        self.reset_level()

    def reset_level(self):
        self.paddle_w = 120
        self.paddle_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT - 40, 120, 15)
        self.ball_rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 16, 16)
        self.ball_speed = 6
        self.ball_dx = 0
        self.ball_dy = 0
        self.ball_active = False
        self.lives = 3
        self.score = 0
        self.shake_timer = 0
        
        self.bricks = []
        self.particles = []
        self.floaters = []
        self.powerups = []
        self.ball_trail = [] # List of (x,y)
        
        # Create Bricks
        rows = 6
        cols = 9
        w = 70
        h = 25
        padding = 10
        offset_x = (SCREEN_WIDTH - (cols * (w + padding))) // 2
        
        for r in range(rows):
            for c in range(cols):
                bx = offset_x + c * (w + padding)
                by = 60 + r * (h + padding)
                rect = pygame.Rect(bx, by, w, h)
                color = BRICK_COLORS[r % len(BRICK_COLORS)]
                self.bricks.append({'rect': rect, 'color': color})

    def apply_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            return offset_x, offset_y
        return 0, 0

    def run(self):
        while True:
            shake_x, shake_y = self.apply_shake()
            display_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            display_surf.fill(c_BG)

            mouse_pos = pygame.mouse.get_pos()
            click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: click = True
                if event.type == pygame.KEYDOWN:
                    if self.state == "PLAYING":
                        if event.key == pygame.K_p: self.state = "PAUSED"
                        if not self.ball_active and event.key == pygame.K_SPACE:
                            self.ball_active = True
                            self.ball_dx = random.choice([-4, 4])
                            self.ball_dy = -self.ball_speed
                    elif self.state == "PAUSED":
                        if event.key == pygame.K_p: self.state = "PLAYING"

            # Draw Stars (Background)
            for s in self.stars:
                s.update()
                s.draw(display_surf)

            # --- STATE MACHINE ---
            if self.state == "MENU":
                self.draw_menu(display_surf, mouse_pos, click)
            elif self.state == "PLAYING":
                self.update_game()
                self.draw_game(display_surf, mouse_pos, click)
            elif self.state == "PAUSED":
                self.draw_game(display_surf, mouse_pos, click) # Draw game frozen
                self.draw_overlay(display_surf, "PAUSED", "Press P to Resume")
                if self.menu_btn.check_hover(mouse_pos) and click: self.state = "MENU"
                self.menu_btn.draw(display_surf, self.font_med)
            elif self.state == "GAMEOVER":
                self.draw_game(display_surf, mouse_pos, click)
                self.draw_overlay(display_surf, "GAME OVER", f"Score: {self.score}", (255, 50, 50))
                if self.menu_btn.check_hover(mouse_pos) and click: self.state = "MENU"
                self.menu_btn.draw(display_surf, self.font_med)
            elif self.state == "WIN":
                self.draw_game(display_surf, mouse_pos, click)
                self.draw_overlay(display_surf, "YOU WIN!", f"Score: {self.score}", (50, 255, 50))
                if self.menu_btn.check_hover(mouse_pos) and click: self.state = "MENU"
                self.menu_btn.draw(display_surf, self.font_med)

            # Render Final Screen with Shake
            self.screen.blit(display_surf, (shake_x, shake_y))
            pygame.display.flip()
            self.clock.tick(FPS)

    def update_game(self):
        # Paddle Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.paddle_rect.left > 0:
            self.paddle_rect.x -= 8
        if keys[pygame.K_RIGHT] and self.paddle_rect.right < SCREEN_WIDTH:
            self.paddle_rect.x += 8

        # Ball Physics
        if self.ball_active:
            # Update position
            self.ball_rect.x += self.ball_dx
            self.ball_rect.y += self.ball_dy
            
            # Trail logic
            self.ball_trail.append(self.ball_rect.center)
            if len(self.ball_trail) > 10: self.ball_trail.pop(0)

            # Walls
            if self.ball_rect.left <= 0 or self.ball_rect.right >= SCREEN_WIDTH:
                self.ball_dx *= -1
            if self.ball_rect.top <= 0:
                self.ball_dy *= -1
            
            # Death
            if self.ball_rect.top > SCREEN_HEIGHT:
                self.lives -= 1
                self.ball_active = False
                self.paddle_rect.width = 120 # Reset powerups
                if self.lives <= 0:
                    self.state = "GAMEOVER"

            # Paddle Collision (Physics: Angle changes based on hit spot)
            if self.ball_rect.colliderect(self.paddle_rect) and self.ball_dy > 0:
                self.ball_dy = -abs(self.ball_dy) # Ensure it goes up
                # Calculate offset (-1 to 1)
                offset = (self.ball_rect.centerx - self.paddle_rect.centerx) / (self.paddle_rect.width / 2)
                self.ball_dx = offset * 6 # Max horizontal speed
                self.shake_timer = 5
                
            # Brick Collision
            hit_index = self.ball_rect.collidelist([b['rect'] for b in self.bricks])
            if hit_index != -1:
                brick = self.bricks.pop(hit_index)
                self.ball_dy *= -1
                self.score += 100
                self.shake_timer = 8
                
                # Visuals
                for _ in range(10):
                    self.particles.append(Particle(brick['rect'].centerx, brick['rect'].centery, brick['color']))
                self.floaters.append(FloatingText(brick['rect'].x, brick['rect'].y, "+100", self.font_small))
                
                # Powerup Drop Chance (15%)
                if random.random() < 0.15:
                    ptype = "W" if random.random() < 0.5 else "L"
                    self.powerups.append(PowerUp(brick['rect'].centerx, brick['rect'].centery, ptype))

                if not self.bricks:
                    self.state = "WIN"

        # Update Particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)
            
        # Update Floaters
        for f in self.floaters[:]:
            f.update()
            if f.life <= 0: self.floaters.remove(f)

        # Update Powerups
        for p in self.powerups[:]:
            p.update()
            if p.rect.colliderect(self.paddle_rect):
                if p.type == "W":
                    self.paddle_rect.width = 180
                    self.floaters.append(FloatingText(self.paddle_rect.centerx, self.paddle_rect.y - 20, "WIDE PADDLE!", self.font_small))
                elif p.type == "L":
                    self.lives += 1
                    self.floaters.append(FloatingText(self.paddle_rect.centerx, self.paddle_rect.y - 20, "EXTRA LIFE!", self.font_small))
                self.powerups.remove(p)
            elif p.rect.y > SCREEN_HEIGHT:
                self.powerups.remove(p)

    def draw_menu(self, surface, mouse_pos, click):
        # Pulsing Title
        scale = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
        title = self.font_big.render("Brick Junior Ball", True, c_PADDLE)
        # Center the scaled title
        w = title.get_width()
        h = title.get_height()
        scaled_title = pygame.transform.scale(title, (int(w * scale), int(h * scale)))
        rect = scaled_title.get_rect(center=(SCREEN_WIDTH//2, 150))
        surface.blit(scaled_title, rect)

        # Credits
        credit = self.font_small.render("Made by Safwan Sabit", True, c_ACCENT)
        c_rect = credit.get_rect(center=(SCREEN_WIDTH//2, 220))
        surface.blit(credit, c_rect)

        # Buttons
        for btn in self.buttons:
            if btn.check_hover(mouse_pos) and click:
                if btn.func_code == "PLAY":
                    self.reset_level()
                    self.state = "PLAYING"
                elif btn.func_code == "QUIT":
                    pygame.quit(); sys.exit()
            btn.draw(surface, self.font_med)

    def draw_game(self, surface, mouse_pos, click):
        # Draw UI
        score_t = self.font_small.render(f"SCORE: {self.score}", True, c_PADDLE)
        lives_t = self.font_small.render(f"LIVES: {self.lives}", True, c_ACCENT)
        surface.blit(score_t, (20, 20))
        surface.blit(lives_t, (20, 50))
        
        # Pause Button
        if self.pause_btn.check_hover(mouse_pos) and click and self.state == "PLAYING":
            self.state = "PAUSED"
        self.pause_btn.draw(surface, self.font_small)

        # Draw Bricks
        for b in self.bricks:
            # Add a glow effect
            pygame.draw.rect(surface, b['color'], b['rect'], border_radius=5)
            pygame.draw.rect(surface, (255,255,255), b['rect'], 2, border_radius=5)

        # Draw Paddle
        pygame.draw.rect(surface, c_PADDLE, self.paddle_rect, border_radius=10)
        # Paddle Highlight
        pygame.draw.rect(surface, (200, 255, 255), (self.paddle_rect.x+5, self.paddle_rect.y+2, self.paddle_rect.w-10, 5), border_radius=5)

        # Draw Ball Trail
        for i, pos in enumerate(self.ball_trail):
            alpha = int(255 * (i / len(self.ball_trail)))
            radius = int(8 * (i / len(self.ball_trail)))
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*c_BALL, alpha), (radius, radius), radius)
            surface.blit(s, (pos[0]-radius, pos[1]-radius))

        # Draw Ball
        pygame.draw.circle(surface, c_BALL, self.ball_rect.center, 9)

        # Draw Particles & Powerups
        for p in self.particles: p.draw(surface)
        for f in self.floaters: f.draw(surface)
        for pup in self.powerups: pup.draw(surface, self.font_small)

        if not self.ball_active and self.lives > 0:
            msg = self.font_med.render("Press SPACE to Launch", True, (200, 200, 200))
            rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            surface.blit(msg, rect)

    def draw_overlay(self, surface, title_txt, sub_txt, color=(255, 255, 255)):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        surface.blit(overlay, (0,0))
        
        t = self.font_big.render(title_txt, True, color)
        r = t.get_rect(center=(SCREEN_WIDTH//2, 200))
        surface.blit(t, r)
        
        s = self.font_med.render(sub_txt, True, (255, 255, 255))
        sr = s.get_rect(center=(SCREEN_WIDTH//2, 280))
        surface.blit(s, sr)

if __name__ == "__main__":
    Game().run()