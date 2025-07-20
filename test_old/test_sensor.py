#!/usr/bin/env python3
"""
Simple sensor test script for the Tamagotchi water bottle
"""

from sensor_manager import SensorManager
import time

def test_sensor():
    print("🧪 Testing GY521 Sensor Integration")
    print("=" * 40)
    
    # Initialize sensor
    sensor = SensorManager()
    print(f"✅ Sensor initialized (Simulation mode: {sensor.simulation_mode})")
    
    # Test for 15 seconds
    print("🎯 Testing for 15 seconds...")
    print("   - Watch for drinking detection")
    print("   - Watch for shake detection")
    print("   - Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    drinking_count = 0
    shake_count = 0
    
    try:
        while time.time() - start_time < 15:
            data = sensor.update()
            
            if data['drinking_detected']:
                drinking_count += 1
                print(f"🍶 Drinking detected! Water: {data['water_amount']}ml")
                
            if data['shaking_detected']:
                shake_count += 1
                print("🔄 Shake detected!")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
    
    # Print results
    print("\n📊 Test Results:")
    print(f"   Drinking events: {drinking_count}")
    print(f"   Shake events: {shake_count}")
    print(f"   Total water consumed: {sensor.get_total_water_consumed():.1f}ml")
    print(f"   Session water: {sensor.get_session_water_consumed():.1f}ml")
    
    print("\n✅ Sensor test complete!")

if __name__ == "__main__":
    test_sensor() 