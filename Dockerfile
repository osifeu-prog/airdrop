FROM python:3.11-slim
<<<<<<< HEAD

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps from backend requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend code
COPY backend/ /app/

# Railway provides $PORT; default 8080 for local
CMD ["sh","-lc","python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
=======
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p certificates && chmod 777 certificates
# מחיקת ה-CMD הקבוע כדי לאפשר ל-Railway להחליט
>>>>>>> 03e5c1437b28768ba89ff31f6cea0fc62306fdf0
