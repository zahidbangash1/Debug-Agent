"""
5 Agent Nodes for the Debugging Agent
Each function takes state, calls Groq LLM, returns partial state update.
"""

import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from .state import DebugState

from dotenv import load_dotenv
load_dotenv()


def get_llm(temperature: float = 0.2):
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        max_tokens=2048
    )


def clean_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    try:
        raw = raw.strip()
        # Extract pure JSON block
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end+1]
        else:
            raw = re.sub(r"```json|```", "", raw).strip()
            
        # Parse allowing unescaped control characters (like newlines)
        return json.loads(raw, strict=False)
    except Exception as e:
        print(f"\n🔴 JSON Parse Error: {e}\n--- RAW STRING ---\n{raw}\n------------------")
        raise e


# ─── Agent 1: Error Analyzer ─────────────────────────────────────────────────

def error_analyzer(state: DebugState) -> dict:
    llm = get_llm()

    system = """You are a senior software engineer doing code review.
Analyze the broken code and error. Respond ONLY with valid JSON, no markdown.
{
  "language": "python|javascript|typescript|java|other",
  "error_type": "e.g. TypeError, KeyError, NullPointerException",
  "root_cause": "1-2 sentences: the actual bug, not just the error message",
  "concept_explanation": "the underlying CS/language concept the developer misunderstood"
}"""

    try:
        res = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Code:\n```\n{state['broken_code']}\n```\n\nError:\n{state['error_message']}")
        ])
        data = clean_json(res.content)
        return {
            "language": data.get("language", "python"),
            "error_type": data.get("error_type", "Unknown"),
            "root_cause": data.get("root_cause", ""),
            "concept_explanation": data.get("concept_explanation", "")
        }
    except Exception as e:
        return {"errors": [f"Error Analyzer failed: {e}"], "error_type": "Unknown", "root_cause": "", "concept_explanation": "", "language": "python"}


# ─── Agent 2: Fix Generator ───────────────────────────────────────────────────

def fix_generator(state: DebugState) -> dict:
    llm = get_llm(temperature=0.3)

    system = """You are an expert debugger. Generate TWO different fixes for this bug.
The fixes must use fundamentally different approaches (e.g. defensive check vs restructuring logic).
Respond ONLY with valid JSON, no markdown.
{
  "fix_a": "complete corrected code for approach A",
  "fix_b": "complete corrected code for approach B",
  "confidence_score": 0-100
}
confidence_score = how sure you are both fixes are correct. Be honest — if uncertain, score below 90."""

    try:
        res = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Broken code:\n```\n{state['broken_code']}\n```\n\nRoot cause: {state['root_cause']}")
        ])
        data = clean_json(res.content)
        return {
            "fix_a": data.get("fix_a", ""),
            "fix_b": data.get("fix_b", ""),
            "confidence_score": int(data.get("confidence_score", 70))
        }
    except Exception as e:
        return {"errors": [f"Fix Generator failed: {e}"], "fix_a": "", "fix_b": "", "confidence_score": 0}


# ─── Teaching Loop: Minimal Repro Builder ─────────────────────────────────────

def teaching_loop(state: DebugState) -> dict:
    """Called when confidence < 90. Builds minimal repro and re-checks the fix."""
    llm = get_llm(temperature=0.1)

    system = """You are debugging a tricky bug. Build the SMALLEST possible code example
that reproduces this error, then verify if the proposed fix actually solves it.
Respond ONLY with valid JSON, no markdown.
{
  "minimal_repro": "smallest code that reproduces the bug",
  "fix_verified": true|false,
  "fix_a": "corrected fix_a after verification (may be same or improved)",
  "fix_b": "corrected fix_b after verification (may be same or improved)",
  "confidence_score": 0-100
}"""

    loop_count = state.get("loop_count", 0) + 1

    try:
        res = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"""
Original broken code:
```
{state['broken_code']}
```
Error: {state['error_message']}
Root cause: {state['root_cause']}
Current fix_a:
```
{state.get('fix_a', '')}
```
Current fix_b:
```
{state.get('fix_b', '')}
```
""")
        ])
        data = clean_json(res.content)
        return {
            "minimal_repro": data.get("minimal_repro", ""),
            "fix_a": data.get("fix_a", state.get("fix_a", "")),
            "fix_b": data.get("fix_b", state.get("fix_b", "")),
            "confidence_score": int(data.get("confidence_score", 75)),
            "loop_count": loop_count,
            "teaching_loop_used": True
        }
    except Exception as e:
        return {
            "errors": [f"Teaching Loop failed: {e}"],
            "loop_count": loop_count,
            "teaching_loop_used": True,
            "confidence_score": 90  # force exit loop on error
        }


# ─── Agent 3: Concept Explainer ───────────────────────────────────────────────

def concept_explainer(state: DebugState) -> dict:
    llm = get_llm()

    system = """You are a senior developer mentoring a junior dev.
Explain why this bug happened in plain, friendly language.
No jargon. Write like you are explaining to someone who has been coding for 6 months.
Respond ONLY with valid JSON, no markdown.
{
  "plain_explanation": "2-3 sentences: why it broke, what was the mental model mistake",
  "senior_tip": "the 1 thing a senior dev would tell them to never forget about this"
}"""

    try:
        res = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Error type: {state['error_type']}\nRoot cause: {state['root_cause']}\nConcept: {state['concept_explanation']}")
        ])
        data = clean_json(res.content)
        return {
            "plain_explanation": data.get("plain_explanation", ""),
            "senior_tip": data.get("senior_tip", "")
        }
    except Exception as e:
        return {"errors": [f"Concept Explainer failed: {e}"], "plain_explanation": "", "senior_tip": ""}


# ─── Agent 4: Tradeoff Analyst ────────────────────────────────────────────────

def tradeoff_analyst(state: DebugState) -> dict:
    llm = get_llm()

    system = """You are a code reviewer comparing two different fixes for a bug.
Analyze tradeoffs honestly. Respond ONLY with valid JSON, no markdown.
{
  "fix_a_pros": "comma-separated pros of fix A",
  "fix_a_cons": "comma-separated cons of fix A",
  "fix_b_pros": "comma-separated pros of fix B",
  "fix_b_cons": "comma-separated cons of fix B",
  "recommended_fix": "A or B",
  "recommendation_reason": "1 sentence why"
}"""

    try:
        res = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Fix A:\n```\n{state.get('fix_a','')}\n```\n\nFix B:\n```\n{state.get('fix_b','')}\n```\n\nContext: {state['root_cause']}")
        ])
        data = clean_json(res.content)
        return {
            "fix_a_pros": data.get("fix_a_pros", ""),
            "fix_a_cons": data.get("fix_a_cons", ""),
            "fix_b_pros": data.get("fix_b_pros", ""),
            "fix_b_cons": data.get("fix_b_cons", ""),
            "recommended_fix": data.get("recommended_fix", "A"),
        }
    except Exception as e:
        return {"errors": [f"Tradeoff Analyst failed: {e}"], "fix_a_pros": "", "fix_a_cons": "", "fix_b_pros": "", "fix_b_cons": "", "recommended_fix": "A"}


# ─── Agent 5: Test Writer ─────────────────────────────────────────────────────

def test_writer(state: DebugState) -> dict:
    llm = get_llm(temperature=0.1)

    # 👇 NAYA SYSTEM PROMPT YAHAN AAYEGA
    system = """You are a QA engineer writing regression tests.
Write a pytest test that would have CAUGHT this bug before it reached production.
Also write a docstring to add to the function that clarifies the tricky behavior.
Respond ONLY with valid JSON, no markdown.

CRITICAL INSTRUCTIONS:
- You must escape all double quotes inside the code as \\"
- You must escape all newlines inside the code as \\n
- Do NOT output raw newlines inside the JSON string values.

{
  "regression_test": "complete pytest code...",
  "docstring": "docstring text..."
}"""

    try:
        res = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"""
Original broken code:
```
{state['broken_code']}
```
Bug: {state['root_cause']}
Fixed code (use Fix {state.get('recommended_fix','A')}):
```
{state.get('fix_a','') if state.get('recommended_fix','A') == 'A' else state.get('fix_b','')}
```
""")
        ])
        data = clean_json(res.content)
        return {
            "regression_test": data.get("regression_test", ""),
            "docstring": data.get("docstring", "")
        }
    except Exception as e:
        return {"errors": [f"Test Writer failed: {e}"], "regression_test": "", "docstring": ""}
