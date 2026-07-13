"""Concrete tool implementations used by the research agent.

Each tool is deliberately dependency-light (standard library only) so the
whole project runs anywhere without API keys, a database server, or GPU
access. Tools return a string starting with "NOT_FOUND" when they cannot
answer a query, which the agent uses to decide whether to fall back to
another tool.
"""

import ast
import csv
import operator
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ---------------------------------------------------------------------------
# Calculator tool
# ---------------------------------------------------------------------------

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

_EXPRESSION_RE = re.compile(r"[-+*/().0-9\s]{3,}")


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def safe_eval(expression: str):
    """Evaluate a simple arithmetic expression without using eval()."""
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def calculator_tool(query: str) -> str:
    match = _EXPRESSION_RE.search(query)
    if not match:
        return "NOT_FOUND: no arithmetic expression detected in the question"
    expr = match.group(0).strip().rstrip(".")
    try:
        result = safe_eval(expr)
        return f"{expr} = {result}"
    except Exception as exc:  # noqa: BLE001 - surfaced as a NOT_FOUND tool result
        return f"NOT_FOUND: could not evaluate '{expr}' ({exc})"


# ---------------------------------------------------------------------------
# SQL-style product lookup tool (backed by a small CSV "table")
# ---------------------------------------------------------------------------


def _load_products():
    path = os.path.join(DATA_DIR, "products.csv")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sql_lookup_tool(query: str) -> str:
    query_lower = query.lower()
    for row in _load_products():
        if row["name"].lower() not in query_lower:
            continue
        if any(word in query_lower for word in ("stock", "units", "how many")):
            return f"{row['name']} has {row['stock']} units in stock."
        if any(word in query_lower for word in ("price", "cost", "how much")):
            return f"{row['name']} costs ${row['price']}."
        return (
            f"{row['name']}: category={row['category']}, "
            f"price=${row['price']}, stock={row['stock']}."
        )
    return "NOT_FOUND: no matching product in the catalog"


# ---------------------------------------------------------------------------
# Document search tool (keyword-overlap retrieval over local .txt files)
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-zA-Z']+")


def _tokenize(text: str):
    return _WORD_RE.findall(text.lower())


def _load_docs():
    docs_dir = os.path.join(DATA_DIR, "docs")
    docs = {}
    for fname in sorted(os.listdir(docs_dir)):
        if fname.endswith(".txt"):
            with open(os.path.join(docs_dir, fname), encoding="utf-8") as f:
                docs[fname] = f.read()
    return docs


def doc_search_tool(query: str) -> str:
    query_terms = set(_tokenize(query))
    best_doc, best_score, best_sentence = None, 0, None
    for fname, text in _load_docs().items():
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            score = len(query_terms & set(_tokenize(sentence)))
            if score > best_score:
                best_score, best_doc, best_sentence = score, fname, sentence.strip()
    if best_doc is None or best_score == 0:
        return "NOT_FOUND: no relevant passage found in the document set"
    return f"[{best_doc}] {best_sentence}"
