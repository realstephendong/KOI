#!/usr/bin/env python3
"""
Test script to verify Pong game works independently
"""

import pygame
import sys
from config import *
from pong_game import PongGame

def test_pong():
    print("🎮 Testing Pong game...")
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Test")
    
    try:
        pong = PongGame(screen)
        print("✅ Pong game created successfully!")
        
        # Test a few frames
        clock = pygame.time.Clock()
        for i in range(10):
            dt = clock.tick(FPS) / 1000.0
            pong.handle_events()
            pong.update(dt)
            pong.draw()
            pygame.display.flip()
            
        print("✅ Pong game runs successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Pong game: {e}")
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_pong()
    if success:
        print("🎉 Pong test passed!")
    else:
        print("💥 Pong test failed!") 