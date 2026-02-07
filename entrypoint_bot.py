#!/usr/bin/env python3
# entrypoint_bot.py - הפעלת בוט טלגרם בלבד

import os
import sys

print("=" * 50)
print("🤖 SLH Airdrop Bot - Starting...")
print("=" * 50)

# בדוק משתני סביבה
required_vars = ["TELEGRAM_TOKEN", "ADMIN_ID"]
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing environment variables: {missing_vars}")
    print("Please set these variables in Railway dashboard")
    sys.exit(1)

print(f"✅ TELEGRAM_TOKEN: {'Set' if os.getenv('TELEGRAM_TOKEN') else 'Not set'}")
print(f"✅ ADMIN_ID: {os.getenv('ADMIN_ID', 'Not set')}")
print(f"✅ API_URL: {os.getenv('API_URL', 'Not set (optional)')}")

# הרץ את הבוט
try:
    from app.bot_worker import main
    main()
except Exception as e:
    print(f"❌ Failed to start bot: {e}")
    sys.exit(1)
