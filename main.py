import time
from PIL import Image
from PIL import ImageDraw
from config import DEVICE_HEIGHT, DEVICE_WIDTH, FPS
from graphics.pet import Pet
from graphics.ui import draw_ui
import pygame
import sys


def pet_selection_loop():
    pet_choice = "koi"
        
    while True:
        return pet_choice
    
def create_pet(pet_choice):
    if (pet_choice == "koi"):
        koi_image_paths = {"idle0": "./graphics/assets/koi/koi_idle0.png",
                        "idle1": "./graphics/assets/koi/koi_idle1.png"}

        koi = Pet(3, 50, koi_image_paths)
        koi.setup_images()
        return koi
    elif (pet_choice == "soy"):
        soy_image_paths = {"idle0": "./graphics/assets/soy/soy_idle0.png", 
                        "idle1": "./graphics/assets/soy/soy_idle1.png"}

        soy = Pet(3, 50, soy_image_paths)
        soy.setup_images()
        return soy
    
def increase_friendship():
    pass

def pet_selection_loop(offscreen, screen, clock):
    pet_choices = ["koi", "soy"]
    pet_index = 0
    current_pet = create_pet(pet_choices[pet_index])
        
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        offscreen.fill((0, 0, 0))
        
        # # Handle button presses
        # if blue_button.is_pressed():
        #     global state, pet_choice
        #     state = "pet"
        #     pet_choice = pet_choices[pet_index]
        #     print(f"Confirmed pet choice: {pet_choice}")
        #     return current_pet
            
        # if yellow_button.is_pressed():
        #     pet_index = (pet_index + 1) % len(pet_choices)
        #     current_pet = create_pet(pet_choices[pet_index])
        #     print(f"Selected pet: {pet_choices[pet_index]}")
        
        # Draw components
        current_pet.draw(offscreen, "idle")

        rotated = pygame.transform.rotate(offscreen, 90)
        screen.blit(rotated, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

def run_loop(offscreen, screen, clock, pet):
    while True: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        offscreen.fill((0, 0, 0)) # Fill screen to black

        # Draw components
        pet.draw(offscreen, "idle")
        draw_ui(offscreen, 3)

        rotated = pygame.transform.rotate(offscreen, 90)
        screen.blit(rotated, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        

def main():
    pygame.init()
    screen = pygame.display.set_mode((DEVICE_HEIGHT, DEVICE_WIDTH))
    offscreen = pygame.Surface((DEVICE_WIDTH, DEVICE_HEIGHT))
    clock = pygame.time.Clock()

    pet_choice = "soy"
    game_state = "pet"
    
    if game_state == "selection":
        selected_pet = pet_selection_loop(offscreen, clock)

        run_loop(offscreen, screen, clock, selected_pet)
    
    elif game_state == "pet":
        pet = create_pet(pet_choice)

        run_loop(offscreen, screen, clock, pet)

if __name__ == "__main__":
    main()