#!/usr/bin/env python3
"""
Setup script for Tamagotchi Water Bottle
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    # Check if pip is available
    if not shutil.which('pip'):
        print("❌ pip not found. Please install pip first.")
        return False
    
    # Install from requirements.txt
    if os.path.exists('requirements.txt'):
        return run_command('pip install -r requirements.txt', 'Installing packages from requirements.txt')
    else:
        print("❌ requirements.txt not found")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("🔧 Setting up environment file...")
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    # Copy from example if it exists
    if os.path.exists('env_example.txt'):
        shutil.copy('env_example.txt', '.env')
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your Gemini API key")
        return True
    else:
        # Create basic .env file
        with open('.env', 'w') as f:
            f.write("# Tamagotchi Water Bottle Environment Variables\n")
            f.write("# Add your Gemini API key here:\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        
        print("✅ Created basic .env file")
        print("⚠️  Please edit .env file and add your Gemini API key")
        return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['assets', 'logs', 'saves']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/ directory")
        else:
            print(f"✅ {directory}/ directory already exists")
    
    return True

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    return run_command('python test_setup.py', 'Running component tests')

def main():
    """Main setup function"""
    print("🚀 Tamagotchi Water Bottle - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Run tests
    if not run_tests():
        print("⚠️  Tests failed, but setup completed. You may need to fix issues manually.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your Gemini API key")
    print("2. Connect your GY521 sensor to the Raspberry Pi")
    print("3. Run 'python main.py' to start the game")
    print("\n💡 For help, check the README.md file")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 