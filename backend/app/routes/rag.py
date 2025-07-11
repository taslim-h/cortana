from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.services.rag_service import get_rag_response
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