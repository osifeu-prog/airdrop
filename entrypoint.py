#!/usr/bin/env python3
# entrypoint.py - מנהל התהליכים הראשי

import os
import subprocess
import sys
import time
import threading

def run_api():
    """מפעיל את ה-FastAPI"""
    print("🚀 Starting FastAPI server...")
    os.environ["PORT"] = os.getenv("PORT", "8000")
    
    # הרץ את uvicorn עם האפליקציה כמחרוזת import
    cmd = [
        "uvicorn", 
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", os.environ["PORT"],
        "--workers", "1"
    ]
    
    subprocess.run(cmd)

def run_bot():
    """מפעיל את בוט הטלגרם"""
    print("🤖 Starting Telegram bot...")
    
    # המתן קצת שה-API יתחיל
    time.sleep(3)
    
    cmd = ["python", "app/bot_worker.py"]
    subprocess.run(cmd)

def main():
    """הפעל את כל השירותים"""
    print("=" * 50)
    print("🚀 SLH Airdrop System - Starting all services")
    print("=" * 50)
    
    # בדוק משתני סביבה
    required_vars = ["TELEGRAM_TOKEN", "API_URL", "ADMIN_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Warning: Missing environment variables: {missing_vars}")
    
    print(f"📡 API URL: {os.getenv('API_URL', 'Not set')}")
    print(f"🤖 Bot Token: {'Set' if os.getenv('TELEGRAM_TOKEN') else 'Not set'}")
    print(f"👑 Admin ID: {os.getenv('ADMIN_ID', 'Not set')}")
    
    # הפעל את ה-API בתהליך ראשי
    # הבוט ירוץ בתהליך נפרד
    import threading
    
    # הפעל את הבוט ב-thread נפרד
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    print("✅ All services started")
    print("=" * 50)
    
    # הרץ את ה-API (תהליך ראשי)
    run_api()

if __name__ == "__main__":
    main()
