import argparse
import logging
import sys
# הוספתי כאן את start_http_server לייבוא
from prometheus_client import Counter, Gauge, start_http_server 

from game import TriviaGame

# Metrics
question_load_errors = Counter(
    'trivia_game_question_load_errors',
    'Number of failed question loads'
)
questions_per_player = Gauge(
    'trivia_game_questions_per_player',
    'Questions per player'
)

def configure_logging(level_name: str):
    level = getattr(logging, level_name.upper(), None)
    if level is None:
        raise ValueError(f"Invalid log level: {level_name}")
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def main():
    parser = argparse.ArgumentParser(description="Trivia Game")
    parser.add_argument("file", help="Questions JSON file")
    parser.add_argument("--players", type=int, default=2, help="Number of players")
    parser.add_argument("--time_limit", type=int, default=30, help="Time limit per question")
    parser.add_argument("--max_per_player", type=int, default=10, help="Questions per player")
    parser.add_argument("--log_level", default="INFO", help="Log level")
    parser.add_argument("--no_api", action="store_true", help="Skip API questions")
    parser.add_argument("--metrics_port", type=int, default=8000, help="Prometheus metrics port")
    args = parser.parse_args()

    try:
        configure_logging(args.log_level)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Set metrics
    questions_per_player.set(args.max_per_player)

    # --- התיקון כאן: קריאה ישירה לפונקציה בלי הקידומת prometheus_client ---
    try:
        start_http_server(port=args.metrics_port)
        logging.info(f"Prometheus metrics server started on port {args.metrics_port}")
    except Exception as e:
        logging.error(f"Failed to start metrics server: {e}")

    # Initialize game
    game = TriviaGame(
        num_players=args.players,
        max_questions_per_player=args.max_per_player,
        time_limit=args.time_limit
    )

    # Load questions
    if not game.load_questions_from_file(args.file):
        question_load_errors.inc()
        print("Failed to load questions.")
        sys.exit(1)

    if not args.no_api:
        game.fetch_from_api()

    game.play()

if __name__ == "__main__":
    main()