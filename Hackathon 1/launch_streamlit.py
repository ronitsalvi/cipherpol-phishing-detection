#!/usr/bin/env python3
"""
Reliable Streamlit Launcher for Phishing Detection System
Handles all configuration and startup issues
"""

import subprocess
import sys
import os
import time
import socket
from pathlib import Path

def check_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def kill_existing_streamlit():
    """Kill any existing Streamlit processes"""
    try:
        subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
        print("🧹 Cleaned up any existing Streamlit processes")
        time.sleep(1)
    except:
        pass

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from modules.phishing_detector import PhishingDetector
        import streamlit
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'

def launch_streamlit(port=8505):
    """Launch Streamlit with proper configuration"""
    
    print("🛡️ Starting Phishing Detection System")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("❌ Module imports failed. Please check dependencies.")
        return False
    
    # Clean up any existing processes
    kill_existing_streamlit()
    
    # Set up environment
    setup_environment()
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️ Port {port} is busy, trying {port + 1}")
        port += 1
        if not check_port_available(port):
            print(f"⚠️ Port {port} is busy, trying {port + 1}")
            port += 1
    
    print(f"🚀 Starting Streamlit on port {port}")
    print(f"🌐 URL: http://localhost:{port}")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Build command
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'simple_app.py',
        '--server.port', str(port),
        '--server.address', 'localhost',
        '--server.headless', 'false'
    ]
    
    print("🔧 Command:", ' '.join(cmd))
    print("💡 Press Ctrl+C to stop the server")
    print("⏳ Starting server...")
    print("-" * 50)
    
    try:
        # Start Streamlit
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor startup
        startup_timeout = 30
        start_time = time.time()
        
        print("📡 Server starting up...")
        
        # Wait for successful startup or timeout
        while True:
            # Check if process is still running
            if process.poll() is not None:
                output, _ = process.communicate()
                print("❌ Streamlit failed to start:")
                print(output)
                return False
            
            # Check if we can connect to the port
            if not check_port_available(port):
                print(f"✅ Server is running on http://localhost:{port}")
                print("🎉 Phishing Detection System is ready!")
                break
            
            # Check for timeout
            if time.time() - start_time > startup_timeout:
                print("⏰ Startup timeout - but server might still be starting...")
                break
            
            time.sleep(0.5)
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
            print("✅ Server stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return False

def main():
    """Main function"""
    success = launch_streamlit()
    
    if not success:
        print("\n💡 Troubleshooting options:")
        print("1. Try: python3 demo_results.py (command-line demo)")
        print("2. Check for port conflicts")
        print("3. Restart terminal and try again")

if __name__ == "__main__":
    main()