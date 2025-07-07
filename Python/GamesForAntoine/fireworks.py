import pygame
import random
import math

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("New Year's Fireworks")

clock = pygame.time.Clock()


# Particle class for fireworks
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(3, 6)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 8)
        self.gravity = 0.2

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.speed -= 0.1  # Slow down the particle
        self.y += self.gravity  # Apply gravity
        self.radius -= 0.1  # Shrink the particle
        self.radius = max(0, self.radius)  # Prevent negative radius

    def draw(self, surface):
        if self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


class Fireworks:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        self.particles = [Particle(self.x, self.y, self.color) for _ in range(50)]
        self.exploded = False

    def explode(self):
        for particle in self.particles:
            particle.move()
        self.particles = [p for p in self.particles if p.radius > 0]  # Remove small particles
        if not self.particles:
            self.exploded = True

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


# Main game loop
def main():
    fireworks = []
    running = True

    while running:
        screen.fill((0, 0, 0))  # Clear screen for the next frame

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Add a new firework at random intervals
        if random.randint(1, 20) == 1:
            fireworks.append(Fireworks(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT // 2)))

        # Update and draw fireworks
        for firework in fireworks:
            firework.explode()
            firework.draw(screen)

        # Remove exploded fireworks
        fireworks = [fw for fw in fireworks if not fw.exploded]

        # Update display
        pygame.display.flip()

        # Control frame rate
        clock.tick(60)

    pygame.quit()


# Run the program
if __name__ == "__main__":
    main()
