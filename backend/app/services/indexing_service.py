# from app.services.google_services import get_drive_service_db, save_drive_documents
# from app.services.mongodb import get_meetings_collection_sync
# from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceHubEmbeddings, HuggingFaceEmbeddings
# from langchain_community.vectorstores import Pinecone
# from pinecone import Pinecone, ServerlessSpec
# from datetime import datetime, timezone
# import time
# import os
# import logging
# from dotenv import load_dotenv
# load_dotenv()




# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Initialize Pinecone client
# pc = Pinecone(api_key="pcsk_paYkE_3MZhMRg9asaa9BApfAMr6HjirYYoHMYU3u6DpNgrecfLa2PQJVDWEVh5RSBDnzg")
# index_name = "cortana-meetings"

# # Create index if it doesn't exist
# if index_name not in pc.list_indexes().names():
#     logger.info(f"Creating Pinecone index: {index_name}")
#     pc.create_index(
#         name=index_name,
#         dimension=1536,
#         metric="cosine",
#         spec=ServerlessSpec(
#             cloud="aws",
#             region="us-east-1"
#         )
#     )
# index = pc.Index(index_name)

# def link_drive(meeting_id: str, drive_access_token: dict, user_id: str):
#     linked_at = datetime.now(timezone.utc)
#     meetings_collection = get_meetings_collection_sync()
#     meetings_collection.update_one(
#         {"_id": meeting_id, "user_id": user_id},
#         {"$set": {"drive_access_token": drive_access_token, "indexing_status": "pending", "linked_at": linked_at}}
#     )
#     logger.info(f"Linked Drive for meeting {meeting_id}, set to pending")
#     return {"message": "Drive linked and awaiting indexing"}

# def index_documents(user_id, meeting_id):
#     meetings_collection = get_meetings_collection_sync()
#     meeting = meetings_collection.find_one({"_id": meeting_id, "user_id": user_id})
#     if not meeting:
#         logger.warning(f"No meeting found for ID {meeting_id} and user {user_id}")
#         return
#     drive_access_token = meeting.get("drive_access_token", {})
#     folder_id = meeting.get("drive_folder_id")
#     if not folder_id:
#         logger.warning(f"No folder_id found for meeting {meeting_id}")
#         return

#     meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "in_progress"}})
#     logger.info(f"Starting indexing for meeting {meeting_id}")
#     try:
#         logger.info(f"Fetching Drive service for meeting {meeting_id}")
#         drive_service = get_drive_service_db(drive_access_token)
#         logger.info(f"Downloading documents for meeting {meeting_id}")
#         documents = save_drive_documents(drive_service, folder_id, meeting_id)
#         logger.info(f"Found {len(documents)} documents for meeting {meeting_id}")
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
#         logger.info(f"Splitting documents for meeting {meeting_id}")
#         chunks = text_splitter.split_documents(documents)
#         logger.info(f"Generated {len(chunks)} chunks for meeting {meeting_id}")
#         embeddings = OpenAIEmbeddings()
        
#         # embeddings = HuggingFaceHubEmbeddings(
#         #     repo_id="sentence-transformers/all-MiniLM-L6-v2",  # You can change this to any supported model
#         #     model_kwargs={"device": "cpu"}  # Use "cuda" if running on GPU
#         # )
#     #     embeddings = HuggingFaceEmbeddings(
#     #         model_name="sentence-transformers/all-MiniLM-L6-v2",
#     #         model_kwargs={"device": "cpu"}
#     # )
#         logger.info(f"Generating embeddings for meeting {meeting_id}")
#         to_upsert = []
#         MAX_TEXT_LEN = 2000
#         for i, chunk in enumerate(chunks):
#             text = chunk.page_content
#             if len(text) > MAX_TEXT_LEN:
#                 logger.warning(f"Skipping chunk {i} for meeting {meeting_id} because it's too large ({len(text)} chars)")
#                 continue
#             metadata = {
#                 "user_id": str(user_id),
#                 "meeting_id": str(meeting_id),
#                 "file_id": chunk.metadata["file_id"],
#                 "chunk_id": i,
#                 "text": text
#             }
#             to_upsert.append((f"{meeting_id}_{i}", embeddings.embed_query(text), metadata))
#         logger.info(f"Preparing to upsert {len(to_upsert)} vectors for meeting {meeting_id}")
#         batch_upsert(index, to_upsert)
#         logger.info(f"Upsert completed for meeting {meeting_id}")
#         meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "completed", "last_indexed_at": datetime.utcnow()}})
#         logger.info(f"Completed indexing for meeting {meeting_id}, {len(to_upsert)} records added")
#     except Exception as e:
#         meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "failed", "indexing_error": str(e)}})
#         logger.error(f"Indexing failed for meeting {meeting_id}: {str(e)}")

# def indexing_worker():
#     meetings_collection = get_meetings_collection_sync()
#     logger.info("Indexer started, checking for pending meetings")
#     while True:
#         pending_meeting = meetings_collection.find_one({"indexing_status": "pending"}, sort=[("drive_linked_at", 1)])
#         logger.debug(f"Queried for pending meetings, result: {pending_meeting is not None}")
#         if pending_meeting:
#             user_id = pending_meeting["user_id"]
#             meeting_id = pending_meeting["_id"]
#             logger.info(f"Processing pending meeting {meeting_id} of {user_id}")
#             meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "in_progress"}})
#             index_documents(user_id, meeting_id)
#         else:
#             logger.debug("No pending meetings, sleeping for 1 second")
#             time.sleep(1)

# BATCH_SIZE = 50  # You can adjust this as needed

# def batch_upsert(index, vectors, batch_size=BATCH_SIZE):
#     for i in range(0, len(vectors), batch_size):
#         batch = vectors[i:i+batch_size]
#         index.upsert(vectors=batch)

from app.services.google_services import get_drive_service_db, save_drive_documents
from app.services.mongodb import get_meetings_collection_sync
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from pinecone import Pinecone, ServerlessSpec
from app.services.document_processor import get_document_processor
from datetime import datetime, timezone
import time
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Pinecone client
pc = Pinecone(api_key="pcsk_paYkE_3MZhMRg9asaa9BApfAMr6HjirYYoHMYU3u6DpNgrecfLa2PQJVDWEVh5RSBDnzg")
index_name = "cortana-meetings"

# Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    logger.info(f"Creating Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
index = pc.Index(index_name)

def link_drive(meeting_id: str, drive_access_token: dict, user_id: str):
    linked_at = datetime.now(timezone.utc)
    meetings_collection = get_meetings_collection_sync()
    meetings_collection.update_one(
        {"_id": meeting_id, "user_id": user_id},
        {"$set": {"drive_access_token": drive_access_token, "indexing_status": "pending", "linked_at": linked_at}}
    )
    logger.info(f"Linked Drive for meeting {meeting_id}, set to pending")
    return {"message": "Drive linked and awaiting indexing"}

def index_documents(user_id: str, meeting_id: str):
    meetings_collection = get_meetings_collection_sync()
    meeting = meetings_collection.find_one({"_id": meeting_id, "user_id": user_id})
    if not meeting:
        logger.warning(f"No meeting found for ID {meeting_id} and user {user_id}")
        return
    drive_access_token = meeting.get("drive_access_token", {})
    folder_id = meeting.get("drive_folder_id")
    if not folder_id:
        logger.warning(f"No folder_id found for meeting {meeting_id}")
        return

    meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "in_progress"}})
    logger.info(f"Starting indexing for meeting {meeting_id}")
    try:
        logger.info(f"Fetching Drive service for meeting {meeting_id}")
        drive_service = get_drive_service_db(drive_access_token)
        logger.info(f"Downloading documents for meeting {meeting_id}")
        documents = save_drive_documents(drive_service, folder_id, meeting_id)
        logger.info(f"Found {len(documents)} documents for meeting {meeting_id}")

        all_docs = []
        for doc in documents:
            metadata = {
                "user_id": str(user_id),
                "meeting_id": str(meeting_id),
                "file_id": doc.metadata.get("file_id", ""),
            }
            processor = get_document_processor(doc.metadata.get("file_path", ""), metadata)
            extracted_docs = processor.process()
            all_docs.extend(extracted_docs)

        logger.info(f"Generated {len(all_docs)} document chunks for meeting {meeting_id}")
        embeddings = OpenAIEmbeddings()
        to_upsert = []
        MAX_TEXT_LEN = 2000
        for i, chunk in enumerate(all_docs):
            text = chunk.page_content
            if len(text) > MAX_TEXT_LEN:
                logger.warning(f"Skipping chunk {i} for meeting {meeting_id} because it's too large ({len(text)} chars)")
                # logger.warning(f"Skipped chunk {text[:50]}... for meeting {meeting_id}")
                # split_texts = split_large_text(text, MAX_TEXT_LEN, overlap=100)
                # for j, split_text in enumerate(split_texts):
                #     metadata = {
                #         "user_id": str(user_id),
                #         "meeting_id": str(meeting_id),
                #         "file_id": chunk.metadata.get("file_id", ""),
                #         "chunk_id": f"{i}_{j}",
                #         "text": split_text
                #     }
                #     to_upsert.append((f"{meeting_id}_{i}_{j}", embeddings.embed_query(split_text), metadata))
                continue
            metadata = {
                "user_id": str(user_id),
                "meeting_id": str(meeting_id),
                "file_id": chunk.metadata.get("file_id", ""),
                "chunk_id": i,
                "text": text  # Explicitly including text in metadata
            }
            to_upsert.append((f"{meeting_id}_{i}", embeddings.embed_query(text), metadata))
        logger.info(f"Preparing to upsert {len(to_upsert)} vectors for meeting {meeting_id}")
        batch_upsert(index, to_upsert)
        logger.info(f"Upsert completed for meeting {meeting_id}")
        meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "completed", "last_indexed_at": datetime.utcnow()}})
        logger.info(f"Completed indexing for meeting {meeting_id}, {len(to_upsert)} records added")
    except Exception as e:
        meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "failed", "indexing_error": str(e)}})
        logger.error(f"Indexing failed for meeting {meeting_id}: {str(e)}")

def indexing_worker():
    meetings_collection = get_meetings_collection_sync()
    logger.info("Indexer started, checking for pending meetings")
    while True:
        pending_meeting = meetings_collection.find_one({"indexing_status": "pending"}, sort=[("drive_linked_at", 1)])
        logger.debug(f"Queried for pending meetings, result: {pending_meeting is not None}")
        if pending_meeting:
            user_id = pending_meeting["user_id"]
            meeting_id = pending_meeting["_id"] # Convert ObjectId to string
            logger.info(f"Processing pending meeting {meeting_id} of {user_id}")
            meetings_collection.update_one({"_id": meeting_id}, {"$set": {"indexing_status": "in_progress"}})
            index_documents(user_id, meeting_id)
        else:
            logger.debug("No pending meetings, sleeping for 1 second")
            time.sleep(1)

BATCH_SIZE = 50  # You can adjust this as needed

def batch_upsert(index, vectors, batch_size=BATCH_SIZE):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)

def split_large_text(text, max_len=2000, overlap=100):
    """Split text into chunks of max_len with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # overlap for context
        if start < 0:
            start = 0
    return chunks