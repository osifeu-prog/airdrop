import aiohttp
import asyncio
import os

async def test_connection():
    print("🔗 בדיקת חיבור בין הבוט ל-API...")
    
    api_url = "https://successful-fulfillment-production.up.railway.app"
    api_key = "bot_api_key_123_secret_456"
    
    headers = {"X-API-Key": api_key}
    
    try:
        # בדוק חיבור בסיסי
        async with aiohttp.ClientSession() as session:
            # בדוק endpoint בריאות
            health_url = f"{api_url}/health"
            async with session.get(health_url, headers=headers) as response:
                if response.status == 200:
                    print(f"✅ API בריא: {await response.json()}")
                else:
                    print(f"❌ שגיאת API: {response.status}")
                    return False
            
            # בדוק admin panel
            admin_url = f"{api_url}/admin/dashboard?admin_key=airdrop_admin_2026"
            async with session.get(admin_url) as response:
                if response.status == 200:
                    print("✅ Admin panel זמין")
                else:
                    print(f"⚠️  Admin panel: {response.status}")
            
            return True
            
    except Exception as e:
        print(f"❌ שגיאת חיבור: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    if result:
        print("\n🎉 החיבור מוכן! הבוט יכול לתקשר עם ה-API.")
    else:
        print("\n⚠️  יש בעיות בחיבור. בדוק את ההגדרות.")
