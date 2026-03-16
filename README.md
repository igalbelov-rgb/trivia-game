# Trivia Game 🎮

A lightweight, turn-based trivia CLI game in Python.

## Quick overview

- Two or more players, each one answers multiple-choice questions.
- Time-limited input (default 30 seconds, adjustable via `--time_limit`).
- Each player gets a fixed number of questions (default 10, adjustable via `--max_per_player`).
- If player 1 misses or timeouts, player 2 gets the same question.
- If player 2 also misses, move to next question (no correct answer revealed).
- Correct answer = 1 point. Final scores saved to `scores.json`.

## Run locally

1. Players take turns answering multiple-choice questions.
2. Per player time limit (default 30 seconds).
3. Each player gets up to 10 questions (default, configurable).
4. If a player answers wrongly or times out, the same question is offered to the next player.
5. If the second player also misses, the game moves to a new question.
6. Correct answer gives +1 point to the current player.
7. Score summary shows current totals and remaining questions.
8. Final scores are written to `scores.json` with an append session log.

## Run locally

1. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: copy environment file

```bash
cp .env.example .env
```

4. Start game:

```bash
python3 main.py questions.json --players 2 --max_per_player 10 --time_limit 30 --log_level INFO
```

5. If you don't want API fetch (offline), add `--no_api`.

## Commands & flags

- `file` (positional): path to questions JSON.
- `--players`: number of players (default 2).
- `--time_limit`: seconds per question (default 30).
- `--max_per_player`: questions per player (default 10).
- `--log_level`: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- `--no_api`: skip fetching extra questions from opentdb.

## Testing

```bash
pytest -q
```

## Development notes

- Scores are logged in `scores.json` as additional sessions.
- `logging` is configured in `cli.py` and used in `game.py`.

Enjoy! 🎉

