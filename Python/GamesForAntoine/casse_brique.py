import pygame
import sys


class CasseBrique:
    def __init__(self):
        # Initialisation de Pygame
        pygame.init()

        # Définition des paramètres
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

    def reset_game(self):
        # Etats de jeu
        self.level = 1
        self.score = 0
        self.lives = 3

        # Joueur
        self.paddle = pygame.Rect(self.screen_width // 2 - 50, self.screen_height - 30, 100, 10)
        self.paddle_speed = 5

        # Ball
        self.ball = pygame.Rect(self.screen_width // 2, self.screen_height // 2, 10, 10)
        self.ball_speed_x = 3
        self.ball_speed_y = 3

        # Briques
        self.bricks = []
        self.create_bricks()

    def create_bricks(self):
        for i in range(5):
            for j in range(8):
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
            self.level += 1
            self.ball_speed_x *= 1.1
            self.ball_speed_y *= 1.1
            self.create_bricks()

    def draw_game(self):
        self.screen.fill((0, 0, 0))

        pygame.draw.rect(self.screen, self.GREEN, self.paddle)
        pygame.draw.ellipse(self.screen, self.WHITE, self.ball)

        for brick in self.bricks:
            pygame.draw.rect(self.screen, self.RED, brick)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score} Level: {self.level} Lives: {self.lives}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()


if __name__ == "__main__":
    CasseBrique().run()
