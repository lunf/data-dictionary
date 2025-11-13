# api/business_glossary.py
from fastapi import APIRouter
from app.pipeline import run_pipeline
router = APIRouter(prefix="/process", tags=["Process Files"])


@router.get("/")
def do_process_file():
    run_pipeline()
    return
    {
        "status": "OK",
        "message": "File has been processed"
    }
