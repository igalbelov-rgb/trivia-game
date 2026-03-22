#!/usr/bin/env python3

import argparse
import logging

from game import TriviaGame


def configure_logging(level: str):
    level_upper = getattr(logging, level.upper(), None)
    if level_upper is None:
        raise ValueError(f"Invalid log level: {level}")
    logging.basicConfig(
        level=level_upper,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def main():
    parser = argparse.ArgumentParser(
        description="CLI Trivia Game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "questions_file", 
        help="Path to questions JSON file"
    )
    parser.add_argument(
        "--players", 
        type=int, 
        default=2, 
        help="Number of players"
    )
    parser.add_argument(
        "--time_limit", 
        type=int, 
        default=30, 
        help="Seconds per question"
    )
    parser.add_argument(
        "--max_per_player", 
        type=int, 
        default=10, 
        help="Questions per player"
    )
    parser.add_argument(
        "--log_level", 
        default="INFO", 
        help="Log level"
    )

    args = parser.parse_args()

    try:
        configure_logging(args.log_level)
    except ValueError as e:
        logging.error(f"Error: {e}")
        return

    # Initialize and run the game
    game = TriviaGame(
        num_players=args.players,
        max_questions_per_player=args.max_per_player,
        time_limit=args.time_limit
    )

    if not game.load_questions_from_file(args.questions_file):
        logging.error("Failed to load questions. Exiting.")
        return

    game.play()

if __name__ == "__main__":
    main()