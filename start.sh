#!/bin/bash

# תיקון נתיב Python
export PYTHONPATH=$PYTHONPATH:.

if [ ! -z "$TELEGRAM_TOKEN" ] || [ "$RAILWAY_SERVICE_NAME" == "bot" ]; then
    echo "Detected Bot Service - Running bot..."
    # הרצה כקובץ ישיר כדי למנוע בעיות מודול
    python3 backend/app/bot.py
else
    echo "Detected Backend Service - Syncing migrations..."
    
    # פקודת הקסם: אומרת ל-DB שהגרסה הנוכחית היא 001_initial (מתעלם מהעבר)
    alembic stamp 001_initial || alembic stamp head
    
    # הרצת המיגרציה (הוספת העמודות החסרות)
    alembic upgrade head
    
    echo "Starting FastAPI..."
    python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
fi
