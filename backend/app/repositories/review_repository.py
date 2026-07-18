"""Human review persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.review import Review


class ReviewRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, review: Review) -> Review:
        self.session.add(review)
        self.session.flush()
        return review

    def list_for_case(self, case_id: str) -> list[Review]:
        statement = (
            select(Review).where(Review.case_id == case_id).order_by(Review.created_at.asc())
        )
        return list(self.session.scalars(statement).all())
