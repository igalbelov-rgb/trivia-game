import json
from pathlib import Path
from models import Question
from game import TriviaGame


def test_load_questions_from_file(tmp_path):
    data = [
        {
            'category': 'Science',
            'difficulty': 'easy',
            'question': 'H2O is?',
            'correct_answer': 'Water',
            'incorrect_answers': ['O2', 'CO2', 'H2']
        }
    ]
    file_path = tmp_path / 'questions.json'
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f)

    game = TriviaGame(num_players=2, max_questions_per_player=1, time_limit=1)
    assert game.load_questions_from_file(str(file_path)) is True
    assert len(game.questions_pool) == 1


def test_save_scores_to_file(tmp_path):
    game = TriviaGame(num_players=2, max_questions_per_player=1)
    game.players_scores = [1, 2]
    game.asked_questions = 1

    scores_file = tmp_path / 'scores.json'
    game.save_scores(str(scores_file))

    with scores_file.open('r', encoding='utf-8') as f:
        content = json.load(f)

    assert 'sessions' in content
    assert content['sessions'][-1]['players_scores'] == [1, 2]
