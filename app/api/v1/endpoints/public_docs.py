from fastapi import APIRouter, Response
from pathlib import Path

router = APIRouter()

def _repo_root() -> Path:
    # backend/app/api/v1/endpoints/public_docs.py -> repo root is parents[5]
    return Path(__file__).resolve().parents[5]

def _read_progress() -> str:
    candidates = [
        _repo_root() / "docs" / "PROGRESS.md",
        _repo_root() / "backend" / "docs" / "PROGRESS.md",
        _repo_root() / "backend" / "app" / "docs" / "PROGRESS.md",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8").lstrip("\ufeff")
    return "No progress doc yet."

@router.get("/public/progress", tags=["public"])
def public_progress():
    return Response(content=_read_progress(), media_type="text/plain; charset=utf-8")