import json
import os
import random
import logging
import time
import sys
import select
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from colorama import Fore, Style, init
from models import Question

init(autoreset=True)
logger = logging.getLogger(__name__)

TIME_LIMIT_SEC = 30
API_QUESTION_COUNT = 5
MAX_QUESTIONS_PER_PLAYER = 10


class TriviaGame:
    def __init__(
        self,
        num_players: int,
        max_questions_per_player: int = MAX_QUESTIONS_PER_PLAYER,
        time_limit: int = TIME_LIMIT_SEC,
    ):
        if num_players < 1:
            raise ValueError("Number of players must be at least 1")
        if max_questions_per_player < 1:
            raise ValueError("Max questions per player must be at least 1")

        self.players_scores = [0] * num_players
        self.player_question_count = [0] * num_players
        self.current_player_idx = 0
        self.questions_pool: List[Question] = []
        self.current_question: Optional[Question] = None
        self.current_question_owner: Optional[int] = None
        self.current_question_retry = False
        self.time_limit = time_limit
        self.max_questions_per_player = max_questions_per_player
        self.max_questions_total = num_players * max_questions_per_player
        self.asked_questions = 0

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    def load_questions_from_file(self, file_path: str) -> bool:
        logger.info("Loading questions from file %s", file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Questions JSON should contain a list.")

            for item in data:
                try:
                    q = Question(**item)
                    q.prepare_answers()
                    self.questions_pool.append(q)
                except Exception as e:
                    logger.warning("Skipping invalid question: %s", e)

            if not self.questions_pool:
                logger.error("No valid questions loaded from file")
                return False

            random.shuffle(self.questions_pool)
            if len(self.questions_pool) > self.max_questions_total:
                self.questions_pool = self.questions_pool[: self.max_questions_total]

            logger.info("Loaded %d questions", len(self.questions_pool))
            return True

        except FileNotFoundError:
            logger.error("File not found: %s", file_path)
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", e)
        except Exception:
            logger.exception("Error while loading questions")

        return False

    def fetch_from_api(self):
        url = f"https://opentdb.com/api.php?amount={API_QUESTION_COUNT}&type=multiple"
        logger.info("Fetching questions from API")

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            new_questions = 0
            for item in data.get("results", []):
                try:
                    q = Question.from_opentdb_item(item)
                    q.prepare_answers()
                    self.questions_pool.append(q)
                    new_questions += 1
                except Exception as e:
                    logger.warning("Skipping invalid API question: %s", e)

            if new_questions > 0:
                random.shuffle(self.questions_pool)
                if len(self.questions_pool) > self.max_questions_total:
                    self.questions_pool = self.questions_pool[: self.max_questions_total]
                logger.info("Fetched %d questions from API", new_questions)
            else:
                logger.info("No questions fetched from API")

        except Exception as e:
            logger.warning("API fetch failed: %s", e)

    def print_welcome(self):
        self.clear_screen()
        logo = rf"""{Fore.CYAN}{Style.BRIGHT}
=============================================
||  _______  ______  ___  __   __  ___   __  ||
|| |__   __||  _   ||   ||  | |  ||   | |  | ||
||    | |   | |_)  ||   ||  | |  ||   | |  | ||
||    | |   |  _  / |   ||  |_|  ||   | |  | ||
||    | |   | | \ \ |   | \     / |   | |  | ||
||    |_|   |_|  \_\|___|  \___/  |___| |__| ||
=============================================
"""
        print(logo)
        print(f"{Fore.YELLOW}TRIVIA GAME")
        print(f"{Fore.GREEN}Answer with number 1-4, or 'q' to quit anytime")

    def get_input_with_countdown(self):
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            remaining = int(self.time_limit - elapsed)
            if remaining <= 0:
                return None, elapsed
            sys.stdout.write(f"\rTime remaining: {remaining}s | Your answer: ")
            sys.stdout.flush()
            input_ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if input_ready:
                return sys.stdin.readline().strip(), elapsed

    def show_status(self):
        remaining_per_player = [
            max(0, self.max_questions_per_player - count)
            for count in self.player_question_count
        ]
        score_line = " | ".join(
            [f"P{i+1}:{score} ({remaining_per_player[i]} left)" for i, score in enumerate(self.players_scores)]
        )
        pool_line = f"Questions in pool: {len(self.questions_pool)}"
        print(f"{Fore.MAGENTA}{pool_line} | {score_line}{Style.RESET_ALL}")

    def save_scores(self, path: str = "scores.json"):
        payload = {
            "datetime": datetime.utcnow().isoformat() + "Z",
            "players_scores": self.players_scores,
            "total_questions": self.max_questions_total,
            "asked_questions": self.asked_questions,
        }

        try:
            file_path = Path(path)
            if file_path.exists():
                with file_path.open("r", encoding="utf-8") as f:
                    existing = json.load(f)
            else:
                existing = {"sessions": []}

            existing.setdefault("sessions", []).append(payload)
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)

            logger.info("Saved score session to %s", path)
        except Exception:
            logger.exception("Failed to save scores")

    def show_results(self):
        self.clear_screen()
        print(f"{Fore.YELLOW}FINAL SCORES{Style.RESET_ALL}")
        for i, score in enumerate(self.players_scores):
            print(f"{Fore.CYAN}Player {i+1}:{Style.RESET_ALL} {score}")
        self.save_scores()

    def play(self):
        self.print_welcome()

        while any(count < self.max_questions_per_player for count in self.player_question_count) and (self.questions_pool or self.current_question):
            self.show_status()

            if self.player_question_count[self.current_player_idx] >= self.max_questions_per_player:
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players_scores)
                continue

            player_no = self.current_player_idx + 1
            next_player_no = ((self.current_player_idx + 1) % len(self.players_scores)) + 1

            if self.current_question is None:
                if not self.questions_pool:
                    break
                self.current_question = self.questions_pool.pop(0)
                self.current_question_owner = self.current_player_idx
                self.current_question_retry = False
                self.player_question_count[self.current_player_idx] += 1
                self.asked_questions += 1
            elif self.current_question_owner != self.current_player_idx:
                self.current_question_owner = self.current_player_idx
                self.player_question_count[self.current_player_idx] += 1
                self.asked_questions += 1

            print(f"\n{Fore.BLUE}PLAYER {player_no} TURN{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Question {self.asked_questions}/{self.max_questions_total}:{Style.RESET_ALL} {Fore.CYAN}{self.current_question.question}{Style.RESET_ALL}")
            for i, ans in enumerate(self.current_question.all_answers):
                print(f"{Fore.CYAN}{i+1}. {ans}{Style.RESET_ALL}")

            user_input, elapsed = self.get_input_with_countdown()
            print()

            if user_input is None:
                print(f"{Fore.RED}TIMEOUT{Style.RESET_ALL}")
                if not self.current_question_retry:
                    print(f"{Fore.YELLOW}Same question goes to next player {next_player_no}{Style.RESET_ALL}")
                    self.current_question_retry = True
                else:
                    print(f"{Fore.YELLOW}Second fail. Next question.{Style.RESET_ALL}")
                    self.current_question = None
                    self.current_question_owner = None
                    self.current_question_retry = False
            elif user_input.lower() == "q":
                print(f"{Fore.MAGENTA}Quit received{Style.RESET_ALL}")
                break
            else:
                try:
                    choice = int(user_input) - 1
                    if choice < 0 or choice >= len(self.current_question.all_answers):
                        raise ValueError()

                    if self.current_question.all_answers[choice] == self.current_question.correct_answer:
                        print(f"{Fore.GREEN}Correct! Time: {elapsed:.2f}s{Style.RESET_ALL}")
                        self.players_scores[self.current_player_idx] += 1
                        self.current_question = None
                        self.current_question_owner = None
                        self.current_question_retry = False
                    else:
                        print(f"{Fore.RED}Wrong! Try again next player.{Style.RESET_ALL}")
                        if not self.current_question_retry:
                            print(f"{Fore.YELLOW}Same question goes to next player {next_player_no}{Style.RESET_ALL}")
                            self.current_question_retry = True
                        else:
                            print(f"{Fore.YELLOW}Second fail. Next question.{Style.RESET_ALL}")
                            self.current_question = None
                            self.current_question_owner = None
                            self.current_question_retry = False
                except ValueError:
                    print(f"{Fore.RED}Invalid input (1-4 or q){Style.RESET_ALL}")
                    if not self.current_question_retry:
                        print(f"{Fore.YELLOW}Same question goes to next player {next_player_no}{Style.RESET_ALL}")
                        self.current_question_retry = True
                    else:
                        print(f"{Fore.YELLOW}Second fail. Next question.{Style.RESET_ALL}")
                        self.current_question = None
                        self.current_question_owner = None
                        self.current_question_retry = False

            self.current_player_idx = (self.current_player_idx + 1) % len(self.players_scores)
            time.sleep(1.2)
            self.clear_screen()

        self.show_results()