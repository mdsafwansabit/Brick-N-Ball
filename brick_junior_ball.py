import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 25
BRICK_PADDING = 10
BRICK_OFFSET_TOP = 50

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
BLUE = (60, 100, 255)
GREEN = (60, 255, 60)
YELLOW = (255, 255, 60)

# --- Game Classes ---

class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(
            (SCREEN_WIDTH // 2) - (PADDLE_WIDTH // 2),
            SCREEN_HEIGHT - 40,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )
        self.speed = 8

    def move(self, direction):
        if direction == "left":
            self.rect.x -= self.speed
        if direction == "right":
            self.rect.x += self.speed
        
        # Keep paddle inside screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2
        )
        self.dx = 4
        self.dy = -4  # Start moving up
        self.active = True

    def move(self):
        if not self.active:
            return

        self.rect.x += self.dx
        self.rect.y += self.dy

        # Wall collisions
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.dx *= -1
        if self.rect.top <= 0:
            self.dy *= -1
        
        # Bottom collision (Game Over condition)
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface):
        pygame.draw.ellipse(surface, WHITE, self.rect)


class BrickManager:
    def __init__(self):
        self.bricks = []
        self.create_bricks()

    def create_bricks(self):
        rows = 5
        cols = SCREEN_WIDTH // (BRICK_WIDTH + BRICK_PADDING)
        
        for row in range(rows):
            for col in range(cols):
                brick_x = col * (BRICK_WIDTH + BRICK_PADDING) + 35
                brick_y = row * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_OFFSET_TOP
                rect = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
                
                # Assign colors based on row
                if row < 2: color = RED
                elif row < 4: color = YELLOW
                else: color = GREEN
                
                self.bricks.append({'rect': rect, 'color': color})

    def draw(self, surface):
        for brick in self.bricks:
            pygame.draw.rect(surface, brick['color'], brick['rect'])


# --- Main Game Loop ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Brick Junior Ball")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    # Initialize objects
    paddle = Paddle()
    ball = Ball()
    brick_manager = BrickManager()

    running = True
    game_over = False
    won = False

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Restart game on spacebar if game over/won
            if event.type == pygame.KEYDOWN:
                if (game_over or won) and event.key == pygame.K_SPACE:
                    game_over = False
                    won = False
                    ball.reset()
                    brick_manager = BrickManager()

        # 2. Game Logic
        keys = pygame.key.get_pressed()
        if not game_over and not won:
            if keys[pygame.K_LEFT]:
                paddle.move("left")
            if keys[pygame.K_RIGHT]:
                paddle.move("right")

            ball.move()

            # Collision: Ball vs Paddle
            if ball.rect.colliderect(paddle.rect):
                ball.dy *= -1
                # Adjust position to prevent sticking
                ball.rect.bottom = paddle.rect.top 

            # Collision: Ball vs Bricks
            hit_index = ball.rect.collidelist([b['rect'] for b in brick_manager.bricks])
            if hit_index != -1:
                hit_brick = brick_manager.bricks.pop(hit_index)
                ball.dy *= -1
            
            # Check Game Over
            if not ball.active:
                game_over = True
            
            # Check Win
            if len(brick_manager.bricks) == 0:
                won = True

        # 3. Drawing
        screen.fill(BLACK)
        
        paddle.draw(screen)
        ball.draw(screen)
        brick_manager.draw(screen)

        # UI Messages
        if game_over:
            text = font.render("GAME OVER! Press SPACE to Restart", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(text, text_rect)
        elif won:
            text = font.render("YOU WIN! Press SPACE to Restart", True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60) # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()