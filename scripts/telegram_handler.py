import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os
from datetime import datetime

class TelegramHandler:
    def __init__(self, bot_token, chat_id):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.otp_data = {}  # {email: otp_code}
        self.waiting_for_otp = {}  # {email: True/False}
    
    async def send_notification(self, email, message):
        """Notification পাঠান"""
        full_message = f"""
╔════════════════════════════════╗
║  🔐 OG.COM REGISTRATION BOT 🔐 ║
╚════════════════════════════════╝

📧 Email: {email}

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Time: {self.get_time()}
        """
        print(f"\n[TELEGRAM NOTIFICATION]")
        print(full_message)
        print("[END NOTIFICATION]\n")
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=full_message
            )
            print(f"[✓] Telegram message sent successfully")
        except Exception as e:
            print(f"[✗] Telegram send failed: {e}")
    
    async def wait_for_otp(self, email, timeout=300):
        """OTP input অপেক্ষা করুন"""
        await self.send_notification(
            email,
            f"📬 OTP পাঠানো হয়েছে এই ইমেইলে\n\n"
            f"⏱️ {timeout} সেকেন্ডের মধ্যে কোড দিন:\n\n"
            f"/otp_{email.split('@')[0]} 123456"
        )
        
        print(f"\n[WAITING] OTP অপেক্ষা করছি {email} এর জন্য ({timeout}s)...")
        self.waiting_for_otp[email] = True
        
        # Timeout loop
        for i in range(timeout):
            if email in self.otp_data:
                otp = self.otp_data[email]
                del self.otp_data[email]
                self.waiting_for_otp[email] = False
                print(f"[✓ OTP RECEIVED] {email}: {otp}\n")
                return otp
            await asyncio.sleep(1)
            if i % 30 == 0 and i > 0:
                print(f"  ⏱️ {timeout - i}s remaining...")
        
        self.waiting_for_otp[email] = False
        print(f"[✗ TIMEOUT] OTP timeout for {email}\n")
        return None
    
    async def handle_otp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin থেকে OTP command পান"""
        message = update.message.text
        
        # Format: /otp_email 123456
        if message.startswith("/otp_"):
            parts = message.split()
            if len(parts) == 2:
                email_prefix = parts[0].replace("/otp_", "")
                otp_code = parts[1]
                
                # সব emails এ খুঁজুন যার prefix match করে
                for email in self.waiting_for_otp:
                    if email.split('@')[0] == email_prefix:
                        self.otp_data[email] = otp_code
                        await update.message.reply_text(
                            f"✅ OTP received for {email}: {otp_code}"
                        )
                        print(f"[✓ OTP INPUT] {email}: {otp_code}")
                        return
                
                await update.message.reply_text("❌ Email not found in waiting list")
    
    @staticmethod
    def get_time():
        return datetime.now().strftime("%H:%M:%S")

telegram_handler = None

async def init_telegram(bot_token, chat_id):
    """Telegram bot initialize করুন"""
    global telegram_handler
    telegram_handler = TelegramHandler(bot_token, chat_id)
    print("[✓] Telegram Bot initialized successfully")
    print(f"[✓] Bot Token: {bot_token[:20]}...")
    print(f"[✓] Chat ID: {chat_id}\n")
