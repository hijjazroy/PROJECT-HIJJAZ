"""
Harvest Rush: Falling Objects Catch Game
Course: SWC3643 Python Programming Language
Run: python main.py
Install dependency: pip install pygame
"""
import os
import random
import sys
import pygame

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 650
FPS = 60
GAME_SECONDS = 60
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Theme colours
NAVY = (20, 32, 55)
DARK = (12, 22, 39)
CREAM = (255, 246, 220)
GREEN = (76, 175, 80)
GOLD = (255, 193, 7)
RED = (235, 80, 75)
WHITE = (255, 255, 255)
MUTED = (185, 200, 215)


def load_image(filename, size=None):
    """Load an image from assets; use a safe fallback if it is missing."""
    path = os.path.join(ASSET_DIR, filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.smoothscale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        return None


def load_sound(filename):
    """Sound effects are optional; the game still works if audio is unavailable."""
    try:
        return pygame.mixer.Sound(os.path.join(ASSET_DIR, filename))
    except (pygame.error, FileNotFoundError):
        return None


class Player:
    """The basket controlled by the player."""

    def __init__(self):
        self.width = 112
        self.height = 72
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 105
        self.speed = 7
        self.image = load_image("basket.png", (self.width, self.height))

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        self.x = max(12, min(WIDTH - self.width - 12, self.x))

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, (173, 105, 48), self.rect, border_radius=12)
            pygame.draw.rect(surface, GOLD, self.rect, 4, border_radius=12)


class Item:
    """A falling object. Each type has its own score and gameplay effect."""

    TYPES = {
        "apple": {"image": "apple.png", "score": 10, "kind": "good"},
        "banana": {"image": "banana.png", "score": 15, "kind": "good"},
        "orange": {"image": "orange.png", "score": 10, "kind": "good"},
        "bomb": {"image": "bomb.png", "score": 0, "kind": "hazard"},
        "golden": {"image": "golden.png", "score": 30, "kind": "bonus"},
    }

    def __init__(self, level=1):
        self.item_type = random.choices(
            list(self.TYPES.keys()), weights=[28, 23, 23, 18, 8], k=1
        )[0]
        self.info = self.TYPES[self.item_type]
        self.size = 48
        self.x = random.randint(12, WIDTH - self.size - 12)
        self.y = -self.size
        self.speed = random.uniform(2.4, 4.0) + (level - 1) * 0.45
        self.image = load_image(self.info["image"], (self.size, self.size))

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            colour = RED if self.item_type == "bomb" else GREEN
            pygame.draw.circle(surface, colour, self.rect.center, self.size // 2)


class GameManager:
    """Controls the game loop, screens, score, lives, timer, and item rules."""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Harvest Rush - Falling Objects Catch Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 17)
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        self.big_font = pygame.font.SysFont("arial", 34, bold=True)
        self.language = "EN"
        self.state = "menu"
        self.running = True
        self.catch_sound = load_sound("catch.wav")
        self.miss_sound = load_sound("miss.wav")
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.items = []
        self.score = 0
        self.lives = 3
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.level = 1
        self.last_tick = pygame.time.get_ticks()
        self.state = "playing"

    def text(self, message, font, colour, center):
        image = font.render(message, True, colour)
        self.screen.blit(image, image.get_rect(center=center))

    def draw_background(self):
        self.screen.fill(NAVY)
        # Decorative stars/fruit-like dots
        for i in range(14):
            x = (i * 79 + 25) % WIDTH
            y = (i * 47 + 22) % (HEIGHT - 130)
            pygame.draw.circle(self.screen, (35, 54, 78), (x, y), 3)
        pygame.draw.rect(self.screen, (27, 45, 66), (0, HEIGHT - 125, WIDTH, 125))
        pygame.draw.line(self.screen, (74, 104, 116), (0, HEIGHT - 125),
                         (WIDTH, HEIGHT - 125), 3)

    def draw_hud(self):
        pygame.draw.rect(self.screen, DARK, (0, 0, WIDTH, 62))
        if self.language == "EN":
            labels = (f"Score: {self.score}", f"Lives: {self.lives}",
                      f"Time: {max(0, int(GAME_SECONDS - self.elapsed))}s",
                      f"Level: {self.level}")
        else:
            labels = (f"Mata: {self.score}", f"Nyawa: {self.lives}",
                      f"Masa: {max(0, int(GAME_SECONDS - self.elapsed))}s",
                      f"Tahap: {self.level}")
        positions = [105, 315, 545, 770]
        for label, x in zip(labels, positions):
            self.text(label, self.font, CREAM, (x, 31))

    def draw_button(self, label, rect, colour=GREEN):
        pygame.draw.rect(self.screen, colour, rect, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=12)
        self.text(label, self.font, WHITE, rect.center)

    def menu_screen(self):
        self.draw_background()
        self.text("HARVEST RUSH", self.title_font, GOLD, (WIDTH // 2, 145))
        subtitle = "Falling Objects Catch Game" if self.language == "EN" else "Permainan Menangkap Objek"
        self.text(subtitle, self.font, CREAM, (WIDTH // 2, 195))
        if self.language == "EN":
            self.text("Catch fruit. Avoid bombs. Beat the clock!", self.font, MUTED, (WIDTH // 2, 245))
            start, instructions, language, exit_text = "START GAME", "INSTRUCTIONS", "LANGUAGE: EN / BM", "EXIT"
        else:
            self.text("Tangkap buah. Elakkan bom. Kejar masa!", self.font, MUTED, (WIDTH // 2, 245))
            start, instructions, language, exit_text = "MULA PERMAINAN", "ARAHAN", "BAHASA: BM / EN", "KELUAR"
        self.draw_button(start, pygame.Rect(300, 300, 300, 52))
        self.draw_button(instructions, pygame.Rect(300, 370, 300, 52), (50, 110, 165))
        self.draw_button(language, pygame.Rect(300, 440, 300, 52), (110, 83, 150))
        self.draw_button(exit_text, pygame.Rect(300, 510, 300, 52), RED)
        pygame.display.flip()

    def instructions_screen(self):
        self.draw_background()
        if self.language == "EN":
            title = "HOW TO PLAY"
            lines = [
                "Move: LEFT / RIGHT arrow keys or A / D",
                "Catch apples, bananas and oranges for points.",
                "Golden fruit gives 30 bonus points.",
                "Avoid bombs. Missing fruit also costs one life.",
                "Press P to pause and R to restart.",
                "Survive for 60 seconds to win!",
                "Press ESC or ENTER to return to the menu."
            ]
        else:
            title = "CARA BERMAIN"
            lines = [
                "Gerak: kekunci anak panah atau A / D",
                "Tangkap epal, pisang dan oren untuk mata.",
                "Buah emas memberi 30 mata bonus.",
                "Elakkan bom. Buah terlepas mengurangkan nyawa.",
                "Tekan P untuk jeda dan R untuk mula semula.",
                "Bertahan selama 60 saat untuk menang!",
                "Tekan ESC atau ENTER untuk kembali ke menu."
            ]
        self.text(title, self.title_font, GOLD, (WIDTH // 2, 125))
        for i, line in enumerate(lines):
            self.text(line, self.small_font, CREAM, (WIDTH // 2, 220 + i * 43))
        pygame.display.flip()

    def end_screen(self):
        self.draw_background()
        won = self.elapsed >= GAME_SECONDS and self.lives > 0
        if self.language == "EN":
            title = "YOU WIN!" if won else "GAME OVER"
            prompt = "Press R to play again or ESC for menu"
            score_label = f"Final score: {self.score}"
        else:
            title = "ANDA MENANG!" if won else "PERMAINAN TAMAT"
            prompt = "Tekan R untuk bermain lagi atau ESC untuk menu"
            score_label = f"Mata akhir: {self.score}"
        self.text(title, self.title_font, GOLD if won else RED, (WIDTH // 2, 220))
        self.text(score_label, self.big_font, CREAM, (WIDTH // 2, 300))
        self.text(prompt, self.font, MUTED, (WIDTH // 2, 375))
        pygame.display.flip()

    def spawn_item(self):
        self.items.append(Item(self.level))

    def update_game(self, dt):
        self.elapsed += dt
        self.level = 1 + int(self.elapsed // 15)
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.spawn_timer += dt
        spawn_interval = max(0.32, 0.85 - (self.level - 1) * 0.10)
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            self.spawn_item()

        for item in self.items[:]:
            item.update()
            if item.rect.colliderect(self.player.rect):
                if item.item_type == "bomb":
                    self.lives -= 1
                    if self.miss_sound:
                        self.miss_sound.play()
                else:
                    self.score += item.info["score"]
                    if self.catch_sound:
                        self.catch_sound.play()
                self.items.remove(item)
            elif item.y > HEIGHT:
                if item.info["kind"] == "good":
                    self.lives -= 1
                    if self.miss_sound:
                        self.miss_sound.play()
                self.items.remove(item)

        if self.lives <= 0:
            self.state = "over"
        elif self.elapsed >= GAME_SECONDS:
            self.state = "over"

    def draw_game(self):
        self.draw_background()
        for item in self.items:
            item.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state in ("playing", "paused", "over", "instructions"):
                    self.state = "menu"
                else:
                    self.running = False
            elif event.key == pygame.K_p and self.state == "playing":
                self.state = "paused"
            elif event.key == pygame.K_p and self.state == "paused":
                self.state = "playing"
                self.last_tick = pygame.time.get_ticks()
            elif event.key == pygame.K_r and self.state in ("playing", "paused", "over"):
                self.reset_game()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.state == "instructions":
                self.state = "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if self.state == "menu":
                if pygame.Rect(300, 300, 300, 52).collidepoint(x, y):
                    self.reset_game()
                elif pygame.Rect(300, 370, 300, 52).collidepoint(x, y):
                    self.state = "instructions"
                elif pygame.Rect(300, 440, 300, 52).collidepoint(x, y):
                    self.language = "BM" if self.language == "EN" else "EN"
                elif pygame.Rect(300, 510, 300, 52).collidepoint(x, y):
                    self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)

            if self.state == "menu":
                self.menu_screen()
            elif self.state == "instructions":
                self.instructions_screen()
            elif self.state == "playing":
                self.update_game(dt)
                self.draw_game()
            elif self.state == "paused":
                self.draw_game()
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 175))
                self.screen.blit(overlay, (0, 0))
                label = "PAUSED - press P to continue" if self.language == "EN" else "DIJEDA - tekan P untuk sambung"
                self.text(label, self.big_font, CREAM, (WIDTH // 2, HEIGHT // 2))
                pygame.display.flip()
            elif self.state == "over":
                self.end_screen()
                # Keep the end screen responsive while waiting for a key.
                self.clock.tick(15)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    GameManager().run()
