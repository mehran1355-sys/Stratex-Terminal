"""
سرویس صوت - تبدیل متن به صدا و صدا به متن
Voice Service Module
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECHRECOGNITION_AVAILABLE = True
except ImportError:
    SPEECHRECOGNITION_AVAILABLE = False


class VoiceConfig:
    def __init__(self, language: str = "fa", tts_enabled: bool = True, stt_enabled: bool = True):
        self.language = language
        self.tts_enabled = tts_enabled and GTTS_AVAILABLE
        self.stt_enabled = stt_enabled and SPEECHRECOGNITION_AVAILABLE
        self.voice_commands = {"تحلیل": "run_analysis", "گزارش": "generate_report", "وضعیت": "status", "توقف": "stop", "شروع": "start"}


class TextToSpeech:
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.temp_dir = Path(tempfile.gettempdir()) / "forex_voice"
        self.temp_dir.mkdir(exist_ok=True)

    def speak(self, text: str, filename: str = None) -> Optional[str]:
        if not self.config.tts_enabled:
            return None
        try:
            if filename is None:
                filename = f"voice_{hash(text)}.mp3"
            filepath = self.temp_dir / filename
            tts = gTTS(text=text, lang=self.config.language, slow=False)
            tts.save(str(filepath))
            return str(filepath)
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    def speak_alert(self, alert_type: str, **kwargs) -> Optional[str]:
        messages = {"signal": f"سیگنال جدید برای {kwargs.get('symbol', '')}", "tp_hit": f"حد سود برای {kwargs.get('symbol', '')} فعال شد", "sl_hit": f"هشدار! حد ضرر برای {kwargs.get('symbol', '')} فعال شد"}
        return self.speak(messages.get(alert_type, kwargs.get("message", "")))


class SpeechToText:
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.recognizer = sr.Recognizer() if SPEECHRECOGNITION_AVAILABLE else None

    def listen_from_microphone(self, timeout: int = 5) -> Optional[str]:
        if not self.config.stt_enabled or not self.recognizer:
            return None
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout)
            return self.recognizer.recognize_google(audio, language="fa-IR")
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None


class VoiceCommandHandler:
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.tts = TextToSpeech(config)
        self.stt = SpeechToText(config)
        self.command_handlers: Dict[str, callable] = {}

    def register_command(self, command_key: str, handler: callable):
        self.command_handlers[command_key] = handler

    def handle_voice_input(self, text: str) -> Optional[str]:
        for cmd_text, cmd_key in self.config.voice_commands.items():
            if cmd_text in text and cmd_key in self.command_handlers:
                return self.command_handlers[cmd_key]()
        return None


class VoiceService:
    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.tts = TextToSpeech(self.config)
        self.stt = SpeechToText(self.config)
        self.handler = VoiceCommandHandler(self.config)
