from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    # NOTE: the column is called "password_hash" in the existing
    # verifyai.db and in auth_service.py. The model used to call it
    # "hashed_password", which made registration/login crash.
    password_hash = Column(
        String(255),
        nullable=False
    )

    # Python-side default is needed because the existing users table has
    # "created_at NOT NULL" with no SQL default.
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )
