import argparse
import json
import random
import html
import requests
from pydantic import BaseModel, ValidationError
from typing import List, Optional

# --- Classes & Pydantic ---
class Question(BaseModel):
    category: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    all_answers: List[str] = []

    def prepare_answers(self):
        self.all_answers = self.incorrect_answers + [self.correct_answer]
        random.shuffle(self.all_answers)

class TriviaGame:
    def __init__(self, num_players: int):
        self.players_scores = [0] * num_players
        self.current_player_idx = 0
        self.questions_pool: List[Question] = []
        self.current_question: Optional[Question] = None

    # --- JSON Parsing & Exceptions ---
    def load_questions_from_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # שימוש ב-Pydantic לתיקוף הנתונים מהקובץ
                    q = Question(**item)
                    q.prepare_answers()
                    self.questions_pool.append(q)
            random.shuffle(self.questions_pool) # דרישה: סדר שאלות שונה בכל פעם
            print(f"Loaded {len(self.questions_pool)} questions from file.")
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            return False
        except json.JSONDecodeError:
            print(f"Error: Failed to decode JSON from '{file_path}'.")
            return False
        except ValidationError as e:
            print(f"Error: Data in file doesn't match the required format: {e}")
            return False
        return True

    # --- Extra Feature: API ---
    def fetch_from_api(self):
        print("Fetching extra questions from API...")
        url = "https://opentdb.com/api.php?amount=5&type=multiple"
        try:
            response = requests.get(url)
            data = response.json()
            for item in data["results"]:
                q = Question(
                    category=item["category"],
                    difficulty=item["difficulty"],
                    question=html.unescape(item["question"]),
                    correct_answer=html.unescape(item["correct_answer"]),
                    incorrect_answers=[html.unescape(ans) for ans in item["incorrect_answers"]]
                )
                q.prepare_answers()
                self.questions_pool.append(q)
        except Exception as e:
            print(f"Could not reach API: {e}")

    def play(self):
        if not self.questions_pool:
            print("No questions available. Game over.")
            return

        print(f"\n🎮 Game starts with {len(self.players_scores)} players!")
        
        while self.questions_pool or self.current_question:
            print(f"\n{'='*20}\nPLAYER {self.current_player_idx + 1} TURN")
            
            if not self.current_question:
                self.current_question = self.questions_pool.pop(0)

            print(f"Question: {self.current_question.question}")
            for i, ans in enumerate(self.current_question.all_answers):
                print(f"{i+1}. {ans}")

            try:
                choice = int(input("Your answer: ")) - 1
                if self.current_question.all_answers[choice] == self.current_question.correct_answer:
                    print("✅ Correct!")
                    self.players_scores[self.current_player_idx] += 1
                    self.current_question = None
                else:
                    print("❌ Wrong! Passing to next player...")
            except (ValueError, IndexError):
                print("Invalid input! Treat as wrong answer.")

            self.current_player_idx = (self.current_player_idx + 1) % len(self.players_scores)

        self.show_results()

    def show_results(self):
        print("\n--- FINAL SCORES ---")
        for i, score in enumerate(self.players_scores):
            print(f"Player {i+1}: {score}")

# --- Main Entry Point with Argparse ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Trivia Game")
    parser.add_argument("file", help="Path to the questions JSON file")
    parser.add_argument("--players", type=int, default=2, help="Number of players")
    args = parser.parse_args()

    game = TriviaGame(num_players=args.players)
    
    # ניסיון טעינה מהקובץ
    if game.load_questions_from_file(args.file):
        game.play()
    else:
        print("Failed to start game due to file error.")