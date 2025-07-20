#!/usr/bin/env python3
"""
Test script for Tamagotchi Water Bottle
Run this to verify all components are working correctly
"""

import sys
import time
import pygame

def test_pygame():
    """Test pygame initialization"""
    print("Testing Pygame...")
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Test")
        
        # Test basic drawing
        screen.fill((255, 255, 255))
        pygame.draw.circle(screen, (255, 0, 0), (400, 300), 50)
        pygame.display.flip()
        
        time.sleep(1)
        pygame.quit()
        print("✅ Pygame test passed!")
        return True
    except Exception as e:
        print(f"❌ Pygame test failed: {e}")
        return False

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    try:
        import config
        print("✅ Config imported")
        
        import mascot
        print("✅ Mascot imported")
        
        import ai_manager
        print("✅ AI Manager imported")
        
        import sensor_manager
        print("✅ Sensor Manager imported")
        
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_mascot():
    """Test mascot functionality"""
    print("Testing mascot...")
    try:
        from mascot import Mascot
        
        mascot = Mascot('koi')
        print(f"✅ Created mascot: {mascot.name}")
        
        # Test update
        mascot.update(0.1, water_drunk=10)
        print(f"✅ Mascot health: {mascot.health}")
        
        # Test state changes
        mascot.drink_water(20)
        print(f"✅ After drinking: {mascot.health}")
        
        return True
    except Exception as e:
        print(f"❌ Mascot test failed: {e}")
        return False

def test_ai_manager():
    """Test AI manager functionality"""
    print("Testing AI manager...")
    try:
        from ai_manager import AIManager
        
        ai = AIManager()
        print(f"✅ AI Manager created (API available: {ai.is_available()})")
        
        # Test fallback features
        feature = ai.get_fallback_feature()
        print(f"✅ Fallback feature: {feature[:50]}...")
        
        conversation = ai.get_fallback_conversation()
        print(f"✅ Fallback conversation: {conversation}")
        
        return True
    except Exception as e:
        print(f"❌ AI Manager test failed: {e}")
        return False

def test_sensor_manager():
    """Test sensor manager functionality"""
    print("Testing sensor manager...")
    try:
        from sensor_manager import SensorManager
        
        sensor = SensorManager()
        print("✅ Sensor Manager created")
        
        # Test simulation mode
        sensor.generate_simulated_data()
        print("✅ Sensor simulation working")
        
        # Test update
        data = sensor.update()
        print(f"✅ Sensor data: {data}")
        
        return True
    except Exception as e:
        print(f"❌ Sensor Manager test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("Testing configuration...")
    try:
        import config
        
        print(f"✅ Screen size: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}")
        print(f"✅ FPS: {config.FPS}")
        print(f"✅ Mascots: {list(config.MASCOTS.keys())}")
        print(f"✅ Health states: {list(config.HEALTH_STATES.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Tamagotchi Water Bottle - Component Tests")
    print("=" * 50)
    
    tests = [
        ("Pygame", test_pygame),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Mascot", test_mascot),
        ("AI Manager", test_ai_manager),
        ("Sensor Manager", test_sensor_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"⚠️  {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to run.")
        print("💡 Run 'python main.py' to start the game!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 