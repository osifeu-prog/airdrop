FROM python:3.11-slim

WORKDIR /app

# התקן תלויות
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתק קבצים
COPY . .

# צור תיקיות
RUN mkdir -p data templates

CMD ["echo", "Use Railway start commands"]
