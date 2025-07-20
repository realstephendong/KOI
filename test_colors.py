#!/usr/bin/env python3
"""
Test script to verify black and white color scheme
"""

from config import *

def test_colors():
    print("🎨 Testing Black and White Color Scheme")
    print("=" * 40)
    
    print("✅ Base Colors:")
    print(f"   WHITE: {WHITE}")
    print(f"   BLACK: {BLACK}")
    print(f"   GRAY: {GRAY}")
    print(f"   LIGHT_GRAY: {LIGHT_GRAY}")
    print(f"   DARK_GRAY: {DARK_GRAY}")
    
    print("\n✅ Mascot Colors:")
    for name, config in MASCOTS.items():
        print(f"   {name}: {config['color']}")
    
    print("\n✅ Health State Colors:")
    for state, data in HEALTH_STATES.items():
        print(f"   {state}: {data['color']}")
    
    print("\n✅ Legacy Color Mappings:")
    print(f"   BLUE: {BLUE}")
    print(f"   GREEN: {GREEN}")
    print(f"   RED: {RED}")
    print(f"   YELLOW: {YELLOW}")
    print(f"   PINK: {PINK}")
    print(f"   PURPLE: {PURPLE}")
    
    print("\n🎉 Color scheme test complete!")

if __name__ == "__main__":
    test_colors() 