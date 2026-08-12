from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Workflow.graph import run_debug_agent  # ✅ correct import

router = APIRouter()

# ─── Models ─────────────────────────────────────────

class DebugRequest(BaseModel):
    broken_code: str
    error_message: str


class FixDetail(BaseModel):
    code: str
    pros: str
    cons: str


class DebugResponse(BaseModel):
    success: bool

    language: str
    error_type: str
    root_cause: str
    plain_explanation: str
    senior_tip: str

    fix_a: FixDetail
    fix_b: FixDetail
    recommended_fix: str
    teaching_loop_used: bool
    confidence_score: int

    regression_test: str
    docstring: str

    agent_errors: list


# ─── Route ─────────────────────────────────────────

@router.post("/api/debug", response_model=DebugResponse)
async def debug_code(request: DebugRequest):

    if not request.broken_code.strip():
        raise HTTPException(status_code=400, detail="broken_code cannot be empty")

    if not request.error_message.strip():
        raise HTTPException(status_code=400, detail="error_message cannot be empty")

    try:
        result = run_debug_agent(
            broken_code=request.broken_code,
            error_message=request.error_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")

    return DebugResponse(
        success=True,
        language=result.get("language", "unknown"),
        error_type=result.get("error_type", ""),
        root_cause=result.get("root_cause", ""),
        plain_explanation=result.get("plain_explanation", ""),
        senior_tip=result.get("senior_tip", ""),

        fix_a=FixDetail(
            code=result.get("fix_a", ""),
            pros=result.get("fix_a_pros", ""),
            cons=result.get("fix_a_cons", "")
        ),
        fix_b=FixDetail(
            code=result.get("fix_b", ""),
            pros=result.get("fix_b_pros", ""),
            cons=result.get("fix_b_cons", "")
        ),

        recommended_fix=result.get("recommended_fix", "A"),
        teaching_loop_used=result.get("teaching_loop_used", False),
        confidence_score=result.get("confidence_score", 0),

        regression_test=result.get("regression_test", ""),
        docstring=result.get("docstring", ""),

        agent_errors=result.get("errors", [])
    )


@router.get("/api/health")
async def health():
    return {"status": "ok", "agent": "debugging-agent"}