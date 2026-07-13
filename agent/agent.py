"""The ResearchAgent: routes a question to a tool, with a fallback to
document search if the first tool comes back empty.

Tools are wrapped with LangChain's `Tool` abstraction so they can be
swapped for a real LangChain AgentExecutor later without changing their
implementations — only the orchestration in `run()` below would need to
change to a ReAct-style loop driven by an LLM.
"""

from langchain_core.tools import Tool

from .planner import classify_intent
from .tools import calculator_tool, doc_search_tool, sql_lookup_tool


class ResearchAgent:
    def __init__(self):
        self.tools = {
            "calculator": Tool(
                name="calculator",
                func=calculator_tool,
                description="Evaluates simple arithmetic expressions.",
            ),
            "sql_lookup": Tool(
                name="sql_lookup",
                func=sql_lookup_tool,
                description="Looks up product price, stock, or category from the catalog.",
            ),
            "doc_search": Tool(
                name="doc_search",
                func=doc_search_tool,
                description="Searches company policy documents for a relevant passage.",
            ),
        }

    def run(self, question: str) -> dict:
        intent = classify_intent(question)
        answer = self.tools[intent].run(question)

        fallback_used = False
        if answer.startswith("NOT_FOUND") and intent != "doc_search":
            fallback_used = True
            intent = "doc_search"
            answer = self.tools["doc_search"].run(question)

        return {
            "tool_used": intent,
            "fallback_used": fallback_used,
            "answer": answer,
        }
