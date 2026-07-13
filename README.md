# agentic-research-assistant

[![CI](https://github.com/aayushi-jha2018/agentic-research-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/aayushi-jha2018/agentic-research-assistant/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A small tool-using research agent. It looks at a question, decides which of three tools can answer it, calls that tool, and falls back to document search if the first attempt comes up empty. This demonstrates the core mechanics of an agentic workflow (planning, tool selection, fallback/retry) alongside a real evaluation harness, rather than a single hard-coded demo call.

## Why a rule-based planner instead of an LLM?

The planner that decides which tool to call is a small, deterministic classifier, not an LLM-driven ReAct loop. That is a deliberate choice, for the same reason the other demos in this profile avoid cloud credentials: it means anyone can clone this repo and run the full test suite with no API keys, no network calls, and no cost, and the behavior is 100% reproducible in CI. Tools are still defined using LangChain's `Tool` abstraction (see `agent/agent.py`), so swapping the planner for a real LLM-based agent later is a change to the orchestration in `ResearchAgent.run()`, not to the tools themselves. In production, this routing step would be replaced by an LLM-based planner, the same kind of swap described for the RAG platform in my [portfolio](https://github.com/aayushi-jha2018/portfolio).

## Architecture

```
question
   |
   v
classify_intent()  -- agent/planner.py  (keyword/regex rules)
   |
   +--> "calculator"   -> calculator_tool()   -- safe arithmetic via ast, no eval()
   +--> "sql_lookup"   -> sql_lookup_tool()   -- reads data/products.csv
   +--> "doc_search"   -> doc_search_tool()   -- keyword-overlap search over data/docs/*.txt
   |
   v
if the chosen tool returns NOT_FOUND, retry once with doc_search (fallback)
   |
   v
{tool_used, fallback_used, answer}
```

## Project structure

```
agentic-research-assistant/
|-- agent/
|   |-- tools.py      # calculator, sql_lookup, doc_search implementations
|   |-- planner.py    # classify_intent(): rule-based tool routing
|   `-- agent.py      # ResearchAgent: orchestration + fallback logic
|-- data/
|   |-- products.csv       # small product catalog used by sql_lookup
|   `-- docs/*.txt         # sample company policy docs used by doc_search
|-- eval/
|   |-- eval_set.json # 20 question/expected-tool/expected-keyword cases
|   `-- run_eval.py   # runs the agent over eval_set.json, fails if accuracy < 85%
`-- main.py            # CLI: ask the agent one question
```

## Running this project

```bash
pip install -r requirements.txt
python main.py "How many units of Widget A are in stock?"
python eval/run_eval.py
```

## What this demonstrates

- **Tool routing and orchestration**: a question is classified, dispatched to the right tool, and the agent retries with a different tool on failure, the same control-flow pattern used in production agentic systems, just with a deterministic planner instead of an LLM.
- **Evaluation-driven development**: correctness is measured with a real eval set (tool-routing accuracy and answer accuracy), not eyeballed outputs, and CI fails the build if accuracy regresses below 85%.
- **Safe tool implementation**: the calculator parses expressions with Python's `ast` module instead of calling `eval()` on arbitrary input.
- **Dependency-light design**: standard library plus `langchain-core` only, so it installs and runs anywhere in seconds.

In production (see my portfolio), the planner would be an LLM-based ReAct agent, the document search would run against OpenSearch with real embeddings instead of keyword overlap (see [mini-rag-pipeline](https://github.com/aayushi-jha2018/mini-rag-pipeline) for that pattern), and the SQL tool would query a real warehouse instead of a CSV.

## License

MIT — feel free to reuse this as a starting point.
