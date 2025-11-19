#!/bin/bash
# Get Real Bot Token and Test Token Validator

echo "========================================================"
echo "🤖 Bot Token Setup Guide"
echo "========================================================"
echo ""
echo "To test the token validator with a real bot, you need to:"
echo ""
echo "Step 1: Create a Test Bot"
echo "  1. Open Telegram app"
echo "  2. Search for: @BotFather"
echo "  3. Send: /newbot"
echo "  4. Choose a name (e.g., 'My Test Bot')"
echo "  5. Choose a username (must end with 'bot', e.g., 'mytestbot_123bot')"
echo ""
echo "Step 2: Copy Your Bot Token"
echo "  BotFather will send you a message with your token like:"
echo "  123456789:ABCdefGHIjklMNOpqrsTUVwxyzABCDEFG"
echo ""
echo "Step 3: Set Environment Variable"
echo "  export TEST_BOT_TOKEN='your_token_here'"
echo ""
echo "Step 4: Run Test Script"
echo "  python scripts/test_with_real_token.py"
echo ""
echo "========================================================"
echo ""

# Check if token is already set
if [ -n "$TEST_BOT_TOKEN" ]; then
    echo "✅ TEST_BOT_TOKEN is already set!"
    echo ""
    echo "Running tests..."
    cd /home/abcdeveloper/projects/analyticbot
    python scripts/test_with_real_token.py
else
    echo "❌ TEST_BOT_TOKEN environment variable is not set"
    echo ""
    read -p "Do you have a bot token ready? (yes/no): " response
    
    if [ "$response" = "yes" ] || [ "$response" = "y" ]; then
        echo ""
        read -p "Enter your bot token: " token
        export TEST_BOT_TOKEN="$token"
        echo ""
        echo "Token set! Running tests..."
        echo ""
        cd /home/abcdeveloper/projects/analyticbot
        python scripts/test_with_real_token.py
    else
        echo ""
        echo "Please follow the steps above to create a bot first."
        echo "Then run this script again with your token."
    fi
fi
