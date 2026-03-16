import argparse
import logging
import sys

from game import TriviaGame


def configure_logging(level_name: str):
    level = getattr(logging, level_name.upper(), None)
    if level is None:
        raise ValueError(f"Invalid log level: {level_name}")

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(description="Trivia Game")
    parser.add_argument("file", help="Questions JSON file")
    parser.add_argument("--players", type=int, default=2, help="Number of players")
    parser.add_argument("--time_limit", type=int, default=30, help="Time limit per question in seconds")
    parser.add_argument("--max_per_player", type=int, default=10, help="Questions per player")
    parser.add_argument("--log_level", default="INFO", help="Log level: DEBUG, INFO, WARNING, ERROR")
    parser.add_argument("--no_api", action="store_true", help="Do not fetch extra questions from API")
    args = parser.parse_args()

    try:
        configure_logging(args.log_level)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    game = TriviaGame(
        num_players=args.players,
        max_questions_per_player=args.max_per_player,
        time_limit=args.time_limit,
    )

    if not game.load_questions_from_file(args.file):
        print("Failed to load questions.")
        sys.exit(1)

    if not args.no_api:
        game.fetch_from_api()

    game.play()


if __name__ == "__main__":
    main()
