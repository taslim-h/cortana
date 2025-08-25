from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.services.rag_service import get_rag_response, get_chat_history
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class RagQuery(BaseModel):
    query: str

@router.post("/query/{meeting_id}")
async def query_rag(meeting_id: str, query_data: RagQuery = Body(...)):
    logger.info(f"Received RAG request for meeting {meeting_id} with query: {query_data.query}")
    try:
        result = await get_rag_response(meeting_id, query_data.query)
        if "error" in result:
            logger.warning(f"RAG error for meeting {meeting_id}: {result['error']}")
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"RAG query failed for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/history/{meeting_id}")
async def fetch_chat_history(meeting_id: str):
    logger.info(f"Received chat history request for meeting {meeting_id}")
    try:
        history = await get_chat_history(meeting_id)
        if not history:
            logger.warning(f"No chat history found for meeting {meeting_id}")
            raise HTTPException(status_code=404, detail="No chat history found for this meeting.")
        return {"meeting_id": meeting_id, "chat_history": history}
    except Exception as e:
        logger.error(f"Chat history query failed for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))