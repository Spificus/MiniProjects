import pygame
import sys
import math
import random

RED = '\033[31m'   # Red text
GREEN = '\033[32m'  # Green text
BLUE = '\033[34m'  # Blue text
RESET = '\033[0m'  # Reset to default color

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

# Set up the window
width, height = 1000, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pygame Advanced Example')

# Color Definitions
COLORS = {'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0),
          'green': (0, 128, 0), 'blue': (0, 0, 128), 'orange': (255, 165, 0)}


class Button:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (255, 165, 0)  # Orange color

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 40)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (self.rect.x + (self.rect.width / 2 - text.get_width() / 2),
                            self.rect.y + (self.rect.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        return self.rect.collidepoint(pos)


class Food:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.color = COLORS['green']
        self.speed = 0.75
        self.duration = 3000
        self.consumed = False
        self.rect = pygame.Rect(x, y, 8, 8)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self):
        self.pos[1] += self.speed
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

    def collision_with_bounds(self):
        if self.pos[0] <= 0 or self.pos[0] >= width - 5 or self.pos[1] <= 0 or self.pos[1] >= height - 5:
            return True
        return False


class Character:
    def __init__(self, x, y, size, speed, color):
        self.pos = pygame.Vector2(x, y)
        self.size = size
        self.speed = speed
        self.color = color
        self.destroyed = False
        self.rect = pygame.Rect(x, y, size, size)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self, dx, dy):
        movement = pygame.Vector2(dx, dy)
        self.pos += movement
        self.rect.topleft = self.pos

    def grow(self):
        self.size += 12
        self.rect.size = (self.size, self.size)

    def collision_with_bounds(self, width, height):
        if self.pos.x <= 0 or self.pos.x >= width - self.size or self.pos.y <= 0 or self.pos.y >= height - self.size:
            return True
        return False


class Player(Character):
    def handle_keys(self, width, height):
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.pos.x >= 0:
            movement.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.pos.x <= width - self.size:
            movement.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.pos.y >= 0:
            movement.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.pos.y <= height - self.size:
            movement.y += self.speed

        self.move(movement.x, movement.y)


class AI(Character):
    def __init__(self, x, y, size, speed, color):
        super().__init__(x, y, size, speed, color)
        self.sight = 275
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self.change_direction_counter = 0
        self.up_counter = 0
        self.left_counter = 0

    def move_ai(self, width, height):
        if self.change_direction_counter <= 0:
            self.direction = random.choice(['left', 'right', 'up', 'down'])
            self.change_direction_counter = random.randint(1, 70)
        else:
            self.change_direction_counter -= 1

        movement = pygame.Vector2(0, 0)

        # Directional movement logic using Vector2 for clarity and simplicity
        if self.direction == 'left' and self.pos.x >= 0:
            movement.x -= self.speed
        elif self.direction == 'right' and self.pos.x <= width - self.size:
            movement.x += self.speed
        elif self.direction == 'up' and self.pos.y >= 0:
            movement.y -= self.speed
        elif self.direction == 'down' and self.pos.y <= height - self.size:
            movement.y += self.speed

        self.move(movement.x, movement.y)

    def move_towards(self, target_pos):
        movement = pygame.Vector2(0, 0)
        horizontal_distance = abs(self.pos[0] - target_pos[0])
        vertical_distance = abs(self.pos[1] - target_pos[1])

        if horizontal_distance > vertical_distance:
            # Move horizontally
            if self.pos[0] < target_pos[0] and self.pos[0] <= width - self.size:
                movement.x = self.speed
            elif self.pos[0] > target_pos[0] and self.pos[0] >= 0:
                movement.x = -self.speed

        else:
            # Move vertically
            if self.pos[1] < target_pos[1] and self.pos[1] <= height - self.size:
                movement.y = self.speed
            elif self.pos[1] > target_pos[1] and self.pos[1] >= 0:
                movement.y = -self.speed

        self.move(movement.x, movement.y)

    def move_away(self, target_pos):
        movement = pygame.Vector2(0, 0)
        horizontal_distance = abs(self.pos[0] - target_pos[0])
        vertical_distance = abs(self.pos[1] - target_pos[1])

        if horizontal_distance > vertical_distance:
            # Move horizontally
            if self.pos[0] <= target_pos[0] and self.pos[0] >= 0:
                movement.x = -self.speed
            elif self.pos[0] > target_pos[0] and self.pos[0] <= width - self.size:
                movement.x = self.speed
        else:
            # Move vertically
            if self.pos[1] <= target_pos[1] and self.pos[1] >= 0:
                movement.y = -self.speed
            elif self.pos[1] > target_pos[1] and self.pos[1] <= height - self.size:
                movement.y = self.speed

        self.move(movement.x, movement.y)


def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


def coordinate_ai_movement(ai, food_list, player):
    if player.destroyed:
        player_in_sight = False
    else:
        player_in_sight = calculate_distance(ai.pos, player.pos) < ai.sight

    if player_in_sight:
        if ai.size > player.size:
            ai.move_towards(player.pos)
        elif ai.size < player.size:
            ai.move_away(player.pos)
        else:
            closest_food = None
            min_distance = float('inf')
            for food in food_list:
                distance = calculate_distance(ai.pos, food.pos)
                if distance < min_distance:
                    min_distance = distance
                    closest_food = food

            if closest_food is not None:
                ai.move_towards(closest_food.pos)
            else:
                ai.move_ai(width, height)
    else:
        closest_food = None
        min_distance = float('inf')
        for food in food_list:
            distance = calculate_distance(ai.pos, food.pos)
            if distance < min_distance:
                min_distance = distance
                closest_food = food

        if closest_food is not None:
            ai.move_towards(closest_food.pos)
        else:
            ai.move_ai(width, height)


def render(characters, food_list, background_color):
    # Render
    screen.fill(background_color)

    for character in characters:
        if character.destroyed == False:
            character.draw(screen)

    for food in food_list:
        food.duration -= 1
        food.move()
        food.draw()

    pygame.display.flip()


def title_screen(screen, title, text):
    running = True
    title_font = pygame.font.SysFont('comicsans', 70)
    sub_text_font = pygame.font.SysFont('comicsans', 20)
    start_btn = Button(width // 2 - 100, height // 2, 200, 50, 'Start')

    while running:
        screen.fill(COLORS['black'])
        title_text = title_font.render(title, 1, COLORS['white'])
        sub_text = sub_text_font.render(text, 1, COLORS['white'])
        screen.blit(title_text, (width // 2 -
                    title_text.get_width() // 2, 100))
        screen.blit(sub_text, (width // 2 -
                    sub_text.get_width() // 2, 200))

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.is_over(pos):
                    running = False

        start_btn.draw(screen)
        pygame.display.update()


def game_over_screen(screen, title, btn_text, sub_text):
    running = True
    title_font = pygame.font.SysFont('comicsans', 70)
    sub_text_font = pygame.font.SysFont('comicsans', 40)
    play_again_btn = Button(width // 2 - 125, height //
                            2, 250, 50, btn_text)
    quit_btn = Button(width // 2 - 100, height // 2 + 100, 200, 50, 'Quit')

    while running:
        screen.fill(COLORS['black'])
        title_text = title_font.render(title, 1, COLORS['white'])
        text = sub_text_font.render(sub_text, 1, COLORS['white'])
        screen.blit(title_text, (width // 2 -
                    title_text.get_width() // 2, 100))
        screen.blit(text, (width // 2 -
                    text.get_width() // 2, 200))

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_btn.is_over(pos):
                    running = False
                if quit_btn.is_over(pos):
                    pygame.quit()
                    sys.exit()

        play_again_btn.draw(screen)
        quit_btn.draw(screen)
        pygame.display.update()


def game(ai_speed, ai_amount):

    # Main loop
    running = True
    background_color = COLORS['black']
    # feedback_counter = 0
    # inBounds = True
    food_gen_timer = 0
    initial_food_delay = 200
    food_list = []
    ai_list = []
    player_victory = False

    # Create Player and AI
    player = Player(width // 2, height // 2, 20, 10, COLORS['blue'])
    for i in range(ai_amount):
        ai_list.append(AI(width // 2, height // 2,
                       20, ai_speed, COLORS['red']))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.handle_keys(width, height)

        for ai in ai_list:
            coordinate_ai_movement(ai, food_list, player)

        if initial_food_delay <= 0:
            if food_gen_timer == 0:
                food_gen_timer = random.randint(100, 300)
                new_food_x = random.randint(0, width - 5)
                new_food_y = random.randint(0, height - 5)
                food_list.append(Food(new_food_x, new_food_y))
            else:
                food_gen_timer -= 1
        else:
            initial_food_delay -= 1

        # Check collisions between player and AIs
        for ai in ai_list:
            if player.rect.colliderect(ai.rect):
                if player.size > ai.size:
                    ai.destroyed = True
                elif ai.size > player.size:
                    player.destroyed = True

        # Check collisions between player/AIs and food
        for food in food_list:
            if player.rect.colliderect(food.rect):
                print("Player has collided with food!")
                player.grow()
                food.consumed = True

            for ai in ai_list:
                if ai.rect.colliderect(food.rect):
                    print("AI has collided with food!")
                    ai.grow()
                    food.consumed = True

        # if player.collision_with_bounds() or ai.collision_with_bounds():
        #     if inBounds == True:
        #         background_color = white if background_color == black else black
        #         inBounds = False
        # else:
        #     inBounds = True

        food_list[:] = [
            food for food in food_list if food.duration > 0]
        food_list[:] = [
            food for food in food_list if food.consumed == False]
        food_list[:] = [
            food for food in food_list if food.collision_with_bounds() == False]

        character_list = [player] + ai_list
        render(character_list, food_list, background_color)

        if player.destroyed == True:
            running = False
        if all(ai.destroyed for ai in ai_list):  # Check if all AIs are destroyed
            running = False
            player_victory = True

        clock.tick(60)

        # Analytics
        # if (feedback_counter % 1000) == 0:
        #     print(GREEN + "Player Position: " + str(player.pos) + RESET)
        #     print(RED + "AI Position: " + str(ai.pos) + RESET)
        #     print("Distance between player and ai: " +
        #           str(calculate_distance(player.pos, ai.pos)))
        # feedback_counter += 1
    return player_victory


def main():
    running = True
    game_state = 'title'
    round_counter = 1
    ai_count = 1

    while running:
        if game_state == 'title':
            title_screen(screen, "Eat the Food!",
                         "Use the arrow keys to move. Eat food to grow bigger and eat the other square")
            game_state = 'game'
        elif game_state == 'game':
            ai_speed = ((round_counter % 10) * 0.5) + 1
            if round_counter % 10 == 0:
                    ai_count += 1 
            player_won = game(ai_speed, ai_count)
            game_state = 'gameOver'
        elif game_state == 'gameOver':
            if player_won:
                game_over_screen(screen, "You Won", "Next Round",
                                 f"Beat Round: {round_counter}   Starting Round: {round_counter + 1}")
                round_counter += 1
            else:
                game_over_screen(screen, "You Lost", "Start Over",
                                 f"Highest Round Beaten: {round_counter}")
                round_counter = 1
            game_state = 'game'


if __name__ == "__main__":
    main()
