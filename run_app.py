#!/usr/bin/env python3
"""
Launch script for the Phishing Detection System
Handles streamlit configuration and startup
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def find_streamlit():
    """Find the streamlit executable"""
    
    # Try common locations
    possible_paths = [
        "/Users/ronitsalvi/Library/Python/3.8/bin/streamlit",
        "/usr/local/bin/streamlit",
        "/opt/homebrew/bin/streamlit"
    ]
    
    # Check if streamlit is in PATH
    try:
        result = subprocess.run(["which", "streamlit"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    # Check the known paths
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try with python -m
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                      capture_output=True, check=True)
        return f"{sys.executable} -m streamlit"
    except:
        pass
    
    return None

def create_streamlit_config():
    """Create streamlit configuration"""
    
    config_dir = Path.home() / ".streamlit"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.toml"
    
    config_content = """
[server]
port = 8503
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[logger]
level = "info"
"""
    
    with open(config_file, "w") as f:
        f.write(config_content.strip())
    
    print(f"✅ Created Streamlit config at: {config_file}")

def launch_app():
    """Launch the Streamlit application"""
    
    print("🚀 Starting Phishing Detection System...")
    print("=" * 50)
    
    # Create config
    create_streamlit_config()
    
    # Find streamlit
    streamlit_path = find_streamlit()
    if not streamlit_path:
        print("❌ Streamlit not found. Please install with: pip3 install streamlit")
        return False
    
    print(f"📍 Using Streamlit at: {streamlit_path}")
    
    # Change to the app directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    print(f"📁 Working directory: {app_dir}")
    print("🔧 Starting Streamlit server...")
    
    # Build the command
    if "python" in streamlit_path:
        cmd = streamlit_path.split() + ["run", "app.py"]
    else:
        cmd = [streamlit_path, "run", "app.py"]
    
    cmd.extend([
        "--server.port", "8503",
        "--server.address", "localhost",
        "--server.headless", "false"
    ])
    
    try:
        print("⏳ Launching application...")
        print(f"🌐 App will be available at: http://localhost:8503")
        print("📖 Loading phishing detection system...")
        print("\n💡 Use Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the process
        process = subprocess.Popen(cmd)
        
        # Wait a moment then try to open browser
        time.sleep(3)
        try:
            webbrowser.open("http://localhost:8503")
        except:
            pass
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        try:
            process.terminate()
        except:
            pass
        print("✅ Server stopped")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def test_system_first():
    """Run a quick system test before launching"""
    
    print("🧪 Quick System Test")
    print("-" * 30)
    
    try:
        # Test imports
        from modules.phishing_detector import PhishingDetector
        print("✅ Core modules imported successfully")
        
        # Test basic functionality
        detector = PhishingDetector()
        print("✅ Phishing detector initialized")
        
        print("✅ System ready for launch!")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        print("💡 Try running: python3 simple_test.py")
        return False

def main():
    """Main function"""
    
    print("🛡️ Explainable Phishing Detection System")
    print("=" * 50)
    
    # Test system first
    if not test_system_first():
        print("\n❌ System tests failed. Please fix issues before launching.")
        return
    
    print("\n🚀 System tests passed! Launching web interface...")
    print("=" * 50)
    
    # Launch the app
    success = launch_app()
    
    if success:
        print("\n🎉 Application launched successfully!")
    else:
        print("\n💡 Alternative launch methods:")
        print("1. python3 -m streamlit run app.py --server.port 8503")
        print("2. streamlit run app.py --server.port 8503")
        print("3. python3 demo_results.py (for command-line demo)")

if __name__ == "__main__":
    main()