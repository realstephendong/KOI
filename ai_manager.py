import random
import time
from config import *

class AIManager:
    def __init__(self):
        self.current_pet = "koi"

        # Response categories with lots of variety
        self.pet_responses = {
            "koi": ["Yay~! That tickles! ^w^", "Pet me more pls! :3"],
            "soy": ["bro just sigma stroked me", "rizz hands activated"],
            "joy": ["what the hell are you doing", "touch me again and i bite"]
        }

        self.drinking_responses = {
            "koi": ["Yummy water~!", "You're doing great! ^w^"],
            "soy": ["hydration grindset", "drinkin' like a giga"],
            "joy": ["finally. took you long enough.", "bout damn time, dehydrated crust"]
        }

        self.large_drink_responses = {
            "koi": ["Big sips! Wow~!", "You're so strong! :D"],
            "soy": ["gulped that like a sigma", "hydration W fr fr"],
            "joy": ["jesus, chill. it's not a contest.", "congrats. you drank water. do you want a medal?"]
        }
        
        self.small_drink_responses = {
            "koi": ["A little sip is still good! ^_^", "Every drop counts! :3"],
            "soy": ["weak sip tbh", "sip so small it's in beta"],
            "joy": ["pathetic.", "that wasn't a drink. that was an insult."]
        }
        
        self.game_start_responses = {
            "koi": ["Let's do our best! Yay~!", "Game time! I'm excited! ^w^"],
            "soy": ["ayo let's cook", "game on skibidi style"],
            "joy": ["ugh. here we go again.", "better not suck this time."]
        }
        
        self.good_game_responses = {
            "koi": ["That was so much fun! ^_^", "You did amazing~!"],
            "soy": ["W gameplay", "that was actually sigma af"],
            "joy": ["well, you didn't mess it up. shocking.", "not bad. for once."]
        }
        
        self.okay_game_responses = {
            "koi": ["You tried your best! ^w^", "That was fun! Let's do even better next time!"],
            "soy": ["mid game tbh", "skibidi effort detected"],
            "joy": ["i've seen snails with more hustle.", "you call that a game?"]
        }
        
        self.achievements = {
            "koi": ["You did it~! I'm so proud of you! ^w^", "Yay yay yay! Great job!"],
            "soy": ["W unlocked", "u just leveled up in life"],
            "joy": ["cool. now do it again.", "i'll be impressed when you do that twice."]
        }
        
        # Track last responses to avoid repetition
        self.last_pet_response = None
        self.last_drink_response = None
        self.last_game_response = None
        self.last_achievement = None
        
    def is_available(self):
        """Always available since we're using local responses"""
        return True
        
    def get_random_response(self, response_list, last_response_var):
        """Get a random response that's different from the last one"""
        if len(response_list) <= 1:
            return response_list[0]
            
        # Get a response different from the last one
        available_responses = [r for r in response_list if r != last_response_var]
        if not available_responses:
            available_responses = response_list
            
        response = random.choice(available_responses)
        return response
        
    def generate_conversation(self, mascot_name, personality, context):
        """Generate conversation response based on context"""
        if "petted" in context.lower():
            response = self.get_random_response(self.pet_responses[self.current_pet], self.last_pet_response)
            self.last_pet_response = response
            return response
        elif "drank" in context.lower():
            # Extract water amount from context
            try:
                import re
                amount_match = re.search(r'(\d+)ml', context)
                if amount_match:
                    amount = int(amount_match.group(1))
                    if amount > 100:
                        response = self.get_random_response(self.large_drink_responses[self.current_pet], self.last_drink_response)
                    else:
                        response = self.get_random_response(self.small_drink_responses[self.current_pet], self.last_drink_response)
                else:
                    response = self.get_random_response(self.drinking_responses[self.current_pet], self.last_drink_response)
            except:
                response = self.get_random_response(self.drinking_responses[self.current_pet], self.last_drink_response)
            
            self.last_drink_response = response
            return response
        elif "played" in context.lower() and "scored" in context.lower():
            # Extract score from context
            try:
                import re
                score_match = re.search(r'(\d+) points', context)
                if score_match:
                    score = int(score_match.group(1))
                    if score > 50:
                        response = self.get_random_response(self.good_game_responses[self.current_pet], self.last_game_response)
                    else:
                        response = self.get_random_response(self.okay_game_responses[self.current_pet], self.last_game_response)
                else:
                    response = self.get_random_response(self.okay_game_responses[self.current_pet], self.last_game_response)
            except:
                response = self.get_random_response(self.okay_game_responses[self.current_pet], self.last_game_response)
            
            self.last_game_response = response
            return response
        else:
            # Default response
            return random.choice(self.pet_responses[self.current_pet])
            
    def generate_achievement(self, water_amount, streak_days):
        """Generate achievement based on water amount and streak"""
        response = self.get_random_response(self.achievements[self.current_pet], self.last_achievement)
        self.last_achievement = response
        return response
        
    def generate_random_feature(self, mascot_name, personality, health):
        """Generate random feature suggestion"""
        features = [
            "Let's have a dance party!",
            "Time for some stretching exercises!",
            "How about we play hide and seek?",
            "Let's do some jumping jacks!",
            "Time for a mini workout!",
            "Let's play catch with invisible balls!",
            "How about we do some yoga poses?",
            "Let's have a singing contest!",
            "Time for some shadow boxing!",
            "Let's play follow the leader!",
            "How about we do some breathing exercises?",
            "Let's have a mini meditation session!",
            "Time for some fun stretches!",
            "Let's do some silly dances!",
            "How about we play charades?",
            "Let's have a mini workout session!",
            "Time for some fun exercises!",
            "Let's do some jumping around!",
            "How about we play mirror movements?",
            "Let's have a fun fitness session!"
        ]
        return random.choice(features) 