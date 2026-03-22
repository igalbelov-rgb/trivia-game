from models import Question


def test_question_prepare_answers():
    q = Question(
        category="Science",
        difficulty="easy",
        question="What is H2O?",
        correct_answer="Water",
        incorrect_answers=["O2", "CO2", "H2"]
    )
    q.prepare_answers()
    assert len(q.all_answers) == 4
    assert "Water" in q.all_answers
    assert set(q.all_answers) == {"Water", "O2", "CO2", "H2"}
