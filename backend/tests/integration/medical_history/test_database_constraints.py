"""Constraints reais do PostgreSQL, além da validação HTTP/Pydantic."""

from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.documents.models import Document
from app.modules.medications.models import DoseIntake, Medication
from app.modules.users.models import User

pytestmark = pytest.mark.integration


def _user(db: Session) -> User:
    user = User(
        email="constraints@example.com",
        password_hash="not-a-login-hash",
        full_name="Fixture",
        role="user",
    )
    db.add(user)
    db.flush()
    return user


def test_document_rejects_missing_user(db: Session) -> None:
    with pytest.raises(IntegrityError, match="foreign key constraint"), db.begin_nested():
        db.add(Document(user_id=uuid4(), type="exam", title="Fixture"))
        db.flush()


def test_document_rejects_missing_dependent(db: Session) -> None:
    user = _user(db)
    with pytest.raises(IntegrityError, match="foreign key constraint"), db.begin_nested():
        db.add(Document(user_id=user.id, dependent_id=uuid4(), type="exam", title="Fixture"))
        db.flush()


def test_medication_rejects_nonpositive_duration(db: Session) -> None:
    user = _user(db)
    with pytest.raises(IntegrityError, match="medication_duration"), db.begin_nested():
        db.add(
            Medication(
                user_id=user.id,
                source="manual",
                name="Fixture",
                start_date=date(2026, 11, 15),
                duration_days=0,
            )
        )
        db.flush()


def test_database_rejects_duplicate_dose(db: Session) -> None:
    user = _user(db)
    medication = Medication(
        user_id=user.id, source="manual", name="Fixture", start_date=date(2026, 11, 15)
    )
    db.add(medication)
    db.flush()
    values = {"medication_id": medication.id, "date": date(2026, 11, 15), "time": "08:00"}
    db.add(DoseIntake(**values))
    db.flush()
    with pytest.raises(IntegrityError, match="uq_dose_intake"), db.begin_nested():
        db.add(DoseIntake(**values))
        db.flush()
