FROM python:3.11-slim

WORKDIR /app

# התקן דרישות
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתק קבצים
COPY . .

# צור תיקיית data
RUN mkdir -p data

# הרץ את ה-API
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
