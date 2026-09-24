"""
=========================================================
FlowForge - Task Embedding Model
=========================================================

WHY THIS FILE EXISTS
--------------------
This file defines the "Blueprint" (Model) for a new database table.
It stores the AI embeddings (vectors) for each task.

WHAT IS A VECTOR / EMBEDDING?
-----------------------------
When we convert a task's text (title + description) into 768 numbers 
using Google Gemini, those numbers are called an "embedding" or "vector".

We need to STORE these vectors in our database so we can SEARCH them 
later when a user asks the AI chatbot a question.

WHAT IS pgvector?
-----------------
pgvector is a special plugin (extension) for PostgreSQL.
Without it, the database only understands normal things like text, numbers, and dates.
With pgvector, the database learns how to store and search through lists of 768 numbers.
"""

# =====================================================
# Imports
# =====================================================

# 'from ... import ...' tells Python to grab specific tools from other libraries.
# 'sqlalchemy' is a library that helps Python talk to databases.
# 'String' is for short text (like names).
# 'Text' is for long text (like descriptions).
# 'ForeignKey' is a database rule that links a row in one table to a row in another table.
from sqlalchemy import String, Text, ForeignKey

# 'Mapped' and 'mapped_column' are special tools from SQLAlchemy.
# They help us define exactly what each column in our database table looks like.
# 'relationship' helps us create a convenient link between Python objects (like Task and TaskEmbedding).
from sqlalchemy.orm import Mapped, mapped_column, relationship

# We import 'BaseModel' from our own app.db.base file.
# BaseModel automatically gives every table an 'id' column, and 'created_at'/'updated_at' timestamps.
from app.db.base import BaseModel

# We import 'Vector' from the pgvector library.
# This tells SQLAlchemy that we are going to use a special type of column that holds lists of numbers.
from pgvector.sqlalchemy import Vector


# =====================================================
# TaskEmbedding Model
# =====================================================

# 'class' is a Python keyword used to create a blueprint for an object.
# 'TaskEmbedding' is the name of our blueprint.
# '(BaseModel)' means our blueprint inherits all the features from BaseModel (like id and timestamps).
class TaskEmbedding(BaseModel):
    """
    This blueprint tells the database to create a table to store vectors.
    """

    # -------------------------------------------------
    # Table Name
    # -------------------------------------------------

    # '__tablename__' is a special variable that SQLAlchemy looks for.
    # It tells SQLAlchemy exactly what to name the table in the PostgreSQL database.
    __tablename__ = "task_embeddings"


    # -------------------------------------------------
    # task_id — Which task does this embedding belong to?
    # -------------------------------------------------

    # We are creating a column named 'task_id'.
    # 'Mapped[int]' is a type hint telling Python this column will hold an integer (whole number).
    # 'mapped_column()' is a function that configures the rules for this database column.
    task_id: Mapped[int] = mapped_column(
        
        # 'ForeignKey' tells the database: "The number in this column MUST match an 'id' in the 'tasks' table."
        # 'ondelete="CASCADE"' is a very important rule. It means:
        # "If the original Task is deleted, CASCADE (fall down) and delete this embedding too."
        # We don't want useless embeddings left behind in the database taking up space.
        ForeignKey("tasks.id", ondelete="CASCADE"),
        
        # 'unique=True' means no two rows in this table can have the same task_id.
        # This guarantees a strict ONE-to-ONE relationship (One Task = Exactly One Embedding).
        unique=True,
        
        # 'nullable=False' means this column CANNOT be empty. 
        # An embedding without a task makes no sense.
        nullable=False,
    )


    # -------------------------------------------------
    # chunk_text — The original text that was embedded
    # -------------------------------------------------

    # 'Mapped[str]' tells Python this column holds a string (text).
    chunk_text: Mapped[str] = mapped_column(
        # We use 'Text' because the combined task text might be very long.
        Text,
        nullable=False,
    )


    # -------------------------------------------------
    # embedding — The 3072-number vector
    # -------------------------------------------------

    # 'Mapped[list]' tells Python this column will hold a list of items.
    embedding: Mapped[list] = mapped_column(
        # 'Vector(3072)' is the special pgvector data type.
        # It tells the database to expect EXACTLY 3072 numbers.
        Vector(3072),
        nullable=False,
    )


    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------

    # This creates a "virtual" link in Python (it doesn't create a column in the database).
    # It allows us to easily access the task details if we have an embedding.
    # For example, if we have a variable 'my_emb', we can type 'my_emb.task.title' to get the task's title.
    task: Mapped["Task"] = relationship(
        # We tell it to link to the "Task" model.
        "Task",
    )
