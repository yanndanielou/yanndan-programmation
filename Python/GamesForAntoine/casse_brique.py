import pygame
import pygame.constants
from pygame.locals import K_EQUALS, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT, KEYDOWN, K_SPACE, K_MINUS, K_PLUS, K_KP_MINUS, K_KP_PLUS, K_p, K_a, K_s, K_o  # pylint: disable=[no-name-in-module]
import sys
import json
import random
from typing import List, Dict

from logger import logger_config

LEVELS_FILE_NAME = "casse_brique_levels.json"


class CasseBrique:
    def __init__(self) -> None:
        # Initialisation de Pygame
        pygame.init()

        # Charger les niveaux depuis le fichier JSON
        self.levels = self.load_levels()

        # Définir les paramètres de la fenêtre
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Casse-Brique")

        self.clock = pygame.time.Clock()

        # Barre d'état
        self.status_bar_height = 40
        self.menu_bar_height = 20

        # Couleurs
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        # Configuration menu
        self.menu_items = [
            {"label": "Ralentir balle", "shortcut": "S", "action": self.reduce_ball_speed},
            {"label": "Suppr. brique aléatoire", "shortcut": "P", "action": self.remove_random_brick},
            {"label": "Suppr. toutes briques", "shortcut": "A", "action": self.remove_all_bricks},
            {"label": "Modifier taille paddle", "shortcut": "O", "action": self.prompt_paddle_size},
            {"label": "Paddle -10", "shortcut": "-", "action": lambda: self.change_paddle_width(-10)},
            {"label": "Paddle +10", "shortcut": "+", "action": lambda: self.change_paddle_width(10)},
        ]
        self.menu_buttons = []

        # Initialiser le jeu
        self.reset_game()

    def load_levels(self) -> List[Dict]:
        logger_config.print_and_log_info(f"Load levels from file {LEVELS_FILE_NAME}")
        with open(LEVELS_FILE_NAME, "r") as file:
            return json.load(file)

    def reset_game(self) -> None:
        logger_config.print_and_log_info("reset_game")

        self.level_index = 0
        self.score = 0
        self.lives = 3
        self.setup_level(self.level_index)

    def setup_level(self, level_index: int) -> None:
        logger_config.print_and_log_info(f"setup_level {level_index}")

        level_data = self.levels[level_index]
        self.paddle = pygame.Rect(
            self.screen_width // 2 - level_data["player_width"] // 2,
            self.screen_height - 30 - self.status_bar_height,
            level_data["player_width"],
            level_data["player_height"],
        )
        self.paddle_speed = level_data["player_speed"]

        self.ball = pygame.Rect(
            self.screen_width // 2,
            self.screen_height // 2,
            level_data["ball_size"],
            level_data["ball_size"],
        )
        self.ball_speed_x = level_data["ball_speed_x"]
        self.ball_speed_y = level_data["ball_speed_y"]

        self.bricks: List[pygame.Rect] = []
        self.create_bricks(level_data["brick_configuration"])

    def create_bricks(self, config: List[List[int]]) -> None:
        self.bricks.clear()
        for i, row in enumerate(config):
            for j, brick_present in enumerate(row):
                if brick_present:
                    brick = pygame.Rect(
                        j * 100 + 10,
                        i * 30 + 10 + self.status_bar_height + self.menu_bar_height,
                        80,
                        20,
                    )
                    self.bricks.append(brick)

    def run(self) -> None:
        while True:
            self.handle_events()
            self.update_game()
            self.draw_game()
            self.clock.tick(60)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_p:
                    # raccourci po: supprimer une brique aléatoire
                    self.remove_random_brick()
                elif event.key == K_a:
                    # supprimer toutes les briques
                    self.remove_all_bricks()
                elif event.key == K_s:
                    # diminuer la vitesse de la balle
                    self.reduce_ball_speed()
                elif event.key == K_o:
                    # modifier taille de la raquette (popup)
                    self.prompt_paddle_size()
                elif event.key == K_MINUS or event.key == K_KP_MINUS:
                    self.change_paddle_width(-10)
                elif event.key == K_PLUS or event.key == K_EQUALS or event.key == K_KP_PLUS:
                    self.change_paddle_width(10)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                logger_config.print_and_log_info(f"Mouse button down")
                mouse_x, mouse_y = event.pos
                if self.status_bar_height <= mouse_y <= self.status_bar_height + self.menu_bar_height:
                    for button in self.menu_buttons:
                        if button["rect"].collidepoint(mouse_x, mouse_y):
                            logger_config.print_and_log_info(f"Clicked on {button["action"]} button")
                            button["action"]()
                            break
                    continue

                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_ALT:
                    for brick in list(self.bricks):
                        if brick.collidepoint(mouse_x, mouse_y):
                            self.bricks.remove(brick)
                            self.score += 10
                            break

    def update_game(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.paddle.x -= self.paddle_speed
        if keys[pygame.K_RIGHT]:
            self.paddle.x += self.paddle_speed

        # Confinement de la raquette à l'écran
        self.paddle.x = max(0, min(self.paddle.x, self.screen_width - self.paddle.width))

        # Mouvement de la balle
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        # Collision avec les murs
        if self.ball.x <= 0 or self.ball.x >= self.screen_width - self.ball.width:
            self.ball_speed_x *= -1
        if self.ball.y <= self.status_bar_height + self.menu_bar_height:
            self.ball_speed_y *= -1

        # Collision avec la raquette
        if self.ball.colliderect(self.paddle):
            self.ball_speed_y *= -1

        # Collision avec les briques
        self.check_bricks_collision()

        # Balle perdue
        if self.ball.y >= self.screen_height:
            self.on_ball_lost()

        # Passage au niveau suivant
        if not self.bricks:
            self.switch_to_next_level()

    def check_bricks_collision(self) -> None:
        for brick in self.bricks:
            if self.ball.colliderect(brick):
                self.on_brick_touched(brick)
                break

    def on_brick_touched(self, brick: pygame.Rect) -> None:
        self.ball_speed_y *= -1
        self.bricks.remove(brick)
        self.score += 10

    def on_ball_lost(self) -> None:
        self.lives -= 1
        logger_config.print_and_log_info(f"Ball lost!. Now: {self.lives} lives")
        if self.lives > 0:
            self.ball.x, self.ball.y = self.screen_width // 2, self.screen_height // 2
            logger_config.print_and_log_info("Put back ball on field")

        else:
            logger_config.print_and_log_info("Game over")

            self.show_game_over()

    def switch_to_next_level(self) -> None:
        self.level_index += 1
        logger_config.print_and_log_info(f"Switch to next level {self.level_index}")

        if self.level_index < len(self.levels):
            self.setup_level(self.level_index)
        else:
            logger_config.print_and_log_info(f"All Levels Complete! Total Score:{self.score}")
            self.reset_game()

    def reduce_ball_speed(self) -> None:
        self.ball_speed_x *= 0.8
        self.ball_speed_y *= 0.8
        logger_config.print_and_log_info(f"Ball speed reduced: ({self.ball_speed_x:.2f}, {self.ball_speed_y:.2f})")

    def remove_random_brick(self) -> None:
        if self.bricks:
            random_brick = random.choice(self.bricks)
            self.bricks.remove(random_brick)
            self.score += 10
            logger_config.print_and_log_info("Random brick removed")

    def remove_all_bricks(self) -> None:
        removed = len(self.bricks)
        self.bricks.clear()
        self.score += removed * 10
        logger_config.print_and_log_info(f"All bricks removed ({removed})")

    def change_paddle_width(self, delta: int) -> None:
        min_width = 20
        max_width = self.screen_width
        new_width = max(min_width, min(max_width, self.paddle.width + delta))
        self.paddle.width = new_width
        self.paddle.x = max(0, min(self.screen_width - self.paddle.width, self.paddle.x))
        logger_config.print_and_log_info(f"Paddle width changed to {new_width}")

    def prompt_paddle_size(self) -> None:
        prompt_text = "Entrez nouvelle largeur de la raquette (20-800) :"
        current_input = ""
        running = True

        while running:
            self.screen.fill((0, 0, 0))
            self.draw_menu_bar()

            font = pygame.font.SysFont(None, 32)
            prompt_surface = font.render(prompt_text, True, self.WHITE)
            input_surface = font.render(current_input + "_", True, self.WHITE)

            self.screen.blit(prompt_surface, (20, 120))
            self.screen.blit(input_surface, (20, 160))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            new_width = int(current_input)
                            if 20 <= new_width <= self.screen_width:
                                self.paddle.width = new_width
                                self.paddle.x = max(0, min(self.screen_width - self.paddle.width, self.paddle.x))
                                logger_config.print_and_log_info(f"Paddle width set by prompt: {new_width}")
                                running = False
                            else:
                                current_input = ""
                        except ValueError:
                            current_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        current_input = current_input[:-1]
                    elif event.unicode.isdigit():
                        current_input += event.unicode
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.clock.tick(30)

    def draw_menu_bar(self) -> None:
        menu_height = self.menu_bar_height
        pygame.draw.rect(self.screen, (50, 50, 50), (0, self.status_bar_height, self.screen_width, menu_height))
        font = pygame.font.SysFont(None, 20)

        self.menu_buttons = []
        x = 10
        for item in self.menu_items:
            label_text = f"{item['shortcut']} : {item['label']}"
            text_surface = font.render(label_text, True, self.WHITE)
            self.screen.blit(text_surface, (x, self.status_bar_height + (menu_height - text_surface.get_height()) // 2))

            button_rect = pygame.Rect(x - 5, self.status_bar_height, text_surface.get_width() + 10, menu_height)
            self.menu_buttons.append({"rect": button_rect, "action": item["action"]})

            x += text_surface.get_width() + 20

    def draw_game(self) -> None:
        self.screen.fill((0, 0, 0))

        # Barre d'état en haut de l'écran
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, self.screen_width, self.status_bar_height))

        font = pygame.font.SysFont(None, 32)
        score_text = font.render(f"Score: {self.score}", True, self.WHITE)
        level_text = font.render(f"Niveau: {self.level_index + 1}", True, self.WHITE)
        lives_text = font.render(f"Vies: {self.lives}", True, self.WHITE)

        sep = 20
        x = 10
        self.screen.blit(score_text, (x, (self.status_bar_height - score_text.get_height()) // 2))
        x += score_text.get_width() + sep
        self.screen.blit(level_text, (x, (self.status_bar_height - level_text.get_height()) // 2))
        x += level_text.get_width() + sep
        self.screen.blit(lives_text, (x, (self.status_bar_height - lives_text.get_height()) // 2))

        # Barre de menu
        self.draw_menu_bar()

        # Dessiner la zone de jeu
        pygame.draw.rect(self.screen, self.GREEN, self.paddle)
        pygame.draw.ellipse(self.screen, self.WHITE, self.ball)

        for brick in self.bricks:
            pygame.draw.rect(self.screen, self.RED, brick)

        pygame.display.flip()

    def show_game_over(self) -> None:
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 48)
        text1 = font_big.render("GAME OVER", True, self.RED)
        text2 = font_small.render(f"Score: {self.score}", True, self.WHITE)
        text3 = font_small.render("Appuyez sur espace pour quitter", True, self.WHITE)

        self.screen.blit(text1, ((self.screen_width - text1.get_width()) // 2, 200))
        self.screen.blit(text2, ((self.screen_width - text2.get_width()) // 2, 300))
        self.screen.blit(text3, ((self.screen_width - text3.get_width()) // 2, 380))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
            self.clock.tick(30)

        pygame.quit()
        sys.exit()


def main() -> None:
    with logger_config.application_logger(log_file_suffix_before_extension="casse_brique"):
        CasseBrique().run()


if __name__ == "__main__":
    main()
