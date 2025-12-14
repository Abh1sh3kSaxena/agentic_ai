import random
from typing import List, Optional

from questions_loader import Question, load_questions


def select_questions(questions: List[Question], tech: str, role: str, years: int, n: int = 5) -> List[Question]:
    """Select up to `n` questions matching tech, role and years.
    Relax constraints if not enough matches are available.
    """
    # strict match: tech + role + years
    candidates = [q for q in questions if q.tech == tech and (role in q.roles or 'any' in q.roles) and q.min_years <= years <= q.max_years]
    if len(candidates) >= n:
        random.shuffle(candidates)
        return candidates[:n]

    # relax years
    candidates = [q for q in questions if q.tech == tech and (role in q.roles or 'any' in q.roles)]
    if len(candidates) >= n:
        random.shuffle(candidates)
        return candidates[:n]

    # relax role
    candidates = [q for q in questions if q.tech == tech and q.min_years <= years <= q.max_years]
    if len(candidates) >= n:
        random.shuffle(candidates)
        return candidates[:n]

    # fallback: any question for tech
    candidates = [q for q in questions if q.tech == tech]
    random.shuffle(candidates)
    return candidates[:n]


class InterviewSession:
    def __init__(self, session_id: str, tech: str, role: str, years: int, selected_questions: List[Question]):
        self.session_id = session_id
        self.tech = tech
        self.role = role
        self.years = years
        self.selected_questions = selected_questions
        self.current_index = 0
        self.answers = {}  # qid -> answer text

    def get_next_question(self) -> Optional[Question]:
        if self.current_index >= len(self.selected_questions):
            return None
        q = self.selected_questions[self.current_index]
        self.current_index += 1
        return q

    def record_answer(self, qid: str, answer: str):
        self.answers[qid] = answer

    def is_finished(self) -> bool:
        return self.current_index >= len(self.selected_questions)


def get_explanation(question: Question) -> Optional[str]:
    return question.explanation


if __name__ == "__main__":
    qdir = "questions"
    qs = load_questions(qdir)
    sel = select_questions(qs, tech="dotnet", role="backend", years=4, n=5)
    print(f"Selected {len(sel)} questions for dotnet/backend/4y")