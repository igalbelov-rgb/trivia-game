import requests
import json
from config import API_QUESTION_COUNT

def fetch_from_api():
    url = f"https://opentdb.com/api.php?amount={API_QUESTION_COUNT}&type=multiple"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching from API: {e}")
        return None