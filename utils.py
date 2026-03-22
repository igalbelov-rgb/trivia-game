
import logging

import requests

try:
    from config import API_QUESTION_COUNT
except ImportError:
    # אם הקובץ לא נמצא, נשתמש בברירת מחדל של 10
    API_QUESTION_COUNT = 10


def fetch_from_api():
    url = f"https://opentdb.com/api.php?amount={API_QUESTION_COUNT}&type=multiple"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data
    except Exception as e:
        logging.error(f"Error fetching from API: {e}")
        return None