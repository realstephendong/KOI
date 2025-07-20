import pygame
import os

class Pet:
    def __init__(self):
        """Pet class - handles textbox appearance when mascot is pet"""
        self.speaking = False
        self.speech_text = ""
        self.speech_timer = 0
        self.speech_duration = 4.0  # Show speech for 4 seconds
        
        # Load custom font
        self.custom_font = None
        self.load_custom_font()
        
    def load_custom_font(self):
        """Load the custom TTF font from assets/fonts"""
        try:
            font_path = os.path.join("assets", "fonts", "Delicatus-e9OLl.ttf")
            if os.path.exists(font_path):
                self.custom_font = pygame.font.Font(font_path, 20)
                print(f"✅ Loaded custom font: {font_path}")
            else:
                print(f"⚠️  Custom font not found: {font_path}")
                self.custom_font = pygame.font.Font(None, 20)  # Fallback to default
        except Exception as e:
            print(f"❌ Error loading custom font: {e}")
            self.custom_font = pygame.font.Font(None, 20)  # Fallback to default
        
    def start_speaking(self, text):
        """Start showing a speech bubble with the given text"""
        self.speaking = True
        self.speech_text = text
        self.speech_timer = self.speech_duration

    def update(self, dt):
        """Update speech timer"""
        self.speech_timer -= dt
        if self.speech_timer <= 0:
            self.speaking = False
            
    def draw_speech_bubble(self, offscreen, mascot_x, mascot_y):
        """Draw speech bubble when mascot is speaking"""
        if not self.speaking or not self.speech_text:
            return
            
        # Use custom font if available, otherwise fallback to default
        font = self.custom_font if self.custom_font else pygame.font.Font(None, 20)
        
        # Calculate bubble size based on text
        words = self.speech_text.split()
        lines = []
        current_line = ""
        max_width = 0
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] < 200:  # Smaller for vertical layout
                current_line = test_line
            else:
                lines.append(current_line)
                max_width = max(max_width, font.size(current_line)[0])
                current_line = word
        lines.append(current_line)
        max_width = max(max_width, font.size(current_line)[0])
        
        # Draw speech bubble
        bubble_width = max_width + 30
        bubble_height = len(lines) * 25 + 15
        bubble_x = mascot_x - bubble_width // 2  # Center relative to mascot
        bubble_y = mascot_y - bubble_height - 150  # Position above mascot
        
        # Keep bubble on screen
        if bubble_x < 10:
            bubble_x = 10
        elif bubble_x + bubble_width > 600 - 10:  # DEVICE_WIDTH
            bubble_x = 600 - bubble_width - 10
            
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # Bubble background
        pygame.draw.rect(offscreen, (255, 255, 255), bubble_rect)
        pygame.draw.rect(offscreen, (0, 0, 0), bubble_rect, 2)
        
        # Draw speech bubble tail
        tail_x = mascot_x
        tail_y = bubble_y + bubble_height
        tail_points = [
            (tail_x, tail_y),
            (tail_x - 10, tail_y + 15),
            (tail_x + 10, tail_y + 15)
        ]
        pygame.draw.polygon(offscreen, (255, 255, 255), tail_points)
        pygame.draw.polygon(offscreen, (0, 0, 0), tail_points, 2)
        
        # Draw text using custom font
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))
            text_x = bubble_x + 15
            text_y = bubble_y + 12 + i * 20
            offscreen.blit(text, (text_x, text_y))
            
        