"""
=========================================================
FlowForge - AI Assistant Service (RAG Engine)
=========================================================

WHY THIS FILE EXISTS
--------------------
This is the BRAIN of the AI chatbot.
It combines all the pieces we've built so far to answer user questions.

WHAT DOES R.A.G. STAND FOR?
---------------------------
RAG stands for Retrieval-Augmented Generation.

Here is the exact flow of what happens when a user asks a question:

1. [R] RETRIEVAL: 
   We take the user's question, convert it to numbers (embedding), and 
   search our database for the most mathematically similar tasks.

2. [A] AUGMENTATION: 
   We take those found tasks and "augment" (add to) a giant prompt. 
   We essentially say to the AI: "Here are some tasks from the user's database. 
   Read them."

3. [G] GENERATION: 
   We send the giant prompt + the user's question to Google Gemini. 
   Gemini reads the tasks and GENERATES a smart, accurate answer.
"""

# =====================================================
# Imports
# =====================================================

# 'Session' lets us talk to our PostgreSQL database.
from sqlalchemy.orm import Session
from sqlalchemy import select

# We need the 'User' model to know WHO is asking the question (for security).
from app.models.user import User
from app.models.board import Board

# We import the tools we built in Phase 2 (generate_embedding) and Phase 3 (Repository).
from app.services.embedding import generate_embedding, gemini_client
from app.repositories.task_embedding import TaskEmbeddingRepository
from app.schemas.ai import AiChatResponse

# 'logger' lets us print success/error messages to the terminal.
from loguru import logger


# =====================================================
# AiAssistantService Class
# =====================================================

class AiAssistantService:
    
    # '__init__' is the constructor that runs when this service is created.
    # It takes the active database connection ('db').
    def __init__(self, db: Session):
        # We save the database connection to 'self.db' so other methods can use it.
        self.db = db
        # We create our repository so we can search the embeddings later.
        self.repo = TaskEmbeddingRepository(db)


    # -------------------------------------------------
    # Helper: Resolve project_id from board_id
    # -------------------------------------------------

    def _get_project_id_for_board(self, board_id: int) -> int | None:
        """
        Given a board_id, look up which project it belongs to.
        Returns the project_id, or None if the board was not found.
        """
        stmt = select(Board).where(Board.id == board_id)
        board = self.db.execute(stmt).scalar_one_or_none()
        if board:
            return board.project_id
        return None


    # -------------------------------------------------
    # The Core RAG Chat Method
    # -------------------------------------------------
    
    # We define the 'chat' method.
    # It takes the 'user_message' (text), the 'user' (the person logged in),
    # and an optional 'board_id' to scope the search to the correct project.
    def chat(self, user_message: str, user: User, board_id: int | None = None) -> AiChatResponse:
        """Executes the full RAG pipeline to answer a user's question."""
        
        logger.info(f"User {user.id} asked AI: '{user_message}' (board_id={board_id})")
        
        # ---------------------------------------------------------
        # STEP 1: EMBED THE QUESTION
        # ---------------------------------------------------------
        # Before we can search our database, we must convert the user's 
        # english question into numbers (a vector).
        
        question_vector = generate_embedding(user_message)
        
        # 'if not question_vector:' means "If generating the numbers failed..."
        if not question_vector:
            # We return a friendly error message to the user.
            # We return an empty list '[]' for the sources since we didn't find any.
            return AiChatResponse(
                response="I'm sorry, I couldn't process your question right now because the AI connection failed.",
                sources=[]
            )


        # ---------------------------------------------------------
        # STEP 2: DETERMINE WHICH PROJECT(S) TO SEARCH
        # ---------------------------------------------------------

        # We collect all project IDs this user has access to (for security).
        project_ids = [p.id for p in user.projects]
        
        # If the user has NO projects, they have NO tasks.
        if len(project_ids) == 0:
            return AiChatResponse(
                response="You don't have any projects or tasks yet! Create a project first.",
                sources=[]
            )

        # If a board_id was provided, resolve it to the specific project.
        # This scopes the search precisely to what the user is currently looking at.
        active_project_id: int | None = None
        if board_id is not None:
            resolved = self._get_project_id_for_board(board_id)
            # Only use the resolved project if the user actually owns it (security check).
            if resolved is not None and resolved in project_ids:
                active_project_id = resolved
                logger.info(f"AI search scoped to project {active_project_id} (via board {board_id}).")
            else:
                logger.warning(
                    f"board_id={board_id} could not be resolved to a user project. "
                    "Falling back to cross-project search."
                )
        else:
            logger.info("No board_id provided — performing cross-project search.")

        # ---------------------------------------------------------
        # STEP 3: [R] RETRIEVE RELEVANT TASKS
        # ---------------------------------------------------------

        if active_project_id is not None:
            # Scoped search: only tasks belonging to this specific project.
            similar_tasks = self.repo.search_similar(
                query_vector=question_vector,
                limit=5,
                project_id=active_project_id
            )
        else:
            # Broad search: search ALL of the user's projects one by one and merge results.
            # We search each project and collect up to 3 results per project, capped at 5 total.
            similar_tasks = []
            for pid in project_ids:
                partial = self.repo.search_similar(
                    query_vector=question_vector,
                    limit=3,
                    project_id=pid
                )
                similar_tasks.extend(partial)
            # Deduplicate by task id and keep only top 5 (already sorted by similarity per project).
            seen_ids = set()
            deduped = []
            for task in similar_tasks:
                if task.id not in seen_ids:
                    seen_ids.add(task.id)
                    deduped.append(task)
            similar_tasks = deduped[:5]

        # If we found absolutely nothing...
        if not similar_tasks:
            return AiChatResponse(
                response=(
                    "I couldn't find any tasks related to your question. "
                    "This can happen if tasks haven't been indexed for AI search yet. "
                    "Try creating a new task (it will be indexed automatically), or ask "
                    "an admin to run a full re-index from the admin panel."
                ),
                sources=[]
            )


        # ---------------------------------------------------------
        # STEP 4: [A] BUILD THE PROMPT (AUGMENTATION)
        # ---------------------------------------------------------
        
        # We need to build a giant string of text that contains all the task information.
        # We start with an empty string.
        context_text = ""
        
        # We create an empty list to keep track of the Task IDs we are using.
        source_task_ids = []

        # We loop through the tasks we found in the database.
        for task in similar_tasks:
            # We add the task ID to our list.
            source_task_ids.append(task.id)
            
            # We add the task's details to our giant string.
            # '\n' is a special character that means "New Line" (like pressing Enter).
            context_text += f"Task ID: {task.id}\n"
            context_text += f"Title: {task.title}\n"
            context_text += f"Description: {task.description or 'No description'}\n"
            context_text += f"Status: {task.status.value if hasattr(task.status, 'value') else task.status}\n"
            context_text += f"Priority: {task.priority.value if hasattr(task.priority, 'value') else task.priority}\n"
            context_text += "-" * 20 + "\n" # Adds a divider line like "--------------------"

        # Now we build the "System Prompt".
        # This tells Gemini WHO it is and HOW it should behave.
        system_prompt = f"""
You are FlowForge AI, a helpful and professional project management assistant.
You answer questions about the user's tasks, boards, and projects.

Here is the task context retrieved from the database:
--------------------------------------------------
{context_text}
--------------------------------------------------

INSTRUCTIONS:
1. Answer the user's question using ONLY the context provided above.
2. If the context does not contain the answer, say "I don't have enough information to answer that." DO NOT guess.
3. Use markdown formatting (like bolding and bullet points) to make your answer easy to read.
4. Mention the Task ID when referring to a specific task.
"""

        # ---------------------------------------------------------
        # STEP 5: [G] CALL GEMINI (GENERATION)
        # ---------------------------------------------------------
        
        # We wrap the API call in a try/except so we don't crash if Google is down.
        try:
            # We use 'gemini-3.5-flash'.
            # WHY? Because the "flash" models are incredibly fast, very cheap, 
            # and smart enough for text generation tasks like this.
            
            # We combine the system prompt and the user's question.
            final_prompt = f"{system_prompt}\n\nUser Question: {user_message}"
            
            # We send the giant prompt to Gemini.
            response = gemini_client.models.generate_content(
                model='gemini-3.5-flash',
                contents=final_prompt,
            )
            
            # We extract the text answer that Gemini generated.
            ai_text_answer = response.text
            
            logger.info("✅ Successfully generated AI response.")
            
            # We return the response and the source task IDs to the frontend!
            return AiChatResponse(
                response=ai_text_answer,
                sources=source_task_ids
            )
            
        except Exception as e:
            # If generating the answer fails, log the error.
            logger.error(f"❌ Gemini Generation Error: {e}")
            return AiChatResponse(
                response="I'm sorry, I encountered an error while trying to think of an answer.",
                sources=[]
            )


