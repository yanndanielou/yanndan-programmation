import pygame
import sys
import json
from typing import List, Dict


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

        # Couleurs
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        # Initialiser le jeu
        self.reset_game()

    def load_levels(self) -> List[Dict]:
        with open("casse_brique_levels.json", "r") as file:
            return json.load(file)

    def reset_game(self):
        self.level_index = 0
        self.score = 0
        self.lives = 3
        self.setup_level(self.level_index)

    def setup_level(self, index: int):
        level_data = self.levels[index]
        self.paddle = pygame.Rect(self.screen_width // 2 - level_data["player_width"] // 2, self.screen_height - 30, level_data["player_width"], level_data["player_height"])
        self.paddle_speed = level_data["player_speed"]

        self.ball = pygame.Rect(self.screen_width // 2, self.screen_height // 2, level_data["ball_size"], level_data["ball_size"])
        self.ball_speed_x = level_data["ball_speed_x"]
        self.ball_speed_y = level_data["ball_speed_y"]

        self.bricks = []
        self.create_bricks(level_data["brick_configuration"])

    def create_bricks(self, config: List[List[int]]):
        self.bricks.clear()
        for i, row in enumerate(config):
            for j, brick_present in enumerate(row):
                if brick_present:
                    brick = pygame.Rect(j * 100 + 10, i * 30 + 10, 80, 20)
                    self.bricks.append(brick)

    def run(self):
        while True:
            self.handle_events()
            self.update_game()
            self.draw_game()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update_game(self):
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
        if self.ball.y <= 0:
            self.ball_speed_y *= -1

        # Collision avec la raquette
        if self.ball.colliderect(self.paddle):
            self.ball_speed_y *= -1

        # Collision avec les briques
        for brick in self.bricks:
            if self.ball.colliderect(brick):
                self.ball_speed_y *= -1
                self.bricks.remove(brick)
                self.score += 10
                break

        # Balle perdue
        if self.ball.y >= self.screen_height:
            self.lives -= 1
            if self.lives > 0:
                self.ball.x, self.ball.y = self.screen_width // 2, self.screen_height // 2
            else:
                print("Game Over! Score:", self.score)
                self.reset_game()

        # Passage au niveau suivant
        if not self.bricks:
            self.level_index += 1
            if self.level_index < len(self.levels):
                self.setup_level(self.level_index)
            else:
                print("All Levels Complete! Total Score:", self.score)
                self.reset_game()

    def draw_game(self):
        self.screen.fill((0, 0, 0))

        pygame.draw.rect(self.screen, self.GREEN, self.paddle)
        pygame.draw.ellipse(self.screen, self.WHITE, self.ball)

        for brick in self.bricks:
            pygame.draw.rect(self.screen, self.RED, brick)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score} Level: {self.level_index + 1} Lives: {self.lives}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()


if __name__ == "__main__":
    CasseBrique().run()
