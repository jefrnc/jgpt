#!/bin/bash

# VM Setup Commands for Flash Research Integration
echo "🚀 Setting up Flash Research Integration on VM..."

# Update system
sudo apt update

# Install Chrome (required for Selenium)
echo "📦 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Flash Research Credentials
FLASH_RESEARCH_EMAIL=jsfrnc@gmail.com
FLASH_RESEARCH_PASSWORD=ge1hwZxFeN

# OpenAI API Key (optional - add your key)
# OPENAI_API_KEY=your_key_here

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Scanner Settings
SCANNER_INTERVAL=300
EOF
    echo "⚠️  Please edit .env file with your actual credentials"
fi

# Set executable permissions
chmod +x test_vm_deployment.py
chmod +x check_flash_research.py

echo "✅ Setup complete!"
echo ""
echo "🔍 Test the deployment:"
echo "  python3 test_vm_deployment.py"
echo ""
echo "🚀 Quick Flash Research check:"
echo "  python3 check_flash_research.py"
echo ""
echo "▶️  Run the bot:"
echo "  python3 src/main.py --once     # Single scan"
echo "  python3 src/main.py           # Continuous"