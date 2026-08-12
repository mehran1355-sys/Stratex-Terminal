"""
سرویس تلگرام
Telegram Service Module
"""

import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Callable
from io import BytesIO

logger = logging.getLogger(__name__)


class TelegramConfig:
    def __init__(self, bot_token: str, channel_id: str, admin_chat_ids: List[str] = None):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.admin_chat_ids = admin_chat_ids or []
        self.api_base = f"https://api.telegram.org/bot{bot_token}"


class TelegramService:
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.message_history: List[Dict] = []

    def send_message(self, text: str, chat_id: str = None, parse_mode: str = "HTML", reply_markup: Dict = None) -> Optional[int]:
        url = f"{self.config.api_base}/sendMessage"
        payload = {"chat_id": chat_id or self.config.channel_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            if result.get("ok"):
                msg_id = result["result"]["message_id"]
                self.message_history.append({"message_id": msg_id, "text": text[:100], "timestamp": datetime.now()})
                return msg_id
            else:
                logger.error(f"Telegram error: {result.get('description')}")
                return None
        except Exception as e:
            logger.error(f"Telegram exception: {e}")
            return None

    def send_photo(self, photo_bytes: bytes, caption: str = "", chat_id: str = None) -> Optional[int]:
        url = f"{self.config.api_base}/sendPhoto"
        files = {"photo": ("chart.png", BytesIO(photo_bytes), "image/png")}
        data = {"chat_id": chat_id or self.config.channel_id, "caption": caption, "parse_mode": "HTML"}
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()
            return result["result"]["message_id"] if result.get("ok") else None
        except Exception as e:
            logger.error(f"Photo error: {e}")
            return None

    def send_document(self, file_path: str, caption: str = "", chat_id: str = None) -> Optional[int]:
        url = f"{self.config.api_base}/sendDocument"
        try:
            with open(file_path, "rb") as f:
                files = {"document": f}
                data = {"chat_id": chat_id or self.config.channel_id, "caption": caption}
                response = requests.post(url, files=files, data=data, timeout=60)
            result = response.json()
            return result["result"]["message_id"] if result.get("ok") else None
        except Exception as e:
            logger.error(f"Document error: {e}")
            return None

    def send_trade_signal_message(self, symbol: str, timeframe: str, direction: str, break_type: str, entry_zones: Dict, tp1: float, tp2: float, sl: float, volume: float, signal_id: str, chart_image: bytes = None) -> tuple:
        emoji = "🟢" if direction == "صعودی" else "🔴"
        message = f"{emoji} <b>سیگنال معاملاتی</b> {emoji}\n\n"
        message += f"📊 <b>نماد:</b> {symbol}\n"
        message += f"⏰ <b>تایم‌فریم:</b> {timeframe}\n"
        message += f"📈 <b>جهت:</b> {direction}\n"
        message += f"🔍 <b>نوع شکست:</b> {break_type}\n\n"
        message += f"<b>سطوح:</b>\n  🎯 TP1: {tp1:.5f}\n  🎯 TP2: {tp2:.5f}\n  🛑 SL: {sl:.5f}\n\n"
        message += f"💰 <b>حجم:</b> {volume:.4f}"

        photo_id = None
        if chart_image:
            photo_id = self.send_photo(chart_image, f"📈 {symbol} - {timeframe}")

        keyboard = {"inline_keyboard": [[{"text": "✅ تأیید", "callback_data": f"approve_{signal_id}"}, {"text": "❌ لغو", "callback_data": f"reject_{signal_id}"}]]}
        msg_id = self.send_message(message, reply_markup=keyboard)
        return msg_id, photo_id

    def send_daily_report(self, report_text: str, excel_path: str = None):
        self.send_message(f"📊 <b>گزارش روزانه</b>\n{datetime.now().strftime('%Y-%m-%d')}\n\n{report_text}")
        if excel_path:
            self.send_document(excel_path, "📑 گزارش کامل")

    def send_error_alert(self, error_message: str, severity: str = "ERROR"):
        emoji = "🔴" if severity == "CRITICAL" else "⚠️"
        alert = f"{emoji} <b>{severity}</b> {emoji}\n\n⏰ {datetime.now()}\n📝 <code>{error_message}</code>"
        for admin_id in self.config.admin_chat_ids:
            self.send_message(alert, chat_id=admin_id)

    def set_webhook(self, webhook_url: str) -> bool:
        url = f"{self.config.api_base}/setWebhook"
        try:
            response = requests.post(url, json={"url": webhook_url}, timeout=10)
            return response.json().get("ok", False)
        except:
            return False
            message += f"\n\n🤖 Stratex Algo Bot"
