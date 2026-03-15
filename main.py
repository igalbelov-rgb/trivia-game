import argparse
import requests
import random
import html
from pydantic import BaseModel
from typing import List, Optional

class Question(BaseModel):
    category: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    all_answers: List[str] = []

    def prepare_answers(self):
        # Create a shuffled list of all possible answers
        self.all_answers = self.incorrect_answers + [self.correct_answer]
        random.shuffle(self.all_answers)

class TriviaGame:
    def __init__(self, num_players: int):
        self.players_scores = [0] * num_players
        self.current_player_idx = 0
        self.current_question: Optional[Question] = None
        self.categories = {
            "1": {"name": "General Knowledge", "id": 9},
            "2": {"name": "Science & Nature", "id": 17},
            "3": {"name": "History", "id": 23},
            "4": {"name": "Geography", "id": 22}
        }
        self.difficulties = ["easy", "medium", "hard"]

    def fetch_single_question(self, category_id: int, difficulty: str):
        url = f"https://opentdb.com/api.php?amount=1&category={category_id}&difficulty={difficulty}&type=multiple"
        try:
            response = requests.get(url)
            data = response.json()
            if data["response_code"] == 0:
                item = data["results"][0]
                q = Question(
                    category=item["category"],
                    difficulty=item["difficulty"],
                    question=html.unescape(item["question"]),
                    correct_answer=html.unescape(item["correct_answer"]),
                    incorrect_answers=[html.unescape(ans) for ans in item["incorrect_answers"]]
                )
                q.prepare_answers()
                return q
        except Exception:
            print("Error connecting to the trivia server.")
        return None

    def get_user_preferences(self):
        print("\n--- SELECT CATEGORY ---")
        for key, val in self.categories.items():
            print(f"{key}. {val['name']}")
        
        cat_choice = input("Enter category number: ")
        while cat_choice not in self.categories:
            cat_choice = input("Invalid choice. Try again: ")
            
        print("\n--- SELECT DIFFICULTY (easy, medium, hard) ---")
        diff_choice = input("Enter difficulty: ").lower()
        while diff_choice not in self.difficulties:
            diff_choice = input("Invalid choice. Try again: ")
            
        return self.categories[cat_choice]['id'], diff_choice

    def play(self):
        print(f"🎮 Game started with {len(self.players_scores)} players! 🎮")
        
        while True:
            print(f"\n{'='*30}")
            print(f"PLAYER {self.current_player_idx + 1} TURN")
            
            # If no inherited question, ask for preferences
            if not self.current_question:
                cat_id, diff = self.get_user_preferences()
                self.current_question = self.fetch_single_question(cat_id, diff)
                if not self.current_question:
                    print("No questions found, trying again...")
                    continue

            print(f"\nCategory: {self.current_question.category} ({self.current_question.difficulty})")
            print(f"Question: {self.current_question.question}")
            for i, ans in enumerate(self.current_question.all_answers):
                print(f"{i+1}. {ans}")

            try:
                ans_idx = int(input("\nYour answer (number): ")) - 1
                selected = self.current_question.all_answers[ans_idx]
            except (ValueError, IndexError):
                print("Invalid input.")
                continue

            if selected == self.current_question.correct_answer:
                print("✅ Correct! You got a point.")
                self.players_scores[self.current_player_idx] += 1
                self.current_question = None  # Question solved
            else:
                print("❌ Wrong! The question passes to the next player.")

            # Move to next player
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players_scores)
            
            cont = input("\nKeep playing? (y/n): ")
            if cont.lower() != 'y':
                break

        self.show_results()

    def show_results(self):
        print("\n" + "🏆" * 10)
        print("FINAL RESULTS:")
        for i, score in enumerate(self.players_scores):
            print(f"Player {i+1}: {score} points")
        
        max_score = max(self.players_scores)
        winners = [i+1 for i, s in enumerate(self.players_scores) if s == max_score]
        print(f"Winner(s): Player {winners}")
        print("🏆" * 10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, default=2)
    args = parser.parse_args()

    game = TriviaGame(num_players=args.players)
    game.play()