#!/usr/bin/env python3
"""
Script para obtener chat IDs de Telegram y testear el bot.
Ejecutar: python get_chat_id.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_bot_info():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print(f"🤖 Bot Token: {token[:10]}...")
    
    # Get bot info
    response = requests.get(f'https://api.telegram.org/bot{token}/getMe')
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"✅ Bot: @{bot_info['username']} ({bot_info['first_name']})")
    else:
        print("❌ Error getting bot info")
        return None
    
    return token

def get_updates(token):
    print("\n📥 Getting recent updates...")
    
    response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates')
    if response.status_code != 200:
        print("❌ Error getting updates")
        return
    
    updates = response.json().get('result', [])
    
    if not updates:
        print("⚠️ No recent messages found.")
        print("💡 Send a message to the bot or add it to a channel/group, then run this script again.")
        return
    
    print(f"📊 Found {len(updates)} recent updates:")
    
    unique_chats = {}
    
    for update in updates:
        chat = None
        message_type = ""
        
        if 'message' in update:
            chat = update['message']['chat']
            message_type = "message"
        elif 'channel_post' in update:
            chat = update['channel_post']['chat']
            message_type = "channel_post"
        elif 'edited_message' in update:
            chat = update['edited_message']['chat']
            message_type = "edited_message"
        
        if chat:
            chat_id = chat['id']
            chat_type = chat['type']
            title = chat.get('title', chat.get('first_name', 'N/A'))
            
            unique_chats[chat_id] = {
                'type': chat_type,
                'title': title,
                'message_type': message_type
            }
    
    print("\n🔍 Unique chats found:")
    for chat_id, info in unique_chats.items():
        print(f"   Chat ID: {chat_id}")
        print(f"   Type: {info['type']}")
        print(f"   Title: {info['title']}")
        print(f"   Message Type: {info['message_type']}")
        print("   " + "-" * 40)

def send_test_message(token, chat_id):
    """Send a test message to verify the chat ID works"""
    message = "🤖 Test message from Trading Bot!\n\nIf you see this, the chat ID is working correctly."
    
    response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', {
        'chat_id': chat_id,
        'text': message
    })
    
    if response.status_code == 200:
        print(f"✅ Test message sent successfully to chat {chat_id}")
        return True
    else:
        print(f"❌ Failed to send message to chat {chat_id}")
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Telegram Chat ID Finder")
    print("=" * 50)
    
    token = get_bot_info()
    if token:
        get_updates(token)
        
        print("\n💡 Instructions:")
        print("1. Copy the Chat ID you want to use")
        print("2. Add it to your .env file as TELEGRAM_CHAT_ID")
        print("3. For channels, the ID will be negative (e.g., -1001234567890)")
        print("4. For private chats, the ID will be positive (e.g., 123456789)")
        
        # Optional: test a specific chat ID
        test_chat = input("\n🧪 Enter a chat ID to test (or press Enter to skip): ").strip()
        if test_chat:
            try:
                chat_id = int(test_chat)
                send_test_message(token, chat_id)
            except ValueError:
                print("❌ Invalid chat ID format")