import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph_store import index_repo
from app.memory import log_run

router = APIRouter(prefix="/onboard", tags=["onboarding"])

class OnboardRequest(BaseModel):
    repo_path: str
    
@router.post("")
def onboard(req: OnboardRequest):
    if not os.path.isdir(req.repo_path):
        raise HTTPException(status_code=400, detail=f"Path not found: {req.repo_path}")
    stats = index_repo(req.repo_path)
    log_run("onboard", target=req.repo_path, result_count=stats["functions_indexed"])
    return {"repo": req.repo_path, **stats}