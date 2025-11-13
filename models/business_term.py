from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Float,
    Boolean,
    Text,
    TIMESTAMP,
    JSON,
    func
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BusinessTerm(Base):
    __tablename__ = "business_glossary"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    term = Column(String(150), nullable=False)
    term_context = Column(JSON, nullable=True)
    term_definition = Column(Text)
    department_owner = Column(String(100))
    business_domain = Column(String(100))
    synonyms = Column(String(1000))
    document_name = Column(String(200))
    source_system = Column(String(100))
    confidence_score = Column(Float, default=None)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=False)
    approved_by = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BusinessTerm(term='{self.term}', context='{self.term_context}', domain='{self.business_domain}')>"
