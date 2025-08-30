#!/bin/bash

echo "🛡️ Starting Phishing Detection System for CipherPol Hackathon"
echo "============================================================"

cd "/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1"

echo "🚀 Launching Streamlit on port 8507..."
echo "🌐 URL: http://localhost:8507"
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Set environment to skip setup
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Launch streamlit
echo "" | python3 -m streamlit run simple_app.py --server.port 8507 --server.address localhost --server.headless false

echo ""
echo "✅ Demo session ended"