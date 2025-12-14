import os
import glob
import re
from dataclasses import dataclass
from typing import List, Optional

import yaml


@dataclass
class Question:
    id: str
    tech: str
    roles: List[str]
    min_years: int
    max_years: int
    tags: List[str]
    question: str
    explanation: Optional[str] = None


_FRONT_MATTER_RE = re.compile(r"---\s*(.*?)\s*---\s*(.*?)(?=(?:\n---\s*)|$)", re.S)


def _normalize_roles(raw):
    if raw is None:
        return ["any"]
    if isinstance(raw, str):
        return [r.strip() for r in raw.split(",") if r.strip()]
    if isinstance(raw, list):
        return [str(r).strip() for r in raw]
    return [str(raw)]


def _normalize_tags(raw):
    if raw is None:
        return []
    if isinstance(raw, str):
        return [t.strip() for t in raw.split(",") if t.strip()]
    if isinstance(raw, list):
        return [str(t).strip() for t in raw]
    return [str(raw)]


def parse_questions_from_text(text: str, tech: str) -> List[Question]:
    matches = _FRONT_MATTER_RE.findall(text)
    questions: List[Question] = []
    for m in matches:
        yaml_str, body = m
        try:
            meta = yaml.safe_load(yaml_str) or {}
        except Exception:
            meta = {}
        qid = meta.get("id") or f"{tech}-{len(questions)+1}"
        roles = _normalize_roles(meta.get("role") or meta.get("roles"))
        min_years = int(meta.get("min_years", meta.get("min_year", 0) or 0))
        max_years = int(meta.get("max_years", meta.get("max_year", 100) or 100))
        tags = _normalize_tags(meta.get("tags"))
        explanation = meta.get("explanation")
        question_text = body.strip()
        questions.append(Question(
            id=str(qid),
            tech=tech,
            roles=roles,
            min_years=min_years,
            max_years=max_years,
            tags=tags,
            question=question_text,
            explanation=explanation
        ))
    return questions


def load_questions(directory: str) -> List[Question]:
    """Load all .md question files from a directory and return Question objects."""
    out: List[Question] = []
    pattern = os.path.join(directory, "*.md")
    for path in glob.glob(pattern):
        tech = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        parsed = parse_questions_from_text(text, tech)
        out.extend(parsed)
    return out


if __name__ == "__main__":
    # quick local smoke test
    qdir = os.path.join(os.path.dirname(__file__), "questions")
    if os.path.isdir(qdir):
        qs = load_questions(qdir)
        print(f"Loaded {len(qs)} questions from {qdir}")