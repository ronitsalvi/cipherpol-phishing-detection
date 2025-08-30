#!/usr/bin/env python3
"""
Streamlit Launcher - Programmatic startup to bypass setup wizard
Ensures reliable startup of the phishing detection web app
"""

import streamlit.web.cli as stcli
import sys
import os
import time
import subprocess
import socket
import threading
import signal

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def wait_for_server(port, timeout=10):
    """Wait for Streamlit server to start"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    return True
        except:
            pass
        time.sleep(0.5)
    return False

def setup_streamlit_config():
    """Set up Streamlit configuration to bypass setup"""
    config_dir = os.path.expanduser("~/.streamlit")
    os.makedirs(config_dir, exist_ok=True)
    
    # Create minimal config to skip setup
    config_path = os.path.join(config_dir, "config.toml")
    config_content = """
[global]
developmentMode = false

[browser]
gatherUsageStats = false
showErrorDetails = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[theme]
base = "light"
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content.strip())
    
    print(f"✅ Created Streamlit config: {config_path}")

def launch_streamlit_programmatically():
    """Launch Streamlit programmatically"""
    
    port = 8507
    app_file = "simple_app.py"
    
    print("🛡️ CipherPol Phishing Detection System")
    print("=" * 50)
    print("🚀 Starting robust web server...")
    print(f"📍 Working directory: {os.getcwd()}")
    print(f"🌐 Target URL: http://localhost:{port}")
    print()
    
    # Check if app file exists
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found in current directory")
        return False
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️ Port {port} is already in use")
        print("🔄 Attempting to free the port...")
        try:
            # Try to kill any existing streamlit processes
            subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
            time.sleep(2)
        except:
            pass
    
    # Set environment variables to skip setup
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Setup config
    setup_streamlit_config()
    
    print("🔄 Launching Streamlit server...")
    
    try:
        # Use programmatic approach
        sys.argv = [
            "streamlit",
            "run",
            app_file,
            "--server.port", str(port),
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        # Start in background thread to check status
        server_thread = threading.Thread(target=lambda: stcli.main())
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        if wait_for_server(port, timeout=15):
            print(f"✅ Server started successfully!")
            print(f"🌐 Open: http://localhost:{port}")
            print()
            print("🧪 Test URLs:")
            print("   • https://www.google.com (should work)")
            print("   • https://www.instagram.com/reel/DLfVr2_i7sM/?igsh=ZHRvc3owMnlvamlz (fixed!)")
            print()
            print("💡 Press Ctrl+C to stop the server")
            print("-" * 50)
            
            # Keep main thread alive
            try:
                while server_thread.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down server...")
                return True
        else:
            print("❌ Server failed to start within timeout")
            return False
            
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        return False

def main():
    """Main launcher function"""
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = launch_streamlit_programmatically()
    
    if success:
        print("\n✅ Session completed successfully!")
    else:
        print("\n❌ Launch failed - trying alternative method...")
        print("\n🔧 Alternative command:")
        print(f"cd '{script_dir}'")
        print("python3 -c \"import streamlit.web.cli as stcli; import sys; sys.argv=['streamlit', 'run', 'simple_app.py', '--server.port', '8507']; stcli.main()\"")

if __name__ == "__main__":
    main()