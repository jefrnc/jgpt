#!/usr/bin/env python3
"""
Script simple para obtener el Chat ID de un canal de Telegram
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        return
    
    print(f"🤖 Bot Token: {token[:10]}...")
    
    # Get bot info
    response = requests.get(f'https://api.telegram.org/bot{token}/getMe')
    if response.status_code == 200:
        bot = response.json()['result']
        print(f"✅ Bot: @{bot['username']} ({bot['first_name']})")
    else:
        print("❌ Error conectando con el bot")
        return
    
    print("\n📋 INSTRUCCIONES:")
    print("1. Agrega el bot a tu canal como administrador")
    print("2. En el canal, envía este mensaje exacto: /get_id")
    print("3. Espera 5 segundos")
    print("4. Presiona Enter aquí para continuar...")
    input()
    
    # Get updates
    print("\n🔍 Buscando mensajes recientes...")
    response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates')
    
    if response.status_code != 200:
        print("❌ Error obteniendo updates")
        return
    
    updates = response.json().get('result', [])
    
    if not updates:
        print("⚠️ No hay mensajes. Intenta de nuevo.")
        return
    
    # Look for channels
    channels_found = {}
    private_chats = {}
    
    for update in updates:
        # Check channel posts
        if 'channel_post' in update:
            chat = update['channel_post']['chat']
            channels_found[chat['id']] = chat.get('title', 'Unknown')
        
        # Check private messages
        elif 'message' in update:
            chat = update['message']['chat']
            if chat['type'] == 'private':
                private_chats[chat['id']] = chat.get('first_name', 'Unknown')
        
        # Check when bot is added to groups/channels
        elif 'my_chat_member' in update:
            chat = update['my_chat_member']['chat']
            if chat['type'] in ['channel', 'supergroup']:
                channels_found[chat['id']] = chat.get('title', 'Unknown')
    
    print("\n✅ RESULTADOS:")
    
    if channels_found:
        print("\n📢 CANALES ENCONTRADOS:")
        for chat_id, title in channels_found.items():
            print(f"   Nombre: {title}")
            print(f"   Chat ID: {chat_id}")
            print(f"   👆 USA ESTE ID PARA LAS NOTIFICACIONES")
            print("   " + "-" * 40)
    
    if private_chats:
        print("\n💬 CHATS PRIVADOS:")
        for chat_id, name in private_chats.items():
            print(f"   Usuario: {name}")
            print(f"   Chat ID: {chat_id}")
            print("   " + "-" * 40)
    
    if not channels_found and not private_chats:
        print("⚠️ No se encontraron chats")
        print("Asegúrate de:")
        print("1. Agregar el bot como administrador del canal")
        print("2. Enviar un mensaje en el canal")
        print("3. Esperar unos segundos antes de ejecutar este script")
    
    # Clear updates
    if updates:
        last_id = updates[-1]['update_id']
        requests.get(f'https://api.telegram.org/bot{token}/getUpdates?offset={last_id + 1}')
        print(f"\n🧹 Updates limpiados hasta ID: {last_id}")

if __name__ == "__main__":
    main()