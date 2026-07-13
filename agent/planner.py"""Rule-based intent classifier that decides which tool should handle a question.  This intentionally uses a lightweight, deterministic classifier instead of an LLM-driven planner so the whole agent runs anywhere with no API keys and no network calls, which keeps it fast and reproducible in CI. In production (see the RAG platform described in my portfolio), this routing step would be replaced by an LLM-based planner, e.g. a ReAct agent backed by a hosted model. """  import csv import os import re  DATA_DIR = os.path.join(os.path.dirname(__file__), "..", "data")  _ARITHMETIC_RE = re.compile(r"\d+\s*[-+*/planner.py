"""Rule-based intent classifier that decides which tool should handle a question.

This intentionally uses a lightweight, deterministic classifier instead of an
LLM-driven planner so the whole agent runs anywhere with no API keys and no
network calls, which keeps it fast and reproducible in CI. In production
(see the RAG platform described in my portfolio), this routing step would be
replaced by an LLM-based planner, e.g. a ReAct agent backed by a hosted model.
"""

import csv
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

_ARITHMETIC_RE = re.compile(r"\d+\s*[-+*/]\s*\d+")
_LOOKUP_KEYWORDS = ("stock", "units", "price", "cost", "how much", "category")


def _product_names():
    path = os.path.join(DATA_DIR, "products.csv")
    with open(path, newline="", encoding="utf-8") as f:
        return [row["name"].lower() for row in csv.DictReader(f)]


def classify_intent(question: str) -> str:
    """Return one of "calculator", "sql_lookup", or "doc_search"."""
    if _ARITHMETIC_RE.search(question):
        return "calculator"

    question_lower = question.lower()
    mentions_product = any(name in question_lower for name in _product_names())
    mentions_lookup_keyword = any(kw in question_lower for kw in _LOOKUP_KEYWORDS)
    if mentions_product or mentions_lookup_keyword:
        return "sql_lookup"

    return "doc_search"
