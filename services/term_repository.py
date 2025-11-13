from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from models.db import SessionLocal
from models.business_term import BusinessTerm

class BusinessTermRepository:
    def __init__(self):
        self.session = SessionLocal()

    def term_exists(self, term: str) -> bool:
        """Check if term already exists in DB."""
        q = select(BusinessTerm).where(BusinessTerm.term == term)
        return self.session.execute(q).scalar_one_or_none() is not None

    def save_new_terms(self, enriched_terms: list):
        """Save only new terms to DB."""
        saved_count = 0
        for t in enriched_terms:
            if not t.get("term_definition") or self.term_exists(t["term"]):
                continue  # skip existing or invalid entries

            try:
                new_term = BusinessTerm(
                    term=t["term"],
                    term_context=t.get("term_context"),
                    term_definition=t.get("term_definition"),
                    business_domain=t.get("business_domain"),
                    synonyms=", ".join(t.get("synonyms", [])),
                    confidence_score=t.get("confidence_score", None),
                    department_owner=t.get("department_owner"),
                    document_name=t.get("document_name"),
                    source_system=t.get("source_system"),
                    is_active=False
                )
                self.session.add(new_term)
                saved_count += 1
            except SQLAlchemyError as e:
                print(f"Error adding term '{t['term']}': {e}")
                self.session.rollback()

        try:
            self.session.commit()
            print(f"Saved {saved_count} new terms.")
        except SQLAlchemyError as e:
            print(f"Commit error: {e}")
            self.session.rollback()

    def upsert_term(self, term_data: dict):
        """
        Insert or update a business term based on (term, term_context).
        """
        try:
            existing = self.session.execute(
                select(BusinessTerm).where(
                    BusinessTerm.term == term_data["term"],
                    BusinessTerm.term_context == term_data.get("term_context")
                )
            ).scalars().first()

            if existing:
                # Update existing fields if new info is available
                for key, value in term_data.items():
                    if value is not None and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.version += 1
                print(f"Updated existing term: {existing.term}")
            else:
                # Insert new term
                new_term = BusinessTerm(**term_data)
                self.session.add(new_term)
                print(f"Inserted new term: {term_data['term']}")

            self.session.commit()

        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Database error: {e}")

    def get_all_terms(self):
        """Retrieve all active terms."""
        return self.session.query(BusinessTerm).filter_by(is_active=True).all()

    def get_terms_by_domain(self, domain):
        """Retrieve terms filtered by business domain."""
        return self.session.query(BusinessTerm).filter_by(business_domain=domain).all()

    def get_all_term_names(self):
        """Return a flat list of all terms in the database."""
        result = self.session.query(BusinessTerm.term).all()
        return [r[0] for r in result]

    def close(self):
        self.session.close()
