
from models.db import SessionLocal
from models.business_domain import BusinessDomain

class BusinessDomainRepository:
    def __init__(self):
        self.session = SessionLocal()

    def get_all(self):
        query = self.session.query(BusinessDomain)
        return query.all()

    def get_by_id(self, domain_id: int):
        return self.session.query(BusinessDomain).filter(BusinessDomain.id == domain_id).first()

    def get_by_name(self, business_value: str):
        return (
            self.session.query(BusinessDomain)
            .filter(BusinessDomain.business_value.ilike(business_value))
            .first()
        )

    def add_domain(self, business_value, normalized_value=None, synonyms=None, description=None):
        normalized_value = normalized_value or business_value.lower()
        domain = BusinessDomain(
            business_value=business_value,
            normalized_value=normalized_value,
            synonyms=synonyms,
            description=description
        )
        self.session.add(domain)
        self.session.commit()
        return domain

    def update_domain(self, domain_id, **kwargs):
        domain = self.get_by_id(domain_id)
        if not domain:
            return None
        for key, value in kwargs.items():
            if hasattr(domain, key):
                setattr(domain, key, value)
        self.session.commit()
        return domain

    def delete_domain(self, domain_id):
        domain = self.get_by_id(domain_id)
        if domain:
            self.session.delete(domain)
            self.session.commit()
            return True
        return False
