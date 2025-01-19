import asyncio
import pygame
import random
import time

class FencingGame:
    def __init__(self):
        # Keep all the original __init__ code from fencing_game-web.py
        self.player1_score = 0
        self.player2_score = 0
        self.max_position = 14
        self.points_to_win = 10  # Default points to win
        self.lunge_probabilities = {
            1: 65,  # If sword reaches opponent, hit is guaranteed
            2: 60,
            3: 70, 
            4: 15,
            5: 7.5,    # Beyond sword reach, cannot hit
            6: 5,
            7: 2.5,
        }

        # Pygame initialization
        pygame.init()
        self.screen_width = 800
        self.screen_height = 400
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Fencing Game")
        self.clock = pygame.time.Clock()
        self.running = True

        # Replace self.distance with individual positions
        self.player1_pos = 3  # Starting at position 3
        self.player2_pos = 11  # Starting at position 11

        # Add lunge animation and cooldown variables
        self.player1_lunging = False
        self.player2_lunging = False
        self.lunge_animation_frames = 10
        self.player1_lunge_frame = 0
        self.player2_lunge_frame = 0
        
        # Cooldown variables (in frames)
        self.lunge_cooldown = 30  # 1 second at 30 FPS
        self.player1_cooldown = 0
        self.player2_cooldown = 0

        # Fleche variables
        self.player1_fleche = False
        self.player2_fleche = False
        self.fleche_animation_frames = 15
        self.player1_fleche_frame = 0
        self.player2_fleche_frame = 0
        self.fleche_cooldown = 150  # 5 seconds at 30 FPS
        self.player1_fleche_cooldown = 0
        self.player2_fleche_cooldown = 0
        self.fleche_distance = 3  # How many positions to move forward

        # Defense variables
        self.defense_duration = 8  # 0.25 seconds at 30 FPS
        self.defense_cooldown = 30  # 1 second at 30 FPS
        self.player1_defending = False
        self.player2_defending = False
        self.player1_defense_frame = 0
        self.player2_defense_frame = 0
        self.player1_defense_cooldown = 0
        self.player2_defense_cooldown = 0
        
        # Starting positions
        self.player1_start_pos = 3
        self.player2_start_pos = 11
        self.player1_pos = self.player1_start_pos
        self.player2_pos = self.player2_start_pos

        # Font for countdown
        self.countdown_font = pygame.font.Font(None, 74)

        # Add timer and round variables
        self.round_duration = 180  # 3 minutes in seconds
        self.current_time = self.round_duration
        self.current_round = 1
        self.total_rounds = 1  # Will be set based on points selection
        self.last_time = time.time()

    # Keep all the original helper methods (move, lunge, defense, fleche, etc.) unchanged
    # Only convert the main game loop methods to async

    async def countdown(self):
        """Display countdown before resuming play."""
        messages = ["Ready!", "Set!", "GO!"]
        
        for msg in messages:
            self.screen.fill((255, 255, 255))
            
            # Draw current score and round
            score_font = pygame.font.Font(None, 48)
            score_text = score_font.render(f"{self.player1_score} - {self.player2_score}", True, (0, 0, 0))
            score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//4))
            round_text = score_font.render(f"Round {self.current_round}", True, (0, 0, 0))
            round_rect = round_text.get_rect(center=(self.screen_width//2, self.screen_height//4 - 50))
            
            self.screen.blit(round_text, round_rect)
            self.screen.blit(score_text, score_rect)
            
            text = self.countdown_font.render(msg, True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(0)

    async def show_start_menu(self):
        """Display the start menu and handle point selection."""
        menu_font = pygame.font.Font(None, 64)
        button_font = pygame.font.Font(None, 48)
        title_font = pygame.font.Font(None, 74)
        
        # Create button rectangles
        start_button = pygame.Rect(self.screen_width//2 - 100, self.screen_height//2 - 50, 200, 50)
        point_5_button = pygame.Rect(self.screen_width//2 - 220, self.screen_height//2 + 50, 140, 50)
        point_10_button = pygame.Rect(self.screen_width//2 - 70, self.screen_height//2 + 50, 140, 50)
        point_15_button = pygame.Rect(self.screen_width//2 + 80, self.screen_height//2 + 50, 140, 50)
        
        show_point_selection = False
        menu_running = True
        
        while menu_running and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    menu_running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    
                    if not show_point_selection:
                        if start_button.collidepoint(mouse_pos):
                            show_point_selection = True
                    else:
                        if point_5_button.collidepoint(mouse_pos):
                            self.points_to_win = 5
                            self.total_rounds = 1
                            return
                        elif point_10_button.collidepoint(mouse_pos):
                            self.points_to_win = 10
                            self.total_rounds = 2
                            return
                        elif point_15_button.collidepoint(mouse_pos):
                            self.points_to_win = 15
                            self.total_rounds = 3
                            return
            
            self.screen.fill((255, 255, 255))
            
            # Draw title
            title_text = title_font.render("Fencing Game", True, (0, 0, 0))
            title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//4))
            self.screen.blit(title_text, title_rect)
            
            if not show_point_selection:
                pygame.draw.rect(self.screen, (100, 100, 100), start_button)
                start_text = button_font.render("Start", True, (255, 255, 255))
                start_text_rect = start_text.get_rect(center=start_button.center)
                self.screen.blit(start_text, start_text_rect)
            else:
                select_text = menu_font.render("Select Match Points:", True, (0, 0, 0))
                select_rect = select_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
                self.screen.blit(select_text, select_rect)
                
                for button, text in [(point_5_button, "5 Points"),
                                   (point_10_button, "10 Points"),
                                   (point_15_button, "15 Points")]:
                    pygame.draw.rect(self.screen, (100, 100, 100), button)
                    text_surface = button_font.render(text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=button.center)
                    self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(0)

    async def show_victory_screen(self, winner):
        """Display the victory screen for the winning player."""
        victory_font = pygame.font.Font(None, 84)
        score_font = pygame.font.Font(None, 54)
        
        # Create OK button
        ok_button = pygame.Rect(self.screen_width//2 - 60, self.screen_height//2 + 120, 120, 50)
        victory_screen = True
        
        while victory_screen and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    victory_screen = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if ok_button.collidepoint(event.pos):
                        victory_screen = False
            
            self.screen.fill((255, 255, 255))
            
            # Draw victory message
            victory_text = victory_font.render(f"Player {winner} Wins!", True, (0, 0, 0))
            victory_rect = victory_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
            self.screen.blit(victory_text, victory_rect)
            
            # Draw final score
            score_text = score_font.render(f"Final Score: {self.player1_score} - {self.player2_score}", True, (0, 0, 0))
            score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50))
            self.screen.blit(score_text, score_rect)
            
            # Draw OK button
            pygame.draw.rect(self.screen, (100, 100, 100), ok_button)
            ok_text = victory_font.render("OK", True, (255, 255, 255))
            ok_text_rect = ok_text.get_rect(center=ok_button.center)
            self.screen.blit(ok_text, ok_text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(0)

    async def start_new_round(self):
        """Start a new round, resetting positions and timer."""
        self.current_time = self.round_duration
        self.reset_positions()
        await self.countdown()
        self.last_time = time.time()

    async def play(self):
        # Show start menu before starting the game
        await self.show_start_menu()
        if not self.running:
            return
            
        # Start first round
        await self.start_new_round()

        winner = None
        while self.running:
            # Add frame limiting
            await asyncio.sleep(0)
            self.clock.tick(30)  # Limit to 30 FPS
            
            # Update timer
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            self.current_time -= dt

            # Check if round is over
            if self.current_time <= 0:
                if self.current_round < self.total_rounds:
                    self.current_round += 1
                    await self.start_new_round()
                else:
                    if self.player1_score > self.player2_score:
                        winner = 1
                    elif self.player2_score > self.player1_score:
                        winner = 2
                    else:
                        self.current_time = 60
                        await self.countdown()
                        self.last_time = time.time()
                        continue
                    break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Player 1 controls
                    if event.key == pygame.K_w:  # Attack
                        self.lunge(1)
                    elif event.key == pygame.K_e:  # Fleche
                        self.fleche(1)
                    elif event.key == pygame.K_s:  # Defense
                        self.defense(1)
                    elif event.key == pygame.K_d:  # Forward
                        self.move(1, 1, True)
                    elif event.key == pygame.K_a:  # Backward
                        self.move(1, 1, False)

                    # Player 2 controls
                    elif event.key == pygame.K_UP:  # Attack
                        self.lunge(2)
                    elif event.key == pygame.K_SLASH:  # Fleche
                        self.fleche(2)
                    elif event.key == pygame.K_DOWN:  # Defense
                        self.defense(2)
                    elif event.key == pygame.K_LEFT:  # Forward
                        self.move(2, 1, True)
                    elif event.key == pygame.K_RIGHT:  # Backward
                        self.move(2, 1, False)

            # Update animations and cooldowns
            self.update_animations()
            
            # Draw players on screen
            self.draw_players()

            # Check win conditions
            if self.player1_score >= self.points_to_win:
                winner = 1
                break
            elif self.player2_score >= self.points_to_win:
                winner = 2
                break

        # Show victory screen if there's a winner
        if winner and self.running:
            await self.show_victory_screen(winner)

async def main():
    game = FencingGame()
    await game.play()
    pygame.quit()

# Pygbag entry point
asyncio.run(main()) 