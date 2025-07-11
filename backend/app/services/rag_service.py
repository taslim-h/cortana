# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# from pinecone import Pinecone, ServerlessSpec
# from langchain.prompts import PromptTemplate
# from app.services.mongodb import get_meetings_collection_async
# from app.services.chat_service import save_chat_message
# import os
# import logging
# from bson import ObjectId
# import asyncio
# from typing import Dict, Any, List, Optional
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Configuration
# class Config:
#     PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
#     PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "cortana-meetings")
#     EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-ada-002")
#     LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
#     TOP_K = int(os.environ.get("RAG_TOP_K", 5))

#     @classmethod
#     def validate(cls):
#         if not cls.PINECONE_API_KEY:
#             raise ValueError("PINECONE_API_KEY is required")
#         if not cls.PINECONE_INDEX_NAME:
#             raise ValueError("PINECONE_INDEX_NAME is required")

# # Initialize services with retry logic
# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
# def initialize_services():
#     try:
#         Config.validate()
#         pc = Pinecone(api_key=Config.PINECONE_API_KEY)
#         index = pc.Index(Config.PINECONE_INDEX_NAME)
#         embeddings = OpenAIEmbeddings(model=Config.EMBEDDING_MODEL)
#         llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.7)
#         return index, embeddings, llm
#     except Exception as e:
#         logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
#         raise

# # Global services (initialized on first use)
# index, embeddings, llm = None, None, None

# async def get_services():
#     """Lazy initialization of services with async context"""
#     global index, embeddings, llm
#     if index is None or embeddings is None or llm is None:
#         index, embeddings, llm = await asyncio.to_thread(initialize_services)
#     return index, embeddings, llm

# # Custom prompt template
# PROMPT_TEMPLATE = """
# You are a helpful assistant. Use the provided context from meeting documents to answer the user's question as accurately and concisely as possible.

# Instructions:
# - Base your answer only on the information in the context below.
# - If the context does not contain enough information to answer, reply: "I don’t know. Please check the meeting documents for more details."
# - If relevant, summarize key points, decisions, or actions from the context.

# Context:
# {context}

# Question:
# {question}

# Answer:
# """
# prompt = PromptTemplate(input_variables=["context", "question"], template=PROMPT_TEMPLATE)

# async def get_rag_response(meeting_id: str, query: str) -> Dict[str, Any]:
#     """Process a RAG query for a specific meeting with production-ready features"""
#     logger.info(f"Processing RAG query for meeting {meeting_id}: {query}")

#     # Validate meeting_id
#     if not ObjectId.is_valid(meeting_id):
#         return {"error": "Invalid meeting ID format", "status": 400}

#     meeting_obj_id = ObjectId(meeting_id)

#     try:
#         # Verify meeting exists and is indexed
#         meetings_collection = get_meetings_collection_async()
#         meeting = await meetings_collection.find_one({"_id": meeting_obj_id})
#         if not meeting:
#             return {"error": "Meeting not found", "status": 404}
#         if meeting.get("indexing_status") != "completed":
#             return {"error": "Meeting not indexed", "status": 400}

#         # Get services
#         index, embeddings, llm = await get_services()

#         # Get query embedding with retry
#         @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
#         async def get_embedding():
#             return await embeddings.aembed_query(query)

#         query_embedding = await get_embedding()

#         # Query Pinecone with meeting_id filter
#         result = index.query(
#             vector=query_embedding,
#             top_k=Config.TOP_K,
#             include_metadata=True,
#             filter={"meeting_id": str(meeting_id)}
#         )

#         # Extract contexts
#         contexts = [match['metadata'].get('text', '') for match in result['matches'] if match.get('metadata', {}).get('text')]
#         if not contexts:
#             return {
#                 "response": {
#                     "full_response": f"No information about '{query}' was found in the meeting documents. Please check the uploaded files.",
#                     "key_points": []
#                 },
#                 "source_documents": [],
#                 "status": 200
#             }

#         # Build and format prompt
#         context_str = "\n---\n".join(contexts)
#         formatted_prompt = prompt.format(context=context_str, question=query)

#         # Get LLM response with retry
#         @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
#         async def get_llm_response():
#             return await llm.ainvoke(formatted_prompt)

#         response = await get_llm_response()

#         # Save and parse results
#         await save_chat_message(meeting_id, query, response.content)
#         parsed_response = parse_llm_response(response.content)

#         return {
#             "response": parsed_response,
#             "source_documents": [{"text": text, "metadata": match['metadata']} for match, text in zip(result['matches'], contexts) if text],
#             "status": 200
#         }

#     except Exception as e:
#         logger.error(f"RAG processing failed for meeting {meeting_id}: {str(e)}", exc_info=True)
#         return {"error": f"RAG processing failed: {str(e)}", "status": 500}

# def parse_llm_response(response: str) -> Dict[str, Any]:
#     """Parse LLM response into structured format with keyword filtering"""
#     key_points = []
#     for line in response.split("\n"):
#         line = line.strip()
#         if line and any(keyword in line.lower() for keyword in ["name", "project", "deadline", "family", "role"]):
#             key_points.append(line)
#     return {
#         "full_response": response,
#         "key_points": key_points if key_points else ["No key points identified"]
#     }

# # Example usage (for testing)
# if __name__ == "__main__":
#     async def test_rag():
#         result = await get_rag_response("686fdac0eee535ae470975e9", "tell me about taslim")
#         print(result)

#     asyncio.run(test_rag())

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone, ServerlessSpec
from langchain.prompts import PromptTemplate
from app.services.mongodb import get_meetings_collection_async, get_chats_collection_async
from app.services.chat_service import save_chat_message
import os
import logging
from bson import ObjectId
import asyncio
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "cortana-meetings")
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    TOP_K = int(os.environ.get("RAG_TOP_K", 5))
    MAX_HISTORY_LENGTH = int(os.environ.get("MAX_HISTORY_LENGTH", 10))  # Max number of past messages

    @classmethod
    def validate(cls):
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required")
        if not cls.PINECONE_INDEX_NAME:
            raise ValueError("PINECONE_INDEX_NAME is required")

# Initialize services with retry logic
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
def initialize_services():
    try:
        Config.validate()
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        index = pc.Index(Config.PINECONE_INDEX_NAME)
        embeddings = OpenAIEmbeddings(model=Config.EMBEDDING_MODEL)
        llm = ChatOpenAI(model=Config.LLM_MODEL, temperature=0.7)
        return index, embeddings, llm
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
        raise

# Global services (initialized on first use)
index, embeddings, llm = None, None, None

async def get_services():
    """Lazy initialization of services with async context"""
    global index, embeddings, llm
    if index is None or embeddings is None or llm is None:
        index, embeddings, llm = await asyncio.to_thread(initialize_services)
    return index, embeddings, llm

# Custom prompt template with history
PROMPT_TEMPLATE = """
You are a helpful assistant. Use the provided context from meeting documents and the chat history to answer the user's question as accurately and concisely as possible.

Instructions:
- Base your answer only on the information in the context and history below.
- Give extra caution to history, as it may contain user queries and AI responses that are relevant to the current question.
- If the context or history does not contain enough information to answer, reply: "I don’t know. Please check the meeting documents for more details."
- If relevant, summarize key points, decisions, or actions from the context.


Chat History:
{history}

Context:
{context}

Question:
{question}

Answer:
"""
prompt = PromptTemplate(input_variables=["history", "context", "question"], template=PROMPT_TEMPLATE)

async def get_chat_history(meeting_id: str) -> List[Dict[str, Any]]:
    """Fetch and limit chat history for a meeting from the chats collection"""
    try:
        chats_collection = get_chats_collection_async()
        history = await chats_collection.find({"meeting_id": meeting_id}).sort("timestamp", -1).limit(Config.MAX_HISTORY_LENGTH).to_list(length=Config.MAX_HISTORY_LENGTH)
        return [{"user_query": entry["user_message"], "response": entry["ai_response"], "timestamp": entry["timestamp"]} for entry in history]
    except Exception as e:
        logger.error(f"Failed to fetch chat history for meeting {meeting_id}: {str(e)}", exc_info=True)
        return []

async def get_rag_response(meeting_id: str, query: str) -> Dict[str, Any]:
    """Process a RAG query for a specific meeting with chat history"""
    logger.info(f"Processing RAG query for meeting {meeting_id}: {query}")

    # Validate meeting_id
    if not ObjectId.is_valid(meeting_id):
        return {"error": "Invalid meeting ID format", "status": 400}

    meeting_obj_id = ObjectId(meeting_id)

    try:
        # Verify meeting exists and is indexed
        meetings_collection = get_meetings_collection_async()
        meeting = await meetings_collection.find_one({"_id": meeting_obj_id})
        if not meeting:
            return {"error": "Meeting not found", "status": 404}
        if meeting.get("indexing_status") != "completed":
            return {"error": "Meeting not indexed", "status": 400}

        # Get services
        index, embeddings, llm = await get_services()

        # Get query embedding with retry
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
        async def get_embedding():
            return await embeddings.aembed_query(query)

        query_embedding = await get_embedding()

        # Query Pinecone with meeting_id filter
        result = index.query(
            vector=query_embedding,
            top_k=Config.TOP_K,
            include_metadata=True,
            filter={"meeting_id": str(meeting_id)}
        )

        # Extract contexts
        contexts = [match['metadata'].get('text', '') for match in result['matches'] if match.get('metadata', {}).get('text')]
        if not contexts:
            return {
                "response": {
                    "full_response": f"No information about '{query}' was found in the meeting documents. Please check the uploaded files.",
                    "key_points": []
                },
                "source_documents": [],
                "chat_history": await get_chat_history(meeting_id),
                "status": 200
            }

        # Get chat history
        history = await get_chat_history(meeting_id)
        history_str = "\n".join([f"User: {entry['user_query']}\nAssistant: {entry['response']}" for entry in history]) if history else "No previous chat history."

        # Build and format prompt
        context_str = "\n---\n".join(contexts)
        formatted_prompt = prompt.format(history=history_str, context=context_str, question=query)

        # Get LLM response with retry
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(Exception))
        async def get_llm_response():
            return await llm.ainvoke(formatted_prompt)

        response = await get_llm_response()

        # Save and parse results
        await save_chat_message(meeting_id, query, response.content)
        parsed_response = parse_llm_response(response.content)

        return {
            "response": parsed_response,
            "source_documents": [{"text": text, "metadata": match['metadata']} for match, text in zip(result['matches'], contexts) if text],
            "chat_history": await get_chat_history(meeting_id),
            "status": 200
        }

    except Exception as e:
        logger.error(f"RAG processing failed for meeting {meeting_id}: {str(e)}", exc_info=True)
        return {"error": f"RAG processing failed: {str(e)}", "status": 500}

def parse_llm_response(response: str) -> Dict[str, Any]:
    """Parse LLM response into structured format with keyword filtering"""
    key_points = []
    for line in response.split("\n"):
        line = line.strip()
        if line and any(keyword in line.lower() for keyword in ["name", "project", "deadline", "family", "role"]):
            key_points.append(line)
    return {
        "full_response": response,
        "key_points": key_points if key_points else ["No key points identified"]
    }

# Example usage (for testing)
if __name__ == "__main__":
    async def test_rag():
        result = await get_rag_response("686fdac0eee535ae470975e9", "tell me about taslim")
        print(result)

    asyncio.run(test_rag())