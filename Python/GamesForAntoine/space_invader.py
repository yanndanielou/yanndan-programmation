# Jeu Space Invader complet avec gestion du clavier, tirs, niveaux, difficulté et score
import pygame
import sys
import random

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invader")

# Couleurs
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Joueur
player_width, player_height = 50, 30
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
player_speed = 7

# Tir du joueur
bullet_width, bullet_height = 5, 15
bullet_speed = 10
bullets = []  # Liste des tirs actifs
can_shoot = True
shoot_cooldown = 300  # ms
last_shot_time = 0

# Ennemis
enemy_width, enemy_height = 40, 30
enemy_rows = 4
enemy_cols = 8
enemy_padding = 20
enemy_offset_x = 60
enemy_offset_y = 60
enemy_speed = 1.0
enemy_direction = 1  # 1 = droite, -1 = gauche
enemies = []

# Score et niveau
score = 0
level = 1
font = pygame.font.SysFont(None, 36)


# Générer les ennemis
def create_enemies():
    global enemies
    enemies = []
    for row in range(enemy_rows):
        for col in range(enemy_cols):
            x = enemy_offset_x + col * (enemy_width + enemy_padding)
            y = enemy_offset_y + row * (enemy_height + enemy_padding)
            enemies.append({"rect": pygame.Rect(x, y, enemy_width, enemy_height), "alive": True})


create_enemies()


# Fonction pour passer au niveau suivant
def advance_level():
    global level, enemy_speed, enemy_rows, score
    level += 1
    enemy_speed += 0.5
    if level % 3 == 0:
        # Ajoute une ligne d'ennemis tous les 3 niveaux
        global enemy_rows
        enemy_rows += 1
    create_enemies()


# Boucle principale du jeu
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BLACK)
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôle du joueur
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
        player_x += player_speed
    # Tir
    if keys[pygame.K_SPACE] and can_shoot:
        now = pygame.time.get_ticks()
        if now - last_shot_time > shoot_cooldown:
            bullet_rect = pygame.Rect(player_x + player_width // 2 - bullet_width // 2, player_y, bullet_width, bullet_height)
            bullets.append(bullet_rect)
            last_shot_time = now

    # Mettre à jour les tirs
    for bullet in bullets[:]:
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)

    # Déplacement des ennemis
    move_down = False
    for enemy in enemies:
        if enemy["alive"]:
            enemy["rect"].x += enemy_speed * enemy_direction
            if enemy["rect"].right >= screen_width or enemy["rect"].left <= 0:
                move_down = True
    if move_down:
        enemy_direction *= -1
        for enemy in enemies:
            if enemy["alive"]:
                enemy["rect"].y += enemy_height // 2

    # Collision tirs/ennemis
    for bullet in bullets[:]:
        for enemy in enemies:
            if enemy["alive"] and enemy["rect"].colliderect(bullet):
                enemy["alive"] = False
                bullets.remove(bullet)
                score += 10
                break

    # Vérifier si tous les ennemis sont morts
    if all(not enemy["alive"] for enemy in enemies):
        advance_level()

    # Vérifier si un ennemi atteint le joueur
    for enemy in enemies:
        if enemy["alive"] and enemy["rect"].bottom >= player_y:
            running = False  # Game over

    # Affichage du joueur
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
    # Affichage des tirs
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet)
    # Affichage des ennemis
    for enemy in enemies:
        if enemy["alive"]:
            pygame.draw.rect(screen, RED, enemy["rect"])

    # Affichage du score et du niveau
    score_text = font.render(f"Score : {score}", True, WHITE)
    level_text = font.render(f"Niveau : {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

# Affichage Game Over
screen.fill(BLACK)
game_over_text = font.render("GAME OVER", True, WHITE)
score_text = font.render(f"Score final : {score}", True, WHITE)
screen.blit(game_over_text, (screen_width // 2 - 100, screen_height // 2 - 40))
screen.blit(score_text, (screen_width // 2 - 100, screen_height // 2))
pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
sys.exit()
