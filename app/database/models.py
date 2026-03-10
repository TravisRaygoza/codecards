from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import JSON
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func


# ── Enums ──────────────────────────────────────────────────────────

class Language(str, Enum):
    c = "c"
    cpp = "cpp"
    python = "python"
    java = "java"
    golang = "golang"
    rust = "rust"
    javascript = "javascript"
    sql = "sql"


class Topic(str, Enum):
    algorithms = "algorithms"
    system_design = "system_design"
    data_structures = "data_structures"
    general = "general"
    backend = "backend"
    frontend = "frontend"
    devops = "devops"
    databases = "databases"


class CardType(str, Enum):
    qa = "qa"
    code = "code"


class Progress(str, Enum):
    completed = "completed"
    in_progress = "in_progress"
    not_started = "not_started"


# ── Core Models ────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True)
    email_verified: bool = Field(default=False)
    username: str = Field(unique=True)
    password_hash: str = Field(exclude=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        )
    )

    decks: list["Deck"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    study_sessions: list["StudySession"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    card_progress: list["CardProgress"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    review_logs: list["ReviewLog"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Deck(SQLModel, table=True):
    __tablename__ = "decks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    title: str = Field(max_length=100, description="No more than 100 characters")
    description: str | None = Field(default=None, description="Optional")
    language: Language | None = Field(default=None)
    topic: Topic
    is_public: bool = Field(default=False)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        )
    )

    user: "User" = Relationship(
        back_populates="decks",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    cards: list["Card"] = Relationship(
        back_populates="deck",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    study_sessions: list["StudySession"] = Relationship(
        back_populates="deck",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    deck_id: UUID = Field(foreign_key="decks.id")
    card_type: CardType
    front: str = Field(max_length=200, description="No more than 200 characters")
    back: str = Field(max_length=2000)
    code_template: str | None = Field(default=None)
    difficulty: int = Field(
        ge=1,
        le=5,
        default=1,
        description="Choose from 1-5, 1 being easy mode, 5 being hardest.",
    )
    ai_generated: bool = Field(default=False)

    deck: "Deck" = Relationship(
        back_populates="cards",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    test_cases: list["TestCase"] = Relationship(
        back_populates="card",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    card_progress: list["CardProgress"] = Relationship(
        back_populates="card",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    review_logs: list["ReviewLog"] = Relationship(
        back_populates="card",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


# ── Supporting Models ──────────────────────────────────────────────

class TestCase(SQLModel, table=True):
    __tablename__ = "test_cases"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    card_id: UUID = Field(foreign_key="cards.id")
    input_data: dict = Field(sa_column=Column(JSON))
    expected_output: dict = Field(sa_column=Column(JSON))
    is_hidden: bool = Field(default=False)
    order: int

    card: "Card" = Relationship(
        back_populates="test_cases",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


# ── Study & Progress ──────────────────────────────────────────────

class StudySession(SQLModel, table=True):
    __tablename__ = "study_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    deck_id: UUID = Field(foreign_key="decks.id")
    started_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        )
    )
    completed_at: datetime | None = Field(default=None)
    timed_mode: bool = Field(default=False)
    total_reviewed: int = Field(default=0)
    total_correct: int = Field(default=0)

    user: "User" = Relationship(
        back_populates="study_sessions",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    deck: "Deck" = Relationship(
        back_populates="study_sessions",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    review_logs: list["ReviewLog"] = Relationship(
        back_populates="study_session",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class CardProgress(SQLModel, table=True):
    """Tracks per-user learning state for each card (SM-2 spaced repetition)"""
    __tablename__ = "card_progress"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    card_id: UUID = Field(foreign_key="cards.id")
    ease_factor: float = Field(default=2.5)
    interval_days: int = Field(default=0)
    repetitions: int = Field(default=0)
    next_review: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        )
    )
    progress: Progress

    user: "User" = Relationship(
        back_populates="card_progress",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    card: "Card" = Relationship(
        back_populates="card_progress",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class ReviewLog(SQLModel, table=True):
    """Append-only history of every card review"""
    __tablename__ = "review_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    card_id: UUID = Field(foreign_key="cards.id")
    session_id: UUID = Field(foreign_key="study_sessions.id")
    rating: int | None = Field(ge=0, le=5, default=None)
    response_time_ms: int | None = Field(default=None)
    code_passed: bool | None = Field(default=None)
    reviewed_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
        )
    )

    user: "User" = Relationship(
        back_populates="review_logs",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    card: "Card" = Relationship(
        back_populates="review_logs",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    study_session: "StudySession" = Relationship(
        back_populates="review_logs",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
