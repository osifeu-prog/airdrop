FROM python:3.11-slim

WORKDIR /app

# התקן דרישות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# העתק דרישות והתקן
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתק את כל הקבצים
COPY . .

# צור תיקיית data
RUN mkdir -p data

# הרץ את ה-API
CMD ["python", "app/main.py"]
