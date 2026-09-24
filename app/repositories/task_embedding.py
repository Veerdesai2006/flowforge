"""
=========================================================
FlowForge - Task Embedding Repository
=========================================================

WHY THIS FILE EXISTS
--------------------
A "Repository" is a file dedicated completely to talking to the database.
Instead of mixing database queries with our API routes, we put them all here.
This makes our code much cleaner and easier to read.

This specific file handles the CRUD operations (Create, Read, Update, Delete)
for our TaskEmbedding table.

WHAT IS "UPSERT"?
-----------------
"Upsert" is a combination of the words UPdate and inSERT.
It means: "Check if the item exists. If it does, UPDATE it. If it doesn't, INSERT a new one."
"""

# =====================================================
# Imports
# =====================================================

# 'select' is a SQLAlchemy function used to write "SELECT" queries to fetch data from the database.
from sqlalchemy import select

# 'Session' is the active connection to the database. We use it to execute our queries.
from sqlalchemy.orm import Session

# We import the database models we need to interact with.
from app.models.task_embedding import TaskEmbedding
from app.models.task import Task
from app.models.board import Board
from app.models.project import Project


# =====================================================
# TaskEmbeddingRepository Class
# =====================================================

# 'class' creates a blueprint for our repository.
class TaskEmbeddingRepository:
    
    # '__init__' is a special Python method called a "constructor".
    # It runs automatically the moment we create a new TaskEmbeddingRepository object.
    # 'self' refers to the specific object being created.
    # 'db: Session' means this constructor requires a database connection as an input.
    def __init__(self, db: Session):
        # We take the 'db' passed in and store it inside the object as 'self.db'.
        # This allows all the other methods in this class to use the database connection.
        self.db = db

    # -------------------------------------------------
    # Upsert Embedding
    # -------------------------------------------------
    
    # We define a method called 'upsert_embedding'.
    # It takes the task_id, the text, and the list of floats (numbers).
    # '-> TaskEmbedding' tells us it will return the updated or newly created database row.
    def upsert_embedding(self, task_id: int, chunk_text: str, embedding_vector: list[float]) -> TaskEmbedding:
        
        # We write a query to search the TaskEmbedding table for this specific task_id.
        # 'select(TaskEmbedding)' means "SELECT * FROM task_embeddings"
        # '.where(TaskEmbedding.task_id == task_id)' adds the condition to find only this task.
        stmt = select(TaskEmbedding).where(TaskEmbedding.task_id == task_id)
        
        # We execute the query.
        # '.scalar_one_or_none()' tells the database: "Give me the single row if it exists, or give me 'None' if it doesn't."
        existing = self.db.execute(stmt).scalar_one_or_none()

        # 'if existing:' means "If the database found a row..."
        if existing:
            # We UPDATE the existing row with the new text and new vector.
            existing.chunk_text = chunk_text
            existing.embedding = embedding_vector
            
            # '.commit()' actually saves the changes to the database permanently.
            self.db.commit()
            
            # '.refresh()' updates our Python object with any fresh data from the database.
            self.db.refresh(existing)
            
            # We return the updated row.
            return existing
            
        # 'else:' means "Otherwise (if the row didn't exist)..."
        else:
            # We create a brand new TaskEmbedding object in Python.
            new_embedding = TaskEmbedding(
                task_id=task_id,
                chunk_text=chunk_text,
                embedding=embedding_vector
            )
            
            # We use '.add()' to queue it up for insertion into the database.
            self.db.add(new_embedding)
            
            # We save it permanently.
            self.db.commit()
            self.db.refresh(new_embedding)
            
            # We return the newly created row.
            return new_embedding

    # -------------------------------------------------
    # Get by Task ID
    # -------------------------------------------------
    
    def get_by_task_id(self, task_id: int) -> TaskEmbedding | None:
        """Find the embedding for a specific task."""
        stmt = select(TaskEmbedding).where(TaskEmbedding.task_id == task_id)
        return self.db.execute(stmt).scalar_one_or_none()

    # -------------------------------------------------
    # Delete by Task ID
    # -------------------------------------------------
    
    def delete_by_task_id(self, task_id: int) -> None:
        """Remove an embedding from the database manually."""
        
        # We reuse our 'get_by_task_id' function to find the embedding.
        embedding = self.get_by_task_id(task_id)
        
        # If it actually exists...
        if embedding:
            # We tell the database to delete it.
            self.db.delete(embedding)
            # And save the deletion permanently.
            self.db.commit()

    # -------------------------------------------------
    # Search Similar (THE MAGIC RAG METHOD ✨)
    # -------------------------------------------------
    
    def search_similar(self, query_vector: list[float], limit: int = 5, project_id: int | None = None) -> list[Task]:
        """
        This is the most important method for the AI.
        It takes the user's question (converted to a vector of numbers) and finds
        the database tasks whose vectors are mathematically closest to it.
        
        WHAT IS COSINE DISTANCE?
        ------------------------
        Imagine two arrows pointing from the center of a circle.
        Cosine distance measures the ANGLE between the arrows.
        If the angle is very small, the arrows are pointing the same way (similar meaning).
        If the angle is wide, they point in different directions (different meaning).
        
        In SQL, pgvector uses a special symbol '<=>' to calculate this distance.
        """
        
        # We start by querying the 'Task' table (so we can return actual task details).
        # '.join(TaskEmbedding)' tells the database to temporarily merge the Task table and the TaskEmbedding table
        # so we can look at the vectors while returning the tasks.
        stmt = select(Task).join(TaskEmbedding)

        # 'is not None' checks if the user provided a specific project ID to filter by.
        # This is for SECURITY. Users shouldn't be able to search tasks in projects they don't own!
        if project_id is not None:
            # To link a Task to a Project, we have to go through the Board table.
            # (Task belongs to Board, Board belongs to Project).
            # So we '.join(Board)' and then filter where the project_id matches.
            stmt = stmt.join(Board).where(Board.project_id == project_id)

        # Now for the actual vector search.
        # '.order_by()' tells the database how to sort the results.
        # 'TaskEmbedding.embedding.cosine_distance(query_vector)' calculates the distance between 
        # the task's vector and the question's vector.
        # It automatically sorts them from smallest distance (most similar) to largest distance (least similar).
        # '.limit(limit)' tells the database to only give us the top few results (default is 5).
        stmt = stmt.order_by(
            TaskEmbedding.embedding.cosine_distance(query_vector)
        ).limit(limit)

        # We execute the query.
        # '.scalars().all()' tells the database to return all the matching rows as a Python list.
        results = self.db.execute(stmt).scalars().all()
        
        # We return the list of tasks.
        return list(results)
