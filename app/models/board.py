from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import BaseModel

class Board(BaseModel):
    __tablename__ = "boards"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Which project does this board belong to?
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", 
        back_populates="boards"
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="board",
        cascade="all, delete-orphan"
    )
