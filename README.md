# agentic-research-assistant

A small tool-using research agent: it looks at a question, picks one of three tools to answer it, calls that tool, and falls back to document search if the first attempt comes up empty. The interesting part isn't really the tools themselves -- it's the routing/fallback logic and the eval harness that actually measures whether the routing works, instead of a single hard-coded demo call.

## Try it

```
pip install -r requirements.txt
python main.py "How many units of Widget A are in stock?"
python eval/run_eval.py
```

The eval script runs the agent over 20 labeled cases and fails the build if tool-routing or answer accuracy drops below 85%.

## Why a rule-based planner instead of an LLM?

The planner that decides which tool to call is a small, deterministic classifier, not an LLM-driven ReAct loop. That's deliberate, for the same reason the other demos in this profile avoid cloud credentials: anyone can clone this repo and run the full test suite with no API keys, no network calls, and no cost, and the behavior is 100% reproducible in CI. Tools are still defined using LangChain's Tool abstraction (see agent/agent.py), so swapping the planner for a real LLM-based agent later is a change to the orchestration in ResearchAgent.run(), not to the tools themselves.

## How a question moves through the system

```
question
  -> classify_intent() in agent/planner.py (keyword/regex rules)
     -> "calculator"  -> calculator_tool()   (safe arithmetic via ast, no eval())
     -> "sql_lookup"  -> sql_lookup_tool()   (reads data/products.csv)
     -> "doc_search"  -> doc_search_tool()   (keyword-overlap search over data/docs/*.txt)
  -> if the chosen tool returns NOT_FOUND, retry once with doc_search
  -> {tool_used, fallback_used, answer}
```

## Layout

- `agent/tools.py` -- calculator, sql_lookup, doc_search implementations
- `agent/planner.py` -- classify_intent(): rule-based tool routing
- `agent/agent.py` -- ResearchAgent: orchestration + fallback logic
- `data/products.csv` -- small product catalog used by sql_lookup
- `data/docs/*.txt` -- sample policy docs used by doc_search
- `eval/eval_set.json` -- 20 question/expected-tool/expected-keyword cases
- `eval/run_eval.py` -- runs the eval set, fails the build below 85% accuracy

## What would change in production

The planner would become an LLM-based ReAct agent instead of a keyword classifier, the same swap I describe for the RAG platform in my portfolio. Document search would run against OpenSearch with real embeddings instead of keyword overlap (see mini-rag-pipeline for that pattern). The SQL tool would hit a real warehouse instead of a CSV. None of that changes the shape of the code much -- swapping the planner means changing how ResearchAgent.run() decides which tool to call, not the tools themselves, since they're already defined as LangChain Tool objects.

## A note on honesty

Calling this "agentic" while the router is a handful of regex rules could read as oversold, so to be direct about it: there is no LLM call anywhere in this repo. The planning/tool-selection/fallback control flow is the same shape you'd see in a production agent, but the decision of which tool to call is deterministic, not model-driven. I'd rather say that plainly here than have it come up as a surprise later.

MIT license.
