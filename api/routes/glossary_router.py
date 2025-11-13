# api/business_glossary.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.db import SessionLocal
from models.business_term import BusinessTerm

router = APIRouter(prefix="/business-glossary", tags=["Business Glossary"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_business_terms(db: Session = Depends(get_db)):
    terms = db.query(BusinessTerm).filter(BusinessTerm.is_active == False).all()
    return [
        {
            "id": t.id,
            "term": t.term,
            "term_context": t.term_context,
            "business_domain": t.business_domain,
            "term_definition": t.term_definition,
            "synonyms": t.synonyms,
            "confidence_score": t.confidence_score,
        }
        for t in terms
    ]
