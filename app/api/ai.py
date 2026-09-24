"""
=========================================================
FlowForge - AI Endpoints
=========================================================

WHY THIS FILE EXISTS
--------------------
This file creates the API "Routes" (or Endpoints) for our AI.

WHAT IS AN API ROUTE / ENDPOINT?
--------------------------------
Imagine your backend (FastAPI) is a restaurant kitchen, and the frontend 
(React) is a customer sitting at a table.
An "Endpoint" is like a waiter. It takes the customer's order (the Request), 
carries it to the kitchen, and brings back the food (the Response).

URL example: http://localhost:8000/api/ai/chat

WHAT DOES 'POST' MEAN?
----------------------
In web development, we use different "methods" to talk to the server:
- GET: "Give me some data" (like viewing a webpage).
- POST: "Here is some data, do something with it or save it."
We use POST for the AI chat because the user is SENDING their question 
to the server for processing.
"""

# =====================================================
# Imports
# =====================================================

# 'APIRouter' lets us create a mini-app just for AI URLs.
# 'Depends' is FastAPI's magic tool for "Dependency Injection" (explained below).
from fastapi import APIRouter, Depends

# 'Session' lets us talk to the database.
from sqlalchemy.orm import Session

# We need these to get the database connection and the currently logged-in user.
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_admin

# We import the schemas we created in Phase 5 to validate data.
from app.schemas.ai import AiChatRequest, AiChatResponse

# We import our services.
from app.services.ai_assistant import AiAssistantService
from app.services.ingestion import IngestionService

# We import the User model so we can type-hint the current user.
from app.models.user import User


# =====================================================
# Router Setup
# =====================================================

# We create the router. 
# 'prefix="/api/ai"' means every endpoint below automatically starts with /api/ai.
# 'tags=["AI"]' groups these endpoints together in the automatic Swagger documentation.
router = APIRouter(prefix="/api/ai", tags=["AI"])


# =====================================================
# 1. The Main Chat Endpoint
# =====================================================

# '@router.post' tells FastAPI: "If someone sends a POST request to /chat, run the function below."
# 'response_model=AiChatResponse' tells FastAPI to automatically format the output to match our schema.
@router.post("/chat", response_model=AiChatResponse)
def ai_chat(
    # 'request' is the data the user sent. We force it to match our 'AiChatRequest' schema.
    request: AiChatRequest,
    
    # WHAT IS Depends() ?
    # Depends() tells FastAPI: "Before you run this function, go run get_db() first, 
    # and give me whatever it returns."
    # So 'db' automatically becomes our live database connection!
    db: Session = Depends(get_db),
    
    # We do the same thing here. Before running, FastAPI checks if the user has a valid login token.
    # If they don't, FastAPI stops them immediately with an error. 
    # If they do, 'current_user' becomes the actual user object from the database.
    current_user: User = Depends(get_current_user)
):
    """
    This endpoint handles the AI chat conversation.
    It takes the user's question, asks the AiAssistantService to figure out the answer,
    and returns the text response.
    """
    
    # 1. We create the AiAssistantService (our RAG Engine), giving it the database connection.
    ai_service = AiAssistantService(db)
    
    # 2. We call the '.chat()' method. 
    # We pass it the text the user typed ('request.user_message'), who they are ('current_user'),
    # and the board they are currently viewing ('request.board_id') for context-aware search.
    # This might take a few seconds because it has to talk to Google Gemini over the internet!
    response_data = ai_service.chat(
        user_message=request.user_message, 
        user=current_user,
        board_id=request.board_id,
    )
    
    # 3. We return the result to the frontend.
    # Because of 'response_model=AiChatResponse' at the top, FastAPI guarantees 
    # it sends back clean JSON matching our schema.
    return response_data


# =====================================================
# 2. Bulk Reindex Endpoint (Admin Only)
# =====================================================

@router.post("/reindex")
def trigger_bulk_reindex(
    db: Session = Depends(get_db),
    
    # 'require_admin' works just like 'get_current_user', but it ALSO checks 
    # if the user has admin privileges. If they don't, they are blocked!
    admin_user: User = Depends(require_admin)
):
    """
    This endpoint triggers a full re-index of all tasks in the database.
    It loops through every single task and generates an AI embedding for it.
    """
    
    # 1. We create the IngestionService.
    service = IngestionService(db)
    
    # 2. We call the bulk index function.
    total_indexed = service.bulk_index_all_tasks()
    
    # 3. We return a simple JSON response telling the admin how many tasks were processed.
    return {
        "message": "Bulk re-indexing complete.",
        "tasks_processed": total_indexed
    }
