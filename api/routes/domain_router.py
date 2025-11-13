from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.db import SessionLocal
from models.business_domain import BusinessDomain

router = APIRouter(prefix="/business-domain", tags=["Business Domains"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_business_domains(db: Session = Depends(get_db)):
    domains = db.query(BusinessDomain).all()
    return domains
