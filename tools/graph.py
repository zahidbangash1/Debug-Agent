"""
LangGraph Graph — Debugging Agent
Flow: error_analyzer → fix_generator → [teaching_loop?] → concept_explainer → tradeoff_analyst → test_writer
"""

from langgraph.graph import StateGraph, END
from .state import DebugState
from .nodes import (
    error_analyzer,
    fix_generator,
    teaching_loop,
    concept_explainer,
    tradeoff_analyst,
    test_writer
)


def should_use_teaching_loop(state: DebugState) -> str:
    """
    Conditional edge: if confidence < 90 AND loop_count < 3 → teaching_loop
    Otherwise → concept_explainer
    """
    confidence = state.get("confidence_score", 0)
    loop_count = state.get("loop_count", 0)

    if confidence < 90 and loop_count < 3:
        return "teaching_loop"
    return "concept_explainer"


def build_graph():
    graph = StateGraph(DebugState)

    # Add all nodes
    graph.add_node("error_analyzer", error_analyzer)
    graph.add_node("fix_generator", fix_generator)
    graph.add_node("teaching_loop", teaching_loop)
    graph.add_node("concept_explainer", concept_explainer)
    graph.add_node("tradeoff_analyst", tradeoff_analyst)
    graph.add_node("test_writer", test_writer)

    # Entry point
    graph.set_entry_point("error_analyzer")

    # Linear: analyzer → fix generator
    graph.add_edge("error_analyzer", "fix_generator")

    # Conditional: fix_generator → teaching_loop OR concept_explainer
    graph.add_conditional_edges(
        "fix_generator",
        should_use_teaching_loop,
        {
            "teaching_loop": "teaching_loop",
            "concept_explainer": "concept_explainer"
        }
    )

    # Teaching loop feeds back to same conditional check
    graph.add_conditional_edges(
        "teaching_loop",
        should_use_teaching_loop,
        {
            "teaching_loop": "teaching_loop",   # retry if still < 90
            "concept_explainer": "concept_explainer"
        }
    )

    # Linear: explainer → tradeoff → test → END
    graph.add_edge("concept_explainer", "tradeoff_analyst")
    graph.add_edge("tradeoff_analyst", "test_writer")
    graph.add_edge("test_writer", END)

    return graph.compile()


def run_debug_agent(broken_code: str, error_message: str) -> DebugState:
    """Main entry point called from backend.py"""
    graph = build_graph()

    initial_state: DebugState = {
        "broken_code": broken_code,
        "error_message": error_message,
        "language": "",
        "error_type": "",
        "root_cause": "",
        "concept_explanation": "",
        "fix_a": "",
        "fix_b": "",
        "confidence_score": 0,
        "minimal_repro": "",
        "loop_count": 0,
        "teaching_loop_used": False,
        "plain_explanation": "",
        "senior_tip": "",
        "fix_a_pros": "",
        "fix_a_cons": "",
        "fix_b_pros": "",
        "fix_b_cons": "",
        "recommended_fix": "A",
        "regression_test": "",
        "docstring": "",
        "errors": []
    }

    return graph.invoke(initial_state)
