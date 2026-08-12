# 🐛 AI-Powered Debugging Agent

An intelligent, multi-agent debugging workflow built with **LangGraph**, **FastAPI**, and **Groq LLM**. 

Instead of just spitting out a quick fix, this agent deeply analyzes broken code, explains the root cause, and provides two different solutions with tradeoffs. It even acts like a Senior Developer by generating regression tests (pytest) and docstrings to future-proof your codebase.

## Features

* **🧠 Multi-Agent Workflow:** Utilizes specialized AI agents (Error Analyzer, Fix Generator, Tradeoff Analyst, Concept Explainer, Test Writer).
* **⚖️ Tradeoff Analysis:** Provides two distinct fixes (Fix A & Fix B) and evaluates the pros and cons of each.
* **🔄 Teaching Loop:** If the AI's confidence is below 90% (e.g., ambiguous business logic), it triggers a loop to build a minimal reproducible example and verify the fix.
* **🛡️ Regression Tests:** Automatically writes a `pytest` block to prevent the bug from happening again.
* **📝 Auto-Documentation:** Generates a complete docstring explaining the function's behavior.
* **🎨 Modern UI:** A beautiful, responsive, glassmorphism-inspired dark mode frontend.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn
* **AI/LLM:** LangChain, LangGraph, Groq API (llama-3.3-70b-versatile)
* **Frontend:** HTML5, CSS3 (Custom Glassmorphism UI), Vanilla JavaScript

## 📁 Project Structure

```text
📦 debugging-agent
 ┣ 📂 tools
 ┃ ┣ 📜 agents.py      # LLM calls & Agent nodes
 ┃ ┣ 📜 graph.py       # LangGraph workflow setup
 ┃ ┗ 📜 state.py       # State definitions (DebugState)
 ┣ 📂 static
 ┃ ┣ 📜 style.css      # Custom UI styling
 ┃ ┗ 📜 main.js        # Frontend logic
 ┣ 📂 templates
 ┃ ┗ 📜 index.html     # Web UI
 ┣ 📜 app.py           # FastAPI entry point & routes
 ┣ 📜 backend.py       # API endpoints linking UI to LangGraph
 ┣ 📜 .env             # Environment variables (API Keys)
 ┗ 📜 README.md