import os

from questions_loader import load_questions
from interview_agent import select_questions


def test_load_questions():
    qdir = os.path.join(os.path.dirname(__file__), "..", "questions")
    qdir = os.path.normpath(qdir)
    qs = load_questions(qdir)
    assert len(qs) >= 2


def test_select_questions():
    qdir = os.path.join(os.path.dirname(__file__), "..", "questions")
    qdir = os.path.normpath(qdir)
    qs = load_questions(qdir)
    sel = select_questions(qs, tech="dotnet", role="backend", years=4, n=5)
    assert isinstance(sel, list)
    assert len(sel) >= 1
