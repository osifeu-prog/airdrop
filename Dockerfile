FROM python:3.11-slim

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