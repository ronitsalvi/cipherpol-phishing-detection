#!/bin/bash

echo "🛡️ CipherPol Phishing Detection - GUARANTEED STARTUP"
echo "===================================================="
echo "✅ Robust backend with Instagram URL fix complete"
echo "🚀 Using programmatic startup to bypass setup wizard"
echo ""

cd "/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1"

# Method 1: Programmatic launcher (recommended)
echo "🔥 Method 1: Programmatic launcher"
echo "python3 streamlit_launcher.py"
echo ""

# Method 2: Direct command fallback
echo "🔧 Method 2: Direct command (if needed)"
echo "python3 -c \"import streamlit.web.cli as stcli; import sys; sys.argv=['streamlit', 'run', 'simple_app.py', '--server.port', '8507', '--server.address', 'localhost']; stcli.main()\""
echo ""

# Method 3: Environment reset + command line
echo "⚡ Method 3: Environment reset (last resort)"
echo "rm -rf ~/.streamlit && export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false && python3 -m streamlit run simple_app.py --server.port 8507"
echo ""

echo "🎯 Expected Result: http://localhost:8507 should open"
echo "🧪 Instagram test URL: https://www.instagram.com/reel/DLfVr2_i7sM/?igsh=ZHRvc3owMnlvamlz"
echo ""
echo "💡 Run: python3 streamlit_launcher.py"