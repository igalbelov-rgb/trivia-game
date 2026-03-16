import argparse
import json
import random
import html
import requests
import time
import os
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from colorama import Fore, Style, init

# אתחול colorama - חשוב כדי שיעבוד טוב גם ב-WSL וגם בטרמינלים שונים
init(autoreset=True)

load_dotenv()
password = os.getenv("DB_PASSWORD")

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

    def load_questions_from_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    q = Question(**item)
                    q.prepare_answers()
                    self.questions_pool.append(q)
            random.shuffle(self.questions_pool)
            print(f"{Fore.CYAN}Loaded {len(self.questions_pool)} questions from file.{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Error loading file: {e}{Style.RESET_ALL}")
            return False

    def fetch_from_api(self):
        print(f"{Fore.YELLOW}Fetching extra questions from API...{Style.RESET_ALL}")
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
            print(f"{Fore.RED}Could not reach API: {e}{Style.RESET_ALL}")

    def play(self):
        if not self.questions_pool:
            print(f"{Fore.RED}No questions available. Game over.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.MAGENTA}🎮 Game starts with {len(self.players_scores)} players!{Style.RESET_ALL}")
        
        while self.questions_pool or self.current_question:
            print(f"\n{Fore.BLUE}{'='*20}\nPLAYER {self.current_player_idx + 1} TURN{Style.RESET_ALL}")
            
            if not self.current_question:
                self.current_question = self.questions_pool.pop(0)

            print(f"{Fore.WHITE}{Style.BRIGHT}Question: {self.current_question.question}")
            for i, ans in enumerate(self.current_question.all_answers):
                print(f"{Fore.CYAN}{i+1}. {ans}")

            start_time = time.time()
            
            try:
                user_input = input(f"\n{Fore.YELLOW}Your answer (10s limit): {Style.RESET_ALL}")
                end_time = time.time()
                elapsed = end_time - start_time
                
                if elapsed > 10: # שיניתי ל-10 שניות כפי שכתוב ב-input
                    print(f"{Fore.RED}⏰ TOO SLOW! It took you {elapsed:.2f} seconds. No points!{Style.RESET_ALL}")
                    self.current_question = None
                else:
                    choice = int(user_input) - 1
                    if self.current_question.all_answers[choice] == self.current_question.correct_answer:
                        print(f"{Fore.GREEN}✅ CORRECT! (Time: {elapsed:.2f}s){Style.RESET_ALL}")
                        self.players_scores[self.current_player_idx] += 1
                        self.current_question = None
                    else:
                        print(f"{Fore.RED}❌ WRONG! (Time: {elapsed:.2f}s){Style.RESET_ALL}")
                        # אם אתה רוצה שהשאלה תעבור לשחקן הבא, אל תאפס את current_question
            
            except (ValueError, IndexError):
                print(f"{Fore.RED}Invalid input! Treat as wrong answer.{Style.RESET_ALL}")

            self.current_player_idx = (self.current_player_idx + 1) % len(self.players_scores)

        self.show_results()

    def show_results(self):
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}--- FINAL SCORES ---{Style.RESET_ALL}")
        for i, score in enumerate(self.players_scores):
            color = Fore.GREEN if score == max(self.players_scores) else Fore.WHITE
            print(f"{color}Player {i+1}: {score}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Trivia Game")
    parser.add_argument("file", help="Path to the questions JSON file")
    parser.add_argument("--players", type=int, default=2, help="Number of players")
    args = parser.parse_args()

    game = TriviaGame(num_players=args.players)
    game.load_questions_from_file(args.file)
    game.fetch_from_api() 
    
    if game.questions_pool:
        game.play()
    else:
        print(f"{Fore.RED}Failed to start game due to file error.{Style.RESET_ALL}")