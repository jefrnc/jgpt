#!/usr/bin/env python3
"""
Send deployment notification to Telegram
Usage: python send_telegram_notification.py <commit_sha> <commit_message>
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

def send_deployment_notification(commit_sha, commit_message):
    """Send deployment success notification to Telegram"""
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print('⚠️ Telegram credentials not configured')
        return False
    
    # Prepare message
    commit_sha_short = commit_sha[:7] if len(commit_sha) > 7 else commit_sha
    commit_msg_first_line = commit_message.split('\n')[0] if commit_message else 'No message'
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    message = f"""🚀 *Trading Bot Deployed Successfully*
    
📦 *Commit:* `{commit_sha_short}`
📝 *Message:* {commit_msg_first_line}
⏰ *Time:* {current_time}
🖥️ *Server:* GCP VM (flask-vm)

✅ Bot is running and scanning for gaps..."""
    
    # Send message
    try:
        response = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
        )
        
        if response.status_code == 200:
            print('✅ Deployment notification sent to Telegram')
            return True
        else:
            print(f'⚠️ Failed to send Telegram notification: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Error sending notification: {str(e)}')
        return False

if __name__ == '__main__':
    # Get arguments
    commit_sha = sys.argv[1] if len(sys.argv) > 1 else 'unknown'
    commit_message = sys.argv[2] if len(sys.argv) > 2 else 'No message provided'
    
    # Send notification
    send_deployment_notification(commit_sha, commit_message)