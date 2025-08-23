import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Définition des paramètres
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()

# Couleurs
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# Classe pour le joueur
class Player:
    def __init__(self):
        self.width = 50
        self.height = 30
        self.x = screen_width // 2
        self.y = screen_height - self.height - 10
        self.speed = 5
        self.bullets = []

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

    def move(self, dx):
        self.x += dx
        self.x = max(0, min(self.x, screen_width - self.width))

    def shoot(self):
        bullet = pygame.Rect(self.x + self.width // 2, self.y, 5, 10)
        self.bullets.append(bullet)


# Classe pour les ennemis
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 30)
        self.active = True

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, RED, self.rect)


def main():
    player = Player()
    enemies = [Enemy(random.randint(0, screen_width - 40), random.randint(0, screen_height // 2)) for _ in range(5)]
    enemy_speed = 1
    score = 0
    level = 1

    # Boucle principale du jeu
    while True:
        screen.fill((0, 0, 0))

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.shoot()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-player.speed)
        if keys[pygame.K_RIGHT]:
            player.move(player.speed)

        # Mise à jour des tirs
        for bullet in player.bullets[:]:
            bullet.y -= 5
            if bullet.y < 0:
                player.bullets.remove(bullet)

        # Dessiner et vérifier les collisions des ennemis
        enemies_active = False
        for enemy in enemies:
            if enemy.active:
                enemies_active = True
                enemy.rect.y += enemy_speed
                enemy.draw()

            for bullet in player.bullets:
                if enemy.active and enemy.rect.colliderect(bullet):
                    enemy.active = False
                    player.bullets.remove(bullet)
                    score += 10

        # Vérifier si tous les ennemis sont désactivés
        if not enemies_active:
            level += 1
            enemy_speed += 1
            enemies = [Enemy(random.randint(0, screen_width - 40), random.randint(0, screen_height // 2)) for _ in range(5)]

        # Dessiner le joueur
        player.draw()

        # Dessiner les tirs
        for bullet in player.bullets:
            pygame.draw.rect(screen, WHITE, bullet)

        # Afficher le score et le niveau
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score} Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
