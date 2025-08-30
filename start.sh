#!/bin/bash

# Simple launcher for Phishing Detection System
echo "🛡️ Starting Phishing Detection System..."

# Set environment variables to skip streamlit setup
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Create config directory if it doesn't exist
mkdir -p ~/.streamlit

# Create streamlit config
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8504
enableCORS = false
enableXsrfProtection = false
headless = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
EOF

echo "✅ Configuration created"
echo "🚀 Starting application on http://localhost:8504"
echo "💡 Use Ctrl+C to stop the server"
echo ""

# Start streamlit
/Users/ronitsalvi/Library/Python/3.8/bin/streamlit run app.py --server.port 8504 --server.address localhost