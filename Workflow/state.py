from typing import TypedDict, Annotated
import operator

class DebugState(TypedDict):
    # --- Inputs ---
    broken_code: str
    error_message: str
    language: str                  # python, js, etc (auto-detected)

    # --- Agent 1: Error Analyzer ---
    error_type: str                # TypeError, KeyError, etc
    root_cause: str                # actual reason it broke
    concept_explanation: str       # underlying CS concept

    # --- Agent 2: Fix Generator ---
    fix_a: str                     # first fix approach
    fix_b: str                     # second fix approach (different method)
    confidence_score: int          # 0-100 self-assessed

    # --- Teaching Loop ---
    minimal_repro: str             # minimal reproducible example
    loop_count: int                # how many retries happened
    teaching_loop_used: bool       # did we go through the loop?

    # --- Agent 3: Concept Explainer ---
    plain_explanation: str         # why it broke in plain language
    senior_tip: str                # what a senior dev would say

    # --- Agent 4: Tradeoff Analyst ---
    fix_a_pros: str
    fix_a_cons: str
    fix_b_pros: str
    fix_b_cons: str
    recommended_fix: str           # A or B with reason

    # --- Agent 5: Test Writer ---
    regression_test: str           # pytest test code
    docstring: str                 # docstring to add to function

    # --- Meta ---
    errors: Annotated[list, operator.add]
