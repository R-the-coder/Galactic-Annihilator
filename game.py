import pygame
import random
import sys
import math

# Cody: --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Cody: Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Cody: Player properties
PLAYER_SPEED = 7
PLAYER_SHOOT_COOLDOWN = 200 # Cody: milliseconds

# Cody: Enemy properties
ENEMY_SPEED = 1
ENEMY_SHOOT_COOLDOWN = 1000

# Cody: Power-up properties
POWERUP_DROP_CHANCE = 0.15 # Cody: 15% chance
POWERUP_DURATION = 5000 # Cody: 5 seconds in milliseconds

# Cody: --- Game Classes ---

class Player(pygame.sprite.Sprite):
    """Represents the player's ship."""
    def __init__(self, all_sprites, bullets):
        super().__init__()
        self.all_sprites = all_sprites
        self.bullets = bullets
        
        # Cody: Create a triangular ship
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, WHITE, [(20, 0), (0, 30), (40, 30)])
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH / 2, bottom=SCREEN_HEIGHT - 10)
        
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.last_shot_time = 0
        
        # Cody: Power-up status
        self.shield_active = False
        self.shield_end_time = 0
        self.rapid_fire_active = False
        self.rapid_fire_end_time = 0

    def update(self):
        # Cody: Handle key presses for movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE]:
            self.shoot()
            
        # Cody: Update power-up timers
        now = pygame.time.get_ticks()
        if self.shield_active and now > self.shield_end_time:
            self.shield_active = False
        if self.rapid_fire_active and now > self.rapid_fire_end_time:
            self.rapid_fire_active = False

    def shoot(self):
        now = pygame.time.get_ticks()
        cooldown = PLAYER_SHOOT_COOLDOWN / 2 if self.rapid_fire_active else PLAYER_SHOOT_COOLDOWN
        if now - self.last_shot_time > cooldown:
            self.last_shot_time = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)
            # Cody: Placeholder for sound effect
            # Cody: shoot_sound.play()

    def activate_shield(self):
        self.shield_active = True
        self.shield_end_time = pygame.time.get_ticks() + POWERUP_DURATION

    def activate_rapid_fire(self):
        self.rapid_fire_active = True
        self.rapid_fire_end_time = pygame.time.get_ticks() + POWERUP_DURATION

    def draw_shield_bar(self, surface):
        if self.shield_active:
            remaining_time = max(0, self.shield_end_time - pygame.time.get_ticks())
            bar_length = 100 * (remaining_time / POWERUP_DURATION)
            bar_rect = pygame.Rect(10, 40, bar_length, 10)
            pygame.draw.rect(surface, CYAN, bar_rect)
            
    def draw_rapid_fire_bar(self, surface):
        if self.rapid_fire_active:
            remaining_time = max(0, self.rapid_fire_end_time - pygame.time.get_ticks())
            bar_length = 100 * (remaining_time / POWERUP_DURATION)
            bar_rect = pygame.Rect(10, 60, bar_length, 10)
            pygame.draw.rect(surface, YELLOW, bar_rect)


class Enemy(pygame.sprite.Sprite):
    """Represents an enemy ship."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 5, 30, 15))
        pygame.draw.rect(self.image, RED, (10, 0, 10, 5))
        self.rect = self.image.get_rect(center=(x, y))
        self.x_speed = ENEMY_SPEED
        self.y_speed = 40 # Cody: How far to move down when hitting the edge

    def update(self):
        self.rect.x += self.x_speed

class Bullet(pygame.sprite.Sprite):
    """Represents a bullet shot by the player or an enemy."""
    def __init__(self, x, y, speed_y=-10, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = speed_y

    def update(self):
        self.rect.y += self.speed_y
        # Cody: Kill the bullet if it goes off-screen
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    """Represents a power-up dropped by an enemy."""
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(['shield', 'rapid_fire'])
        self.image = pygame.Surface((25, 25))
        if self.type == 'shield':
            pygame.draw.circle(self.image, CYAN, (12, 12), 12, 3)
        else: # Cody: rapid_fire
            pygame.draw.polygon(self.image, YELLOW, [(12, 0), (20, 15), (4, 15)])
        self.rect = self.image.get_rect(center=center)
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Particle(pygame.sprite.Sprite):
    """A single particle for explosion effects."""
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(random.choice([RED, YELLOW, WHITE]))
        self.rect = self.image.get_rect(center=center)
        self.velocity = pygame.math.Vector2(random.uniform(-3, 3), random.uniform(-3, 3))
        self.lifespan = 20 # Cody: frames
        
    def update(self):
        self.rect.move_ip(self.velocity)
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()

class Game:
    """The main game class that orchestrates everything."""
    def __init__(self):
        pygame.init()
        # Cody: pygame.mixer.init() # Cody: For sounds
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Galactic Annihilator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.game_state = "START_MENU"
        
        # Cody: Game variables
        self.level = 1
        self.enemy_shoot_timer = 0
        self.screen_shake = 0

        # Cody: Background stars
        self.stars = [{'x': random.randint(0, SCREEN_WIDTH), 
                       'y': random.randint(0, SCREEN_HEIGHT), 
                       'speed': random.uniform(0.5, 2)} for _ in range(200)]

    def create_explosion(self, center):
        for _ in range(30):
            particle = Particle(center)
            self.all_sprites.add(particle)
            
    def new_game(self):
        """Resets the game to its initial state."""
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.player = Player(self.all_sprites, self.bullets)
        self.all_sprites.add(self.player)
        
        self.player.score = 0
        self.level = 1
        self.player.lives = 3
        
        self.spawn_wave()
        self.game_state = "PLAYING"
        
    def spawn_wave(self):
        """Spawns a new wave of enemies."""
        num_enemies_x = self.level + 5
        num_enemies_y = 2 + (self.level // 2)
        
        for row in range(num_enemies_y):
            for col in range(num_enemies_x):
                x = 50 + col * 50
                y = 50 + row * 40
                enemy = Enemy(x, y)
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)

    def draw_text(self, text, size, x, y, color=WHITE, center=False):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_ui(self):
        # Cody: Score
        self.draw_text(f"Score: {self.player.score}", 30, SCREEN_WIDTH - 150, 10)
        # Cody: Lives
        self.draw_text(f"Lives: {self.player.lives}", 30, 10, 10)
        # Cody: Level
        self.draw_text(f"Level: {self.level}", 30, SCREEN_WIDTH / 2 - 50, 10)
        # Cody: Power-up bars
        self.player.draw_shield_bar(self.screen)
        self.player.draw_rapid_fire_bar(self.screen)


    def draw_background(self):
        self.screen.fill(BLACK)
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(self.screen, WHITE, (star['x'], star['y']), 1)

    def run(self):
        """The main game loop."""
        while self.running:
            self.clock.tick(FPS)
            
            if self.game_state == "START_MENU":
                self.handle_start_menu_events()
                self.draw_start_menu()
            elif self.game_state == "PLAYING":
                self.handle_playing_events()
                self.update_game_state()
                self.draw_game()
            elif self.game_state == "GAME_OVER":
                self.handle_game_over_events()
                self.draw_game_over_screen()
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """General event handling."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def handle_start_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.new_game()

    def handle_playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = "START_MENU"

    def handle_game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.new_game()
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "START_MENU"
    
    def update_game_state(self):
        """Update all game objects and check for collisions."""
        self.all_sprites.update()

        # Cody: --- Collision Detection ---

        # Cody: Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.player.score += 100
            self.create_explosion(hit.rect.center)
            # Cody: Placeholder for sound effect
            # Cody: explosion_sound.play()
            if random.random() < POWERUP_DROP_CHANCE:
                powerup = PowerUp(hit.rect.center)
                self.all_sprites.add(powerup)
                self.powerups.add(powerup)

        # Cody: Player hitting power-ups
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                self.player.activate_shield()
            elif hit.type == 'rapid_fire':
                self.player.activate_rapid_fire()
            # Cody: Placeholder for sound effect
            # Cody: powerup_sound.play()

        # Cody: Enemy bullets hitting player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits and not self.player.shield_active:
            self.player.lives -= 1
            self.screen_shake = 20 # Cody: Activate screen shake
            self.create_explosion(self.player.rect.center)
            if self.player.lives <= 0:
                self.game_state = "GAME_OVER"
        
        # Cody: --- Enemy Logic ---
        
        # Cody: Enemy movement: If any enemy hits the side, all reverse and move down
        reverse_direction = False
        for enemy in self.enemies:
            if enemy.rect.right > SCREEN_WIDTH or enemy.rect.left < 0:
                reverse_direction = True
                break
        if reverse_direction:
            for enemy in self.enemies:
                enemy.x_speed *= -1
                enemy.rect.y += enemy.y_speed

        # Cody: Enemy shooting
        self.enemy_shoot_timer += self.clock.get_time()
        cooldown = max(100, ENEMY_SHOOT_COOLDOWN - self.level * 50)
        if self.enemy_shoot_timer > cooldown and len(self.enemies) > 0:
            self.enemy_shoot_timer = 0
            shooter = random.choice(self.enemies.sprites())
            bullet = Bullet(shooter.rect.centerx, shooter.rect.bottom, speed_y=5, color=RED)
            self.all_sprites.add(bullet)
            self.enemy_bullets.add(bullet)
            
        # Cody: Check if all enemies are defeated
        if not self.enemies:
            self.level += 1
            self.spawn_wave()
            
    def draw_game(self):
        """Draws all elements for the main game screen."""
        self.draw_background()

        # Cody: Screen shake effect
        render_offset = [0, 0]
        if self.screen_shake > 0:
            self.screen_shake -= 1
            render_offset[0] = random.randint(-4, 4)
            render_offset[1] = random.randint(-4, 4)

        # Cody: Draw all sprites with the offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(render_offset))

        # Cody: Draw player shield
        if self.player.shield_active:
            pygame.draw.circle(self.screen, CYAN, self.player.rect.center, 30, 2)
        
        self.draw_ui()

    def draw_start_menu(self):
        self.draw_background()
        self.draw_text("GALACTIC ANNIHILATOR", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, center=True)
        self.draw_text("Use Arrow Keys to Move, Space to Shoot", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
        self.draw_text("Press ENTER to Begin", 40, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, center=True)

    def draw_game_over_screen(self):
        self.draw_background()
        self.draw_text("GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, color=RED, center=True)
        self.draw_text(f"Final Score: {self.player.score}", 40, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, center=True)
        self.draw_text("Press ENTER to Play Again", 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, center=True)
        self.draw_text("Press ESC to Return to Menu", 24, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4 + 40, center=True)

# Cody: --- Main Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()
