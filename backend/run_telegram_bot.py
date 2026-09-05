"""
Standalone Telegram Bot Runner.
Starts the long-polling daemon for Ethiopian Weather Alert notifications.

Usage:
    export TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"
    python run_telegram_bot.py
"""
import os
import sys
import logging

# Ensure backend root is on python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.notifications.telegram import run_telegram_polling, is_telegram_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

if __name__ == "__main__":
    print("=" * 60)
    print("  Ethiopian Weather Dashboard - Telegram Bot Service")
    print("=" * 60)

    if not is_telegram_configured():
        print("\n⚠️ WARNING: TELEGRAM_BOT_TOKEN environment variable is not set!")
        print("To run with a live bot, create a bot with @BotFather on Telegram and run:")
        print("  export TELEGRAM_BOT_TOKEN=\"your_bot_token\"")
        print("  python run_telegram_bot.py\n")
        print("The backend notification pipeline will automatically run in simulated dry-run mode.")
        sys.exit(0)

    print("\nStarting live Telegram polling... Press Ctrl+C to stop.")
    try:
        run_telegram_polling()
    except KeyboardInterrupt:
        print("\nTelegram bot stopped.")
