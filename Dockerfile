FROM python:3.11-slim

WORKDIR /app

# התקן תלות מערכת בסיסית
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# העתק קבצים
COPY requirements.txt .
COPY . .

# התקן תלויות Python
RUN pip install --no-cache-dir -r requirements.txt

# הרץ את המערכת
CMD ["python", "entrypoint.py"]
