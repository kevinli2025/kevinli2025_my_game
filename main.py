import pygame
import math
from pygame.locals import *

pygame.init()

# Screen settings
WIDTH = 1100
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stupid Zombies Clone")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Game settings
FPS = 60
BULLET_SPEED = 8
MAX_BULLETS = 5
MAX_BOUNCES = 5
GRAVITY = 0.5

# Load images
gun_img = pygame.image.load("gun.png")
zombie_img = pygame.image.load("zombie.png")
platform_img = pygame.image.load("platform.png")

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, *groups):
        super().__init__(*groups)
        self.pos = pygame.math.Vector2(pos)
        self.angle = math.radians(angle)
        #self.vel = pygame.math.Vector2(-BULLET_SPEED * math.sin(self.angle), -BULLET_SPEED * math.cos(self.angle))
        self.vel = pygame.math.Vector2(BULLET_SPEED * math.cos(self.angle), -BULLET_SPEED * math.sin(self.angle))
        self.bounces = 0
        self.image = pygame.Surface((5, 5), pygame.SRCALPHA)
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.pos += self.vel
        self.rect.topleft = self.pos

        if self.bounces >= MAX_BOUNCES:
            self.kill()

        if not self.rect.colliderect(screen.get_rect()):
            self.bounces += 1
            if self.rect.left < 0:
                self.pos.x = 0
                self.vel.x *= -1
            if self.rect.right > WIDTH:
                self.pos.x = WIDTH - self.rect.width
                self.vel.x *= -1
            if self.rect.top < 0:
                self.pos.y = 0
                self.vel.y *= -1
            if self.rect.bottom > HEIGHT:
                self.pos.y = HEIGHT - self.rect.height
                self.vel.y *= -1

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.bounces += 1
                if abs(self.rect.left - platform.rect.right) < 5:
                    self.pos.x = platform.rect.right
                    self.vel.x *= -1
                if abs(self.rect.right - platform.rect.left) < 5:
                    self.pos.x = platform.rect.left - self.rect.width
                    self.vel.x *= -1
                if abs(self.rect.top - platform.rect.bottom) < 5:
                    self.pos.y = platform.rect.bottom
                    self.vel.y *= -1
                if abs(self.rect.bottom - platform.rect.top) < 5:
                    self.pos.y = platform.rect.top - self.rect.height
                    self.vel.y *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = platform_img
        self.rect = self.image.get_rect(topleft=pos)

class Zombie(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = zombie_img
        self.rect = self.image.get_rect(midbottom=pos)

class Gun:
    def __init__(self, pos):
        self.pos = pos
        self.angle = 0
        self.image = gun_img
        self.original_image = gun_img

    def update(self, mouse_pos):
        dx, dy = mouse_pos[0] - self.pos[0], self.pos[1] - mouse_pos[1]
        r = math.sqrt(dx*dx + dy*dy)
        self.angle = math.acos(dx/r) / math.pi * 180
        #self.angle = math.degrees(math.acos().atan2(dy, dx))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def create_level():
    global platforms, zombies
    platforms = [Platform((200, 400)), Platform((400, 300)), Platform((600, 200))]
    zombies = pygame.sprite.Group(
        Zombie((250, 390)), Zombie((450, 290)), Zombie((650, 190))
    )
    return platforms, zombies

def draw_text(surface, text, pos, font_size=30, color=WHITE):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def button(surface, text, pos, size, color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    pygame.draw.rect(surface, color, (pos[0], pos[1], size[0], size[1]))

    if pos[0] < mouse[0] < pos[0] + size[0] and pos[1] < mouse[1] < pos[1] + size[1]:
        pygame.draw.rect(surface, (255, 255, 0), (pos[0], pos[1], size[0], size[1]), 2)
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(surface, (0, 0, 0), (pos[0], pos[1], size[0], size[1]), 2)

    draw_text(surface, text, (pos[0] + 5, pos[1] + 5))

def restart_game():
    global bullets, killed_zombies, game_state, bullets_group
    for bullet in bullets_group:
        bullet.kill()
    bullets = MAX_BULLETS
    killed_zombies = 0
    game_state = "play"
    platforms, zombies = create_level()

def main():
    global bullets, killed_zombies, game_state, platforms, zombies, bullets_group
    clock = pygame.time.Clock()

    gun = Gun((WIDTH // 2, HEIGHT - 30))
    bullets_group = pygame.sprite.Group()
    platforms, zombies = create_level()
    init_zombie_count = len(zombies)
    killed_zombies = 0
    bullets = MAX_BULLETS
    game_state = "play"

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == MOUSEBUTTONDOWN:
                if game_state == "play" and bullets > 0:
                    bullet = Bullet(gun.rect.center, gun.angle, bullets_group)
                    if bullets > 0:
                        bullets -= 1
                    else: 
                        running = False
        
        if game_state == "play":
            gun.update(pygame.mouse.get_pos())
            bullets_group.update()
            bullets_group.draw(screen)

            for platform in platforms:
                screen.blit(platform.image, platform.rect)

            for zombie in zombies:
                screen.blit(zombie.image, zombie.rect)

            for bullet in bullets_group:
                hit_zombies = pygame.sprite.spritecollide(bullet, zombies, False)
                if hit_zombies:
                    hit_zombies[0].kill()
                    killed_zombies += 1

            if killed_zombies == init_zombie_count:
                game_state = "win"
            elif bullets == 0 and len(bullets_group) == 0:
                game_state = "lose"

        elif game_state == "win":
            draw_text(screen, "Good job!", (WIDTH // 2 - 50, HEIGHT // 2 - 20))
            button(screen, "Restart", (WIDTH // 2 - 50, HEIGHT // 2 + 20), (100, 30), GREEN, restart_game)

        elif game_state == "lose":
            draw_text(screen, "You failed!", (WIDTH // 2 - 50, HEIGHT // 2 - 20))
            button(screen, "Restart", (WIDTH // 2 - 50, HEIGHT // 2 + 20), (100, 30), RED, restart_game)

        gun.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
