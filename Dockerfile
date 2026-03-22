FROM python:3.11-slim

# מונע מפייתון לכתוב קבצי .pyc ומבטיח לוגים בזמן אמת
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# התקנת תלויות מערכת
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# התקנת ספריות פייתון (שכבה נפרדת ל-Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# יצירת משתמש והעתקת הקוד
RUN useradd -m appuser
COPY . .
RUN chown -R appuser:appuser /app

# מעבר למשתמש הלא-שורש
USER appuser

EXPOSE 8000

ENTRYPOINT ["python", "cli.py"]
CMD ["questions.json", "--players", "2"]