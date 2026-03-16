import random
import html
from typing import List
from pydantic import BaseModel, Field


class Question(BaseModel):
    category: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    all_answers: List[str] = Field(default_factory=list)

    def prepare_answers(self):
        self.all_answers = self.incorrect_answers + [self.correct_answer]
        random.shuffle(self.all_answers)

    @classmethod
    def from_opentdb_item(cls, item: dict):
        return cls(
            category=item["category"],
            difficulty=item["difficulty"],
            question=html.unescape(item["question"]),
            correct_answer=html.unescape(item["correct_answer"]),
            incorrect_answers=[html.unescape(ans) for ans in item.get("incorrect_answers", [])],
        )
