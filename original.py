import pygame
import math
from collections import deque

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
MAX_BOUNCES = 3
MAX_BULLETS = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((4, 4))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 10
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        self.bounces = 0

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.vx = -self.vx
            self.bounces += 1

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.vy = -self.vy
            self.bounces += 1

        if self.bounces > MAX_BOUNCES:
            self.kill()

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ricochet Game")
    clock = pygame.time.Clock()

    # Game variables
    player_pos = (WIDTH // 2, HEIGHT // 2)
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets_queue = deque(maxlen=MAX_BULLETS)

    # Create some enemies
    for i in range(10):
        enemy = Enemy((i * 50 + 50, 50), enemies)

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if len(bullets) < MAX_BULLETS:
                    mouse_pos = pygame.mouse.get_pos()
                    angle = math.degrees(math.atan2(mouse_pos[1] - player_pos[1], mouse_pos[0] - player_pos[0]))
                    bullet = Bullet(player_pos, angle, bullets)
                    bullets_queue.append(bullet)
                else:
                    oldest_bullet = bullets_queue.popleft()
                    oldest_bullet.kill()

        # Update
        bullets.update()
        bullets.draw(screen)
        enemies.draw(screen)

        # Check for collisions
        for bullet in bullets:
            enemy_hit = pygame.sprite.spritecollide(bullet, enemies, True)
            if enemy_hit:
                bullet.kill()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
