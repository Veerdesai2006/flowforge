"""
=========================================================
FlowForge - AI Chatbot Testing Script
=========================================================

WHY THIS FILE EXISTS
--------------------
This script helps us test every single part of our AI Chatbot
step-by-step. It ensures the Gemini API works, the database works,
and the pgvector search works!

HOW TO RUN THIS SCRIPT:
-----------------------
1. Open your terminal.
2. Make sure you are in the FlowForge folder.
3. Run this exact command:
   uv run python tests/test_ai_chatbot.py
"""

import sys
import os

# This tells Python to look in the parent folder for our 'app' code.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from app.config.settings import settings
from app.db.database import SessionLocal
from app.services.embedding import gemini_client, generate_embedding
from app.repositories.task_embedding import TaskEmbeddingRepository

def run_tests():
    logger.info("🚀 STARTING AI CHATBOT TESTS...")
    
    # ---------------------------------------------------------
    # TEST 1: Check Gemini API Key
    # ---------------------------------------------------------
    logger.info("\n--- TEST 1: Gemini API Key ---")
    if not settings.gemini_api_key or settings.gemini_api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
        logger.error("❌ ERROR: Your GEMINI_API_KEY is missing or invalid in the .env file!")
        logger.info("👉 FIX: Open .env and paste your real key.")
        return
    else:
        logger.success("✅ Gemini API Key is present.")


    # ---------------------------------------------------------
    # TEST 2: Test the Embedding Service
    # ---------------------------------------------------------
    logger.info("\n--- TEST 2: Embedding Service (text-embedding-004) ---")
    test_text = "This is a test task to see if embeddings work."
    
    logger.info(f"Sending text to Gemini: '{test_text}'")
    vector = generate_embedding(test_text)
    
    if not vector:
        logger.error("❌ ERROR: Failed to generate an embedding.")
        logger.info("👉 FIX: Check your internet connection or verify your API key is correct.")
        return
        
    logger.success(f"✅ Success! Received a vector with {len(vector)} numbers.")
    # Show the first 3 numbers just to prove it worked
    logger.info(f"First 3 numbers of the vector: {vector[:3]}")


    # ---------------------------------------------------------
    # TEST 3: Test pgvector Database Connection
    # ---------------------------------------------------------
    logger.info("\n--- TEST 3: pgvector Database ---")
    
    # Open a temporary database session
    db = SessionLocal()
    try:
        # Create a repository instance
        repo = TaskEmbeddingRepository(db)
        
        # Test a simple cosine distance query using our vector
        # limit=1 means just bring back the single closest task
        # We wrap this in try/except because if pgvector is missing, this will crash!
        results = repo.search_similar(query_vector=vector, limit=1)
        
        logger.success("✅ pgvector search executed successfully!")
        if len(results) > 0:
            logger.info(f"Found {len(results)} matching task(s) in the database.")
        else:
            logger.info("Search worked, but the database is currently empty (no tasks found).")
            
    except Exception as e:
        logger.error(f"❌ ERROR: pgvector search failed. Error: {e}")
        logger.info("👉 FIX: Make sure PostgreSQL is running and you ran 'uv run alembic upgrade head'.")
    finally:
        # Always close the database connection when done
        db.close()

    logger.info("\n🎉 ALL TESTS COMPLETED! If you saw green checkmarks, your AI backend is 100% working.")


# This tells Python to run the function when we execute the file.
if __name__ == "__main__":
    run_tests()
