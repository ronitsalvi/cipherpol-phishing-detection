#!/usr/bin/env python3
"""
Simple Streamlit Launcher - Direct approach without threading
"""

import os
import sys
import subprocess

def main():
    """Launch Streamlit with proper configuration"""
    
    print("🛡️ CipherPol Phishing Detection System")
    print("=" * 50)
    print("🚀 Starting web server (no setup wizard)...")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Set environment variables
    env = os.environ.copy()
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    env['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Create streamlit config
    config_dir = os.path.expanduser("~/.streamlit")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "config.toml")
    config_content = """[global]
developmentMode = false

[browser]
gatherUsageStats = false

[server]
headless = true
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Config created: {config_path}")
    print(f"🌐 Target URL: http://localhost:8507")
    print()
    print("🧪 Test the Instagram URL that was crashing:")
    print("   https://www.instagram.com/reel/DLfVr2_i7sM/?igsh=ZHRvc3owMnlvamlz")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Launch Streamlit directly
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "simple_app.py",
            "--server.port", "8507",
            "--server.address", "localhost",
            "--server.headless", "true"
        ], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Launch failed: {e}")

if __name__ == "__main__":
    main()