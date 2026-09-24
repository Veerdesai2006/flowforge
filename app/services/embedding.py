"""
=========================================================
FlowForge - Embedding Service
=========================================================

WHY THIS FILE EXISTS
--------------------
This is the first building block of our AI chatbot.
Before the AI can answer questions about your tasks, it needs
a way to UNDERSTAND the MEANING of text — not just match exact words.

For example, these two sentences mean similar things:
  "Fix the login page crash"
  "Resolve the authentication error on sign-in"

A simple keyword search for "login" would NOT find the second sentence.
But an EMBEDDING search would, because both sentences have similar MEANING.

WHAT IS AN EMBEDDING?
---------------------
An embedding is a list of numbers (called a "vector") that
represents the MEANING of a piece of text.

The Google Gemini AI model named "text-embedding-004" converts any text
into exactly 768 numbers. 

WHAT DO THE 768 NUMBERS REPRESENT?
----------------------------------
Each number captures one tiny, abstract aspect of meaning.
Together, all 768 numbers create a unique "fingerprint" for the text.
Texts with similar meaning have similar fingerprints. We can compare
these numbers mathematically to find the most relevant tasks.
"""

# =====================================================
# Imports
# =====================================================

# 'from' and 'import' are Python keywords used to bring in code
# that someone else wrote, so we don't have to write it from scratch.

# 'google.genai' is the official Google package we installed earlier.
# We import the 'genai' module to talk to Google's AI servers.
from google import genai

# 'loguru' is a library for logging (printing messages to the terminal).
# 'logger' is the specific object we use to print errors or success messages.
from loguru import logger

# We import 'settings' from our own app.config.settings file.
# This allows us to safely access our GEMINI_API_KEY from the .env file.
from app.config.settings import settings


# =====================================================
# Gemini Client Setup
# =====================================================

# 'def' is a Python keyword used to DEFINE a new function.
# '_create_gemini_client' is the name of our function. 
# The underscore '_' at the start means this is a "private" function 
# meant to be used only inside this file.
def _create_gemini_client():
    """
    This function sets up our connection (the "client") to Google Gemini.
    It returns the client if successful, or None if there is no API key.
    """
    
    # 'if' is a conditional statement. It checks if something is True.
    # 'not' means the opposite. 
    # So we are checking: "If there is NO gemini_api_key in settings..."
    # 'or' means "if either the first condition OR the second condition is true".
    # '==' checks if two things are exactly equal.
    if not settings.gemini_api_key or settings.gemini_api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
        
        # If the API key is missing, we use 'logger.warning' to print a yellow 
        # message to the terminal.
        logger.warning(
            "GEMINI_API_KEY is not set in .env — "
            "AI features will be disabled."
        )
        
        # 'return' is a Python keyword that stops the function and sends a value back.
        # 'None' is a special Python value that means "nothing" or "empty".
        return None

    # If we made it past the 'if' statement, it means we have a real API key!
    
    # We call 'genai.Client()' to create the connection.
    # We pass 'api_key=settings.gemini_api_key' as an argument.
    # We store the result in a variable named 'client'.
    # '=' is the assignment operator. It assigns the value on the right to the variable on the left.
    client = genai.Client(api_key=settings.gemini_api_key)

    # We log a green success message to the terminal.
    logger.info("✅ Gemini AI client initialized successfully.")

    # Finally, we return the 'client' object so the rest of the file can use it.
    return client


# We call our function right away and store the result in a variable named 'gemini_client'.
# Because this is outside of any function, it runs as soon as this file is loaded.
# This way, we create the connection only ONCE and reuse it.
gemini_client = _create_gemini_client()


# =====================================================
# Build Task Text
# =====================================================

# We define a function called 'build_task_text'.
# Inside the parentheses (task), we say this function requires one input, which we name 'task'.
# '-> str' is a "type hint". It tells other programmers that this function will RETURN a string (text).
def build_task_text(task) -> str:
    """
    This function takes a database Task object and combines its title, 
    description, status, and priority into a single string of text.

    WHY COMBINE THEM?
    -----------------
    The AI model only understands plain text. It doesn't know what a database row is.
    We need to feed it ALL the important information about a task so it understands
    the full context.
    """
    
    # 'parts' is a variable holding a "list". 
    # A list in Python is created using square brackets []. 
    # It holds multiple items in a specific order.
    # We start our list with one item: the title.
    # The 'f' before the quotes means it's a "formatted string" (f-string).
    # It allows us to insert variables directly inside the string using curly braces {}.
    # 'task.title' accesses the title property of the task object.
    parts = [f"Title: {task.title}"]

    # We check if the task has a description. (Some tasks might have empty descriptions).
    if task.description:
        # If it does, we use '.append()' to add a new item to the END of our 'parts' list.
        parts.append(f"Description: {task.description}")

    # We check if the task has a status.
    if task.status:
        # 'hasattr' is a built-in Python function. It stands for "has attribute".
        # It checks if the object (task.status) has a property named 'value'.
        # Since 'status' is an Enum in our database, we need to get its actual text value.
        # If it has a .value, we use it. If not (else), we convert it to a string using 'str()'.
        status_value = task.status.value if hasattr(task.status, 'value') else str(task.status)
        
        # We append the status string to our list.
        parts.append(f"Status: {status_value}")

    # We check if the task has a priority.
    if task.priority:
        # We do the same check for priority as we did for status.
        priority_value = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
        
        # We append the priority string to our list.
        parts.append(f"Priority: {priority_value}")

    # Now we have a list of strings like: ["Title: Fix bug", "Status: TODO"]
    # We want to combine them into one single string.
    # '" | ".join(parts)' takes the string " | " and glues all the items in the 'parts' list together with it.
    # The result will look like: "Title: Fix bug | Status: TODO"
    return " | ".join(parts)


# =====================================================
# Generate Embedding
# =====================================================

# We define 'generate_embedding'. It takes one input: 'text', which MUST be a string (str).
# It returns either a list of floats (list[float]) OR None ('| None').
# A 'float' is a number with a decimal point (like 3.14 or -0.5).
def generate_embedding(text: str) -> list[float] | None:
    """
    This function takes plain text and asks Google's AI to convert it into 
    768 numbers (the embedding vector).
    """

    # First, we check if our Gemini client was successfully created earlier.
    # 'is None' checks if a variable is completely empty.
    if gemini_client is None:
        # If it is empty, we log a warning and return None.
        logger.warning(
            "Cannot generate embedding — Gemini client is not initialized."
        )
        return None

    # Next, we check if the user actually provided any text.
    # 'not text' checks if the text is empty ("").
    # 'text.strip()' removes spaces from the beginning and end of the text.
    # So 'not text.strip()' checks if the text is just a bunch of blank spaces.
    if not text or not text.strip():
        logger.warning("Cannot generate embedding — text is empty.")
        return None

    # 'try' is the start of an error-handling block.
    # We are telling Python: "Try to run the code inside here, but if it crashes,
    # don't stop the whole program. Catch the error instead."
    try:
        # We call the Gemini API over the internet.
        # 'models.embed_content' is the specific function provided by Google to generate embeddings.
        # 'model="gemini-embedding-2"' tells Google EXACTLY which AI model we want to use.
        # 'contents=text' passes our text to the model.
        # We store Google's answer in a variable called 'response'.
        response = gemini_client.models.embed_content(
            model="gemini-embedding-2",
            contents=text,
        )

        # Google's response contains a lot of extra information.
        # We only want the list of 768 numbers.
        # '.embeddings[0]' gets the first embedding from the response.
        # '.values' gets the actual list of numbers from that embedding.
        embedding_vector = response.embeddings[0].values

        # We log a hidden debug message so developers can see it's working behind the scenes.
        # 'len()' is a built-in function that gets the length (number of items) of a list.
        # 'text[:50]' gets only the first 50 characters of the text, so we don't flood the logs.
        logger.debug(
            f"Generated embedding with {len(embedding_vector)} dimensions "
            f"for text: '{text[:50]}...'"
        )

        # We successfully got our numbers, so we return them!
        return embedding_vector

    # 'except' is the second part of the 'try' block.
    # 'Exception as e' means: "If ANY error happens, catch it and name it 'e'."
    except Exception as e:
        # We log a red error message to the terminal, including the exact error ('e').
        logger.error(
            f"Failed to generate embedding: {e}. "
            f"Text was: '{text[:100]}...'"
        )
        # We return None so our program can gracefully continue instead of crashing.
        return None
