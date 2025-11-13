# models/business_domain.py
from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BusinessDomain(Base):
    __tablename__ = "business_domain"

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_value = Column(String(150), nullable=False, unique=True)  # e.g. "Lending"
    normalized_value = Column(String(150), nullable=False)             # e.g. "lending"
    domain = Column(String(150), nullable=True)
    category = Column(String(150), nullable=True)                         
    synonyms = Column(Text, nullable=True)                             # comma-separated list
    description = Column(Text, nullable=True)                          # optional extra detail
    source = Column(String(255), nullable=True)
    confidence_score = Column(Float, default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BusinessDomain(id={self.id}, value='{self.business_value}')>"
