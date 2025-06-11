import os
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from src.utils.logger import setup_logger
import pytz

load_dotenv()


class TelegramAlertBot:
    def __init__(self):
        self.logger = setup_logger('telegram_bot')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.eastern = pytz.timezone('US/Eastern')
        
        if not self.bot_token:
            self.logger.warning("TELEGRAM_BOT_TOKEN not configured - alerts disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.application = Application.builder().token(self.bot_token).build()
        self.bot = Bot(self.bot_token)
        
        # Add command handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup bot command handlers"""
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("alerts", self.cmd_alerts))
        self.application.add_handler(CommandHandler("stop", self.cmd_stop))
        
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "🚀 *Small-Cap Trading Bot Activado!*\n\n"
                f"Tu Chat ID: `{chat_id}`\n"
                "Agrega este ID a tu archivo .env como TELEGRAM_CHAT_ID\n\n"
                "Comandos disponibles:\n"
                "/help - Ver todos los comandos\n"
                "/status - Estado del bot\n"
                "/alerts - Activar/desactivar alertas"
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        self.logger.info(f"Bot started for chat_id: {chat_id}")
        
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "📋 *Comandos Disponibles:*\n\n"
                "/start - Iniciar bot y obtener Chat ID\n"
                "/help - Mostrar esta ayuda\n"
                "/status - Ver estado del scanner\n"
                "/alerts on/off - Activar/desactivar alertas\n"
                "/stop - Detener el bot\n\n"
                "El bot enviará alertas automáticas cuando detecte gaps significativos."
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # This would connect to the main scanner status
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "📊 *Estado del Sistema:*\n\n"
                "✅ Bot: Activo\n"
                "✅ Scanner: Funcionando\n"
                f"⏰ Hora: {datetime.now(self.eastern).strftime('%H:%M:%S ET')}\n"
                "📈 Mercado: Verificando..."
            ),
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        args = context.args
        if not args:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Uso: /alerts on|off"
            )
            return
            
        if args[0].lower() == 'on':
            # Enable alerts logic here
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Alertas activadas"
            )
        elif args[0].lower() == 'off':
            # Disable alerts logic here
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔕 Alertas desactivadas"
            )
            
    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👋 Bot detenido. Usa /start para reactivar."
        )
        
    def format_gap_alert(self, gap_data: Dict) -> str:
        """Format gap data for Telegram message"""
        direction_emoji = "🟢" if gap_data['gap_direction'] == 'UP' else "🔴"
        gap_percent = abs(gap_data['gap_percent'])
        
        # Determine alert level
        if gap_percent >= 20:
            alert_emoji = "🚨🚨🚨"
            alert_text = "MEGA GAP!"
        elif gap_percent >= 10:
            alert_emoji = "🔥🔥"
            alert_text = "HOT GAP!"
        else:
            alert_emoji = "📊"
            alert_text = "Gap Alert"
            
        message = (
            f"{alert_emoji} *{alert_text}* {alert_emoji}\n\n"
            f"{direction_emoji} *${gap_data['symbol']}* {direction_emoji}\n"
            f"Gap: *{gap_data['gap_direction']} {gap_percent:.1f}%*\n"
            f"Precio: ${gap_data['previous_close']:.2f} → ${gap_data['current_price']:.2f}\n"
            f"Volumen: {gap_data['volume']:,}\n\n"
        )
        
        # Add potential setup info
        if gap_percent >= 10:
            message += "💡 *Setup Potencial:* Gap & Go\n"
            message += f"🎯 Target: ${gap_data['current_price'] * 1.05:.2f} (+5%)\n"
            message += f"🛑 Stop: ${gap_data['current_price'] * 0.97:.2f} (-3%)\n"
            
        message += f"\n⏰ {datetime.now(self.eastern).strftime('%H:%M:%S ET')}"
        
        return message
        
    async def send_alert(self, message: str):
        """Send alert to configured chat"""
        if not self.enabled or not self.chat_id:
            self.logger.warning("Telegram alerts not configured")
            return
            
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            self.logger.info("Alert sent successfully")
        except Exception as e:
            self.logger.error(f"Error sending alert: {str(e)}")
            
    async def send_gap_alerts(self, gaps: List[Dict]):
        """Send alerts for multiple gaps"""
        if not gaps:
            return
            
        for gap in gaps[:5]:  # Limit to top 5 to avoid spam
            message = self.format_gap_alert(gap)
            await self.send_alert(message)
            await asyncio.sleep(1)  # Avoid rate limiting
            
    async def send_summary(self, gaps: List[Dict]):
        """Send daily summary of gaps"""
        if not gaps:
            message = "📊 *Resumen del Día*\n\nNo se detectaron gaps significativos hoy."
        else:
            message = f"📊 *Resumen del Día*\n\n"
            message += f"Total gaps detectados: {len(gaps)}\n\n"
            
            # Top 3 gaps
            message += "*Top 3 Gaps:*\n"
            for i, gap in enumerate(gaps[:3], 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                message += f"{emoji} ${gap['symbol']}: {gap['gap_direction']} {abs(gap['gap_percent']):.1f}%\n"
                
        await self.send_alert(message)
        
    def run(self):
        """Run the bot"""
        if not self.enabled:
            self.logger.error("Bot not enabled - missing TELEGRAM_BOT_TOKEN")
            return
            
        self.logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)