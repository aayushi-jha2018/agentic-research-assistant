"""CLI entry point: ask the research agent a single question.

Example:
    python main.py "How many units of Widget A are in stock?"
"""

import argparse

from agent.agent import ResearchAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the research agent a question.")
    parser.add_argument("question", help="The question to ask the agent")
    args = parser.parse_args()

    agent = ResearchAgent()
    result = agent.run(args.question)

    tag = result["tool_used"] + (" (fallback)" if result["fallback_used"] else "")
    print(f"[tool used: {tag}]")
    print(result["answer"])


if __name__ == "__main__":
    main()
