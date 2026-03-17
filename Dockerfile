# משתמשים בתמונה קלה של פייתון
FROM python:3.11-slim

# הגדרת תיקיית העבודה בתוך הקונטיינר
WORKDIR /app

# התקנת כלי מערכת בסיסיים אם צריך (עבור ספריות מסוימות)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# העתקת קובץ הדרישות והתקנתו
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת כל קבצי הקוד (cli.py, game.py, models.py וכו')
COPY . .

# חשיפת הפורט של המטריקות (Prometheus)
EXPOSE 8000

# פקודת ההרצה: מריצים את ה-CLI
# השתמשנו ב-JSON syntax כדי לאפשר קבלת סיגנלים של עצירה (SIGTERM)
ENTRYPOINT ["python", "cli.py"]

# ארגומנטים כברירת מחדל (קובץ השאלות ומספר שחקנים)
CMD ["questions.json", "--players", "2"]