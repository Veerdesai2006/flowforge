"""
=========================================================
FlowForge - Ingestion Service
=========================================================

WHY THIS FILE EXISTS
--------------------
"Ingestion" is the process of taking data (like a Task) and 
feeding it into our AI system (creating an embedding and saving it).

We need an automatic way to keep our Vector Database in sync with our
regular PostgreSQL Database.
- When a task is created -> we create an embedding.
- When a task is updated -> we update its embedding (because the text changed).
- When a task is deleted -> we delete its embedding.

This file acts as the "bridge" between our standard Task logic
and our AI Embedding logic.
"""

# =====================================================
# Imports
# =====================================================

# 'Session' lets us talk to the database.
from sqlalchemy.orm import Session

# We need the Task model because we are reading task data.
from app.models.task import Task

# We need our TaskEmbeddingRepository to save the numbers to the database.
from app.repositories.task_embedding import TaskEmbeddingRepository

# We need our AI tools to actually generate the numbers (the vector).
from app.services.embedding import generate_embedding, build_task_text

# 'logger' lets us print colorful success/error messages to the terminal.
from loguru import logger

# 'select' lets us write a database query to find all tasks.
from sqlalchemy import select


# =====================================================
# IngestionService Class
# =====================================================

class IngestionService:
    
    # '__init__' runs when we create the IngestionService.
    # It requires an active database connection ('db').
    def __init__(self, db: Session):
        # We save the database connection so other methods can use it.
        self.db = db
        # We also create a TaskEmbeddingRepository so we can save embeddings later.
        self.repo = TaskEmbeddingRepository(db)


    # -------------------------------------------------
    # Index (Ingest) One Task
    # -------------------------------------------------
    
    # We define a method called 'index_task'. It takes one 'Task' object.
    def index_task(self, task: Task) -> None:
        """
        This method converts a single task into numbers and saves it.
        It does NOT crash if the AI fails. We wrap it in a 'try/except'.
        """
        
        # 'try' means: "Attempt to run this code, but don't crash if it fails."
        # We use try/except because the Gemini API might be down, or we might 
        # hit a rate limit (too many requests). If that happens, the user should 
        # still be able to create a task normally!
        try:
            # Step 1: Combine the task's title, description, status, etc., into one long string.
            text_to_embed = build_task_text(task)
            
            # Step 2: Send that text to Google Gemini and get 768 numbers back.
            embedding_vector = generate_embedding(text_to_embed)
            
            # If Google Gemini returned actual numbers...
            if embedding_vector:
                # Step 3: Save those numbers in our PostgreSQL database using our repository.
                self.repo.upsert_embedding(
                    task_id=task.id,
                    chunk_text=text_to_embed,
                    embedding_vector=embedding_vector
                )
                # Print a success message in the terminal.
                logger.info(f"✅ Indexed task {task.id} for AI search.")
            else:
                # If Gemini returned None, we log a warning.
                logger.warning(f"⚠️ Failed to generate embedding for task {task.id}.")
                
        # If any Python error happens in the try block, we catch it here.
        except Exception as e:
            # We log the exact error message in red.
            logger.error(f"❌ Error indexing task {task.id}: {e}")


    # -------------------------------------------------
    # Remove Task Embedding
    # -------------------------------------------------
    
    # We define a method to remove an embedding when a task is deleted.
    def remove_task(self, task_id: int) -> None:
        """Removes the AI embedding for a deleted task."""
        try:
            # We use our repository to delete it from the database.
            self.repo.delete_by_task_id(task_id)
            logger.info(f"🗑️ Removed embedding for task {task_id}.")
        except Exception as e:
            logger.error(f"❌ Error removing embedding for task {task_id}: {e}")


    # -------------------------------------------------
    # Bulk Index (One-Time Setup)
    # -------------------------------------------------
    
    # We define a method to index ALL tasks in the database at once.
    # We need this because we already have tasks in our database BEFORE we added AI!
    # Returning an integer ('-> int') tells us how many tasks were successfully indexed.
    def bulk_index_all_tasks(self) -> int:
        """
        Finds all tasks in the database and creates an embedding for each one.
        This might take a while if you have thousands of tasks!
        """
        logger.info("Starting bulk index of all tasks...")
        
        # Write a query to select EVERY task from the database.
        stmt = select(Task)
        
        # Execute the query and get all tasks as a list.
        all_tasks = self.db.execute(stmt).scalars().all()
        
        # We start a counter at zero to keep track of how many we process.
        count = 0
        
        # 'for task in all_tasks:' means "Loop through the list, one task at a time."
        for task in all_tasks:
            # For each task, call our 'index_task' method to embed it.
            self.index_task(task)
            
            # Increase the counter by 1.
            count += 1
            
        logger.info(f"🎉 Bulk index complete. Processed {count} tasks.")
        
        # Return the final count.
        return count
