"""Runs the agent against eval/eval_set.json and reports accuracy.

Exits with a non-zero status if either the tool-routing accuracy or the
answer accuracy falls below the threshold, so CI fails loudly on a
regression instead of silently shipping a worse agent.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent.agent import ResearchAgent  # noqa: E402

THRESHOLD = 0.85


def main() -> int:
    eval_path = os.path.join(os.path.dirname(__file__), "eval_set.json")
    with open(eval_path, encoding="utf-8") as f:
        cases = json.load(f)

    agent = ResearchAgent()
    correct_tool = 0
    correct_answer = 0
    rows = []

    for case in cases:
        result = agent.run(case["question"])
        tool_ok = result["tool_used"] == case["expected_tool"]
        answer_ok = case["expected_keyword"].lower() in result["answer"].lower()
        correct_tool += int(tool_ok)
        correct_answer += int(answer_ok)
        rows.append((case["question"], case["expected_tool"], result["tool_used"], tool_ok, answer_ok))

    total = len(cases)
    tool_accuracy = correct_tool / total
    answer_accuracy = correct_answer / total

    print(f"{'question':<58}{'expected':<13}{'got':<13}{'tool_ok':<9}{'answer_ok'}")
    for question, expected, got, tool_ok, answer_ok in rows:
        print(f"{question[:56]:<58}{expected:<13}{got:<13}{str(tool_ok):<9}{answer_ok}")

    print(f"\nTool routing accuracy: {tool_accuracy:.0%} ({correct_tool}/{total})")
    print(f"Answer accuracy: {answer_accuracy:.0%} ({correct_answer}/{total})")

    if tool_accuracy < THRESHOLD or answer_accuracy < THRESHOLD:
        print(f"\nFAILED: accuracy below the {THRESHOLD:.0%} threshold")
        return 1

    print("\nPASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
