import random
import time
from config import *

class AIManager:
    def __init__(self):
        # Response categories with lots of variety
        self.pet_responses = [
            "Aww, thank you! That feels so nice!",
            "You're the best! I love your gentle touch!",
            "Mmm, that's so relaxing! Thank you!",
            "You make me so happy! I love being petted!",
            "That's wonderful! I feel so loved!",
            "Your touch is so comforting!",
            "I'm the luckiest mascot ever!",
            "That petting was perfect!",
            "You have such a gentle hand!",
            "I could stay like this forever!",
            "This is pure bliss!",
            "You're my favorite person!",
            "That felt amazing!",
            "I'm so grateful for you!",
            "Your love makes me glow!",
            "This is the best feeling ever!",
            "You're absolutely wonderful!",
            "I feel so special right now!",
            "Your touch is magical!",
            "I'm floating on cloud nine!"
        ]
        
        self.drinking_responses = [
            "Great job staying hydrated!",
            "Water is the best choice!",
            "You're taking such good care of yourself!",
            "Hydration is the key to health!",
            "Every sip counts towards wellness!",
            "You're building healthy habits!",
            "Water makes everything better!",
            "Your body will thank you!",
            "Staying hydrated is so important!",
            "You're making smart choices!",
            "Water is nature's perfect drink!",
            "You're on the right track!",
            "Hydration equals happiness!",
            "Your health is your wealth!",
            "Water is life!",
            "You're doing amazing!",
            "Every drop makes a difference!",
            "You're building a healthy future!",
            "Water is the foundation of health!",
            "You're making me proud!"
        ]
        
        self.large_drink_responses = [
            "Wow! That's a big drink! You're really staying hydrated!",
            "Amazing! You're taking hydration seriously!",
            "Incredible! That's a lot of water!",
            "Fantastic! You're really taking care of yourself!",
            "Outstanding! That's some serious hydration!",
            "Excellent! You're a hydration champion!",
            "Brilliant! That's a healthy amount of water!",
            "Superb! You're really prioritizing your health!",
            "Magnificent! That's proper hydration!",
            "Spectacular! You're really committed to wellness!"
        ]
        
        self.small_drink_responses = [
            "Every little bit helps!",
            "Small sips add up!",
            "Every drop counts!",
            "Little by little, you're getting there!",
            "Small steps lead to big changes!",
            "Every sip is progress!",
            "You're building the habit!",
            "Small amounts still matter!",
            "You're on the right path!",
            "Every little bit is good!"
        ]
        
        self.game_start_responses = [
            "Let's break some bricks! Tilt the bottle to move!",
            "Ready to play! Use the bottle tilt to control the paddle!",
            "Game time! Tilt your bottle to move the paddle!",
            "Let's have some fun! Tilt to control!",
            "Time to play! Use bottle tilt for paddle movement!",
            "Game on! Tilt your bottle to move!",
            "Let's get gaming! Tilt to control the paddle!",
            "Ready to break bricks! Tilt your bottle!",
            "Game time! Use bottle tilt to move!",
            "Let's play! Tilt to control the paddle!"
        ]
        
        self.good_game_responses = [
            "Amazing! You're a brick-breaking master!",
            "Incredible! You're really good at this!",
            "Fantastic! You have serious gaming skills!",
            "Outstanding! You're a natural!",
            "Brilliant! You're really talented!",
            "Excellent! You're a gaming champion!",
            "Superb! You have amazing reflexes!",
            "Magnificent! You're a true gamer!",
            "Spectacular! You're really skilled!",
            "Wonderful! You're a gaming pro!"
        ]
        
        self.okay_game_responses = [
            "Great job! You're getting better!",
            "Good work! You're improving!",
            "Nice try! You're learning!",
            "Well done! You're making progress!",
            "Good effort! You're getting there!",
            "Nice work! You're developing skills!",
            "Great attempt! You're improving!",
            "Good job! You're learning!",
            "Well played! You're getting better!",
            "Nice effort! You're making progress!"
        ]
        
        self.achievements = [
            "Hydration Hero!",
            "Water Warrior!",
            "Drinking Champion!",
            "Hydration Master!",
            "Water Wizard!",
            "Liquid Legend!",
            "Hydration King!",
            "Water Wonder!",
            "Drinking Dynamo!",
            "Hydration Star!",
            "Water Champion!",
            "Liquid Master!",
            "Hydration Pro!",
            "Water Expert!",
            "Drinking Hero!",
            "Hydration Legend!",
            "Water Master!",
            "Liquid Champion!",
            "Hydration Expert!",
            "Water Pro!"
        ]
        
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
            response = self.get_random_response(self.pet_responses, self.last_pet_response)
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
                        response = self.get_random_response(self.large_drink_responses, self.last_drink_response)
                    else:
                        response = self.get_random_response(self.small_drink_responses, self.last_drink_response)
                else:
                    response = self.get_random_response(self.drinking_responses, self.last_drink_response)
            except:
                response = self.get_random_response(self.drinking_responses, self.last_drink_response)
            
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
                        response = self.get_random_response(self.good_game_responses, self.last_game_response)
                    else:
                        response = self.get_random_response(self.okay_game_responses, self.last_game_response)
                else:
                    response = self.get_random_response(self.okay_game_responses, self.last_game_response)
            except:
                response = self.get_random_response(self.okay_game_responses, self.last_game_response)
            
            self.last_game_response = response
            return response
        else:
            # Default response
            return random.choice(self.pet_responses)
            
    def generate_achievement(self, water_amount, streak_days):
        """Generate achievement based on water amount and streak"""
        response = self.get_random_response(self.achievements, self.last_achievement)
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