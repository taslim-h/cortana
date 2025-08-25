
# from langchain.document_loaders import (
#     PyPDFLoader,
#     TextLoader,
#     UnstructuredHTMLLoader,
#     UnstructuredMarkdownLoader,
#     Docx2txtLoader,
#     UnstructuredImageLoader,
# )
# from langchain.text_splitter import (
#     RecursiveCharacterTextSplitter,
#     MarkdownTextSplitter
# )
# from langchain.schema import Document
# from typing import List, Dict, Optional
# import os
# import logging
# import requests
# from bs4 import BeautifulSoup
# import re
# from urllib.parse import urlparse
# from PIL import Image
# from transformers import BlipProcessor, BlipForConditionalGeneration
# import subprocess
# import torch
# from app.services.image_processor import EnhancedImageProcessor

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize BLIP model for image captioning
# # blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
# # blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# class DocumentProcessor:
#     """Class to manage document loading and splitting based on file type."""
    
#     def __init__(self, file_path: str, metadata: Dict = None):
#         self.file_path = file_path
#         self.metadata = metadata or {}
#         self.documents: List[Document] = []
#         self._setup_splitter()
#         self.image_processor = EnhancedImageProcessor()  # Initialize here

#     def _setup_splitter(self):
#         """Set up the appropriate text splitter based on file type."""
#         _, ext = os.path.splitext(self.file_path.lower())
#         self.splitter = self._get_splitter(ext)

#     def _get_splitter(self, ext: str) -> Optional[object]:
#         """Return the appropriate text splitter for the file extension."""
#         splitters = {
#             '.pdf': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.docx': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.html': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.md': MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.txt': RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100),
#             '.jpg': None,  # Images don't need splitting
#             '.jpeg': None,
#             '.png': None,
#             '.mp4': None   # Videos don't need splitting
#         }
#         return splitters.get(ext)

#     def _load_document(self, ext: str) -> List[Document]:
#         """Load the document using the appropriate LangChain loader."""
#         loaders = {
#             '.pdf': PyPDFLoader,
#             '.docx': Docx2txtLoader,
#             '.html': UnstructuredHTMLLoader,
#             '.md': UnstructuredMarkdownLoader,
#             '.txt': TextLoader,
#             '.jpg': UnstructuredImageLoader,
#             '.jpeg': UnstructuredImageLoader,
#             '.png': UnstructuredImageLoader,
#         }
#         loader_class = loaders.get(ext)
        
#         if not loader_class:
#             # Handle unsupported file types
#             if ext in ['.jpg', '.jpeg', '.png']:
#                 return self._process_local_image(self.file_path)
#             elif ext in ['.mp4']:
#                 return self._process_local_video(self.file_path)
#             else:
#                 raise ValueError(f"Unsupported file type: {ext}")
                
#         loader = loader_class(self.file_path)
#         docs = loader.load()
        
#         # Handle images
#         if ext in ['.jpg', '.jpeg', '.png']:
#             # for doc in docs:
#             #     # Ensure we have valid page content
#             #     if doc.page_content is None or not doc.page_content.strip():
#             #         doc.page_content = "No text extracted"
                
#             #     # Generate caption and append it
#             #     caption = self._generate_image_caption(self.file_path)
#             #     doc.page_content += f" [Caption: {caption}]"
#             for doc in docs:
#                 if not doc.page_content or doc.page_content.isspace():
#                     doc.page_content = "No text extracted"
#                 # Use EnhancedImageProcessor
#                 processed_content = self.image_processor.process_image(self.file_path)
#                 doc.page_content = processed_content if processed_content else doc.page_content
#         return docs

#     # def _generate_image_caption(self, image_path: str) -> str:
#     #     """Generate a caption for an image using BLIP."""
#     #     try:
#     #         # Open image and ensure it's in RGB format
#     #         image = Image.open(image_path).convert("RGB")
            
#     #         # Generate caption
#     #         inputs = blip_processor(images=image, return_tensors="pt")
            
#     #         # Use CPU if CUDA is not available
#     #         device = "cuda" if torch.cuda.is_available() else "cpu"
#     #         inputs = inputs.to(device)
#     #         blip_model.to(device)
            
#     #         outputs = blip_model.generate(**inputs)
#     #         caption = blip_processor.decode(outputs[0], skip_special_tokens=True)
            
#     #         return caption if caption else "No caption available"
#     #     except Exception as e:
#     #         logger.warning(f"Failed to generate caption for {image_path}: {str(e)}")
#     #         return "Caption unavailable"

#     # def _generate_image_caption(self, image_path: str) -> str:
#     #     """Enhanced image captioning with object counting"""
#     #     try:
#     #         # processor = EnhancedImageProcessor()
#     #         # return processor.generate_detailed_caption(image_path)
#     #          """Generate enhanced image caption"""
#     #          processor = EnhancedImageProcessor()
#     #          result = processor.process_image(image_path)
#     #          # Format for RAG system
#     #          return (
#     #          f"Description: {result['description']}\n"
#     #          f"Objects: {', '.join(f'{count} {label}' for label, count in result['object_counts'].items())}"
#     #          )
#     #     except Exception as e:
#     #         logger.warning(f"Enhanced captioning failed: {str(e)}")
#     #         # Fallback to BLIP if detailed processing fails
#     #         return self._generate_blip_caption(image_path)

#     def _generate_video_description(self, video_path: str) -> str:
#         """Generate a simple description by extracting a key frame."""
#         try:
#             # Extract a frame from video
#             frame_path = f"temp_frame_{os.urandom(4).hex()}.jpg"
#             subprocess.run([
#                 "ffmpeg", "-i", video_path, 
#                 "-ss", "00:00:01",  # Capture at 1 second
#                 "-vframes", "1", 
#                 frame_path
#             ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
#             # Generate caption from the frame
#             caption = self._generate_image_caption(frame_path)
#             os.remove(frame_path)
#             return caption
#         except Exception as e:
#             logger.warning(f"Failed to generate video description for {video_path}: {str(e)}")
#             return "Video content unavailable"

#     def _process_local_image(self, file_path: str) -> List[Document]:
#         """Process local image file using BLIP captioning."""
#         try:
#             caption = self._generate_image_caption(file_path)
#             return [Document(
#                 page_content=f"IMAGE CONTENT: {caption}",
#                 metadata={
#                     "media_type": "image",
#                     "source_path": file_path,
#                     "file_name": os.path.basename(file_path)
#                 }
#             )]
#         except Exception as e:
#             logger.error(f"Failed to process image {file_path}: {str(e)}")
#             return [Document(
#                 page_content="IMAGE CONTENT: Processing error",
#                 metadata={
#                     "media_type": "image",
#                     "source_path": file_path,
#                     "error": str(e)
#                 }
#             )]

#     def _process_local_video(self, file_path: str) -> List[Document]:
#         """Process local video file by generating description."""
#         try:
#             description = self._generate_video_description(file_path)
#             return [Document(
#                 page_content=f"VIDEO CONTENT: {description}",
#                 metadata={
#                     "media_type": "video",
#                     "source_path": file_path,
#                     "file_name": os.path.basename(file_path)
#                 }
#             )]
#         except Exception as e:
#             logger.error(f"Failed to process video {file_path}: {str(e)}")
#             return [Document(
#                 page_content="VIDEO CONTENT: Processing error",
#                 metadata={
#                     "media_type": "video",
#                     "source_path": file_path,
#                     "error": str(e)
#                 }
#             )]

#     def _process_links(self, text: str) -> List[Document]:
#         """Extract and process all types of links from text."""
#         documents = []
#         urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
#         for url in urls:
#             try:
#                 # Get content type
#                 head_response = requests.head(url, timeout=5, allow_redirects=True)
#                 content_type = head_response.headers.get('Content-Type', '').split(';')[0].lower()
                
#                 if content_type.startswith('image/'):
#                     # Process image URL
#                     img_response = requests.get(url, timeout=10)
#                     img_response.raise_for_status()
                    
#                     # Save temp image
#                     ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
#                     img_path = f"temp_img_{os.urandom(4).hex()}{ext}"
#                     with open(img_path, 'wb') as f:
#                         f.write(img_response.content)
                    
#                     # Process and caption
#                     docs = self._process_local_image(img_path)
#                     for doc in docs:
#                         doc.metadata["source_url"] = url
#                         if self.metadata:
#                             doc.metadata.update(self.metadata)
                    
#                     documents.extend(docs)
#                     os.remove(img_path)
                    
#                 elif content_type.startswith('video/'):
#                     # For videos, just store metadata
#                     documents.append(Document(
#                         page_content=f"VIDEO CONTENT: [See source URL]",
#                         metadata={
#                             "media_type": "video",
#                             "source_url": url,
#                             "content_type": content_type
#                         }
#                     ))
                    
#                 else:
#                     # Process as HTML
#                     response = requests.get(url, timeout=5)
#                     response.raise_for_status()
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Clean text
#                     for script in soup(["script", "style"]):
#                         script.extract()
#                     text = soup.get_text(separator="\n")
#                     lines = (line.strip() for line in text.splitlines())
#                     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#                     clean_text = '\n'.join(chunk for chunk in chunks if chunk)
                    
#                     # Split into chunks
#                     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#                     docs = splitter.create_documents([clean_text])
                    
#                     # Add metadata
#                     for doc in docs:
#                         doc.metadata = {
#                             "media_type": "webpage",
#                             "source_url": url,
#                             "content_type": content_type
#                         }
#                         if self.metadata:
#                             doc.metadata.update(self.metadata)
#                     documents.extend(docs)
                    
#             except Exception as e:
#                 logger.warning(f"Failed to process link {url}: {str(e)}")
                
#         return documents

#     def process(self) -> List[Document]:
#         """Process the file, handling various types including multimedia."""
#         _, ext = os.path.splitext(self.file_path.lower())
        
#         # Handle local multimedia files directly
#         if ext in ['.jpg', '.jpeg', '.png']:
#             return self._process_local_image(self.file_path)
#         elif ext in ['.mp4']:
#             return self._process_local_video(self.file_path)
        
#         # Handle standard document types
#         try:
#             # Load the document
#             raw_documents = self._load_document(ext)
#             if not raw_documents:
#                 return []

#             # Combine all pages into a single text for initial processing
#             full_text = "\n".join(doc.page_content for doc in raw_documents)

#             # Apply splitting if needed
#             if self.splitter:
#                 split_documents = self.splitter.split_documents(raw_documents)
#             else:
#                 split_documents = raw_documents

#             # Add metadata to all split documents
#             self.documents = [self._add_metadata(doc) for doc in split_documents]

#             # Process links in text-based documents
#             if ext in ['.txt', '.md', '.html', '.docx', '.pdf']:
#                 link_docs = self._process_links(full_text)
#                 self.documents.extend(link_docs)

#             return self.documents
        
#         except Exception as e:
#             logger.error(f"Error processing file {self.file_path}: {str(e)}")
#             return []

#     def _add_metadata(self, doc: Document) -> Document:
#         """Add metadata to a Document object."""
#         if self.metadata:
#             doc.metadata.update(self.metadata)
#         return doc

# # Factory to get the processor
# def get_document_processor(file_path: str, metadata: Dict = None) -> DocumentProcessor:
#     """Return a DocumentProcessor instance for the file."""
#     return DocumentProcessor(file_path, metadata)


#stable
# from langchain.document_loaders import (
#     PyPDFLoader,
#     TextLoader,
#     UnstructuredHTMLLoader,
#     UnstructuredMarkdownLoader,
#     Docx2txtLoader,
#     UnstructuredImageLoader,
# )
# from langchain.text_splitter import (
#     RecursiveCharacterTextSplitter,
#     MarkdownTextSplitter
# )
# from langchain.schema import Document
# from typing import List, Dict, Optional
# import os
# import logging
# import requests
# from bs4 import BeautifulSoup
# import re
# from urllib.parse import urlparse
# from PIL import Image
# import subprocess
# from app.services.image_processor import EnhancedImageProcessor

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class DocumentProcessor:
#     """Class to manage document loading and splitting based on file type."""
    
#     def __init__(self, file_path: str, metadata: Dict = None):
#         self.file_path = file_path
#         self.metadata = metadata or {}
#         self.documents: List[Document] = []
#         self._setup_splitter()
#         self.image_processor = EnhancedImageProcessor()  # Initialize here

#     def _setup_splitter(self):
#         """Set up the appropriate text splitter based on file type."""
#         _, ext = os.path.splitext(self.file_path.lower())
#         self.splitter = self._get_splitter(ext)

#     def _get_splitter(self, ext: str) -> Optional[object]:
#         """Return the appropriate text splitter for the file extension."""
#         splitters = {
#             '.pdf': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.docx': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.html': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.md': MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200),
#             '.txt': RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100),
#             '.jpg': None,
#             '.jpeg': None,
#             '.png': None,
#             '.mp4': None
#         }
#         return splitters.get(ext)

#     def _load_document(self, ext: str) -> List[Document]:
#         """Load the document using the appropriate LangChain loader."""
#         loaders = {
#             '.pdf': PyPDFLoader,
#             '.docx': Docx2txtLoader,
#             '.html': UnstructuredHTMLLoader,
#             '.md': UnstructuredMarkdownLoader,
#             '.txt': TextLoader,
#             '.jpg': UnstructuredImageLoader,
#             '.jpeg': UnstructuredImageLoader,
#             '.png': UnstructuredImageLoader,
#         }
#         loader_class = loaders.get(ext)
        
#         if not loader_class:
#             if ext in ['.jpg', '.jpeg', '.png']:
#                 return self._process_local_image(self.file_path)
#             elif ext == '.mp4':
#                 return self._process_local_video(self.file_path)
#             else:
#                 raise ValueError(f"Unsupported file type: {ext}")
                
#         loader = loader_class(self.file_path)
#         docs = loader.load()
        
#         if ext in ['.jpg', '.jpeg', '.png']:
#             doc = docs[0] if docs else Document()  # Assume single document per image
#             if not doc.page_content or doc.page_content.isspace():
#                 doc.page_content = "No text extracted"
#             processed_content = self.image_processor.process_image(self.file_path)
#             doc.page_content = processed_content if processed_content else doc.page_content
#             return [doc]
        
#         return docs

#     def _process_local_image(self, file_path: str) -> List[Document]:
#         """Process local image file using EnhancedImageProcessor."""
#         try:
#             processed_content = self.image_processor.process_image(file_path)
#             return [Document(
#                 page_content=processed_content or "IMAGE CONTENT: Processing error",
#                 metadata={
#                     "media_type": "image",
#                     "source_path": file_path,
#                     "file_name": os.path.basename(file_path)
#                 }
#             )]
#         except Exception as e:
#             logger.error(f"Failed to process image {file_path}: {str(e)}")
#             return [Document(
#                 page_content="IMAGE CONTENT: Processing error",
#                 metadata={
#                     "media_type": "image",
#                     "source_path": file_path,
#                     "error": str(e)
#                 }
#             )]

#     def _process_local_video(self, file_path: str) -> List[Document]:
#         """Process local video file by generating description and potential OCR."""
#         try:
#             # Extract a frame
#             frame_path = f"temp_frame_{os.urandom(4).hex()}.jpg"
#             subprocess.run([
#                 "ffmpeg", "-i", file_path,
#                 "-ss", "00:00:01",
#                 "-vframes", "1",
#                 frame_path
#             ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
#             # Process frame with EnhancedImageProcessor
#             processed_content = self.image_processor.process_image(frame_path)
#             os.remove(frame_path)
            
#             return [Document(
#                 page_content=f"VIDEO CONTENT: {processed_content or 'No content extracted'}",
#                 metadata={
#                     "media_type": "video",
#                     "source_path": file_path,
#                     "file_name": os.path.basename(file_path)
#                 }
#             )]
#         except Exception as e:
#             logger.error(f"Failed to process video {file_path}: {str(e)}")
#             return [Document(
#                 page_content="VIDEO CONTENT: Processing error",
#                 metadata={
#                     "media_type": "video",
#                     "source_path": file_path,
#                     "error": str(e)
#                 }
#             )]

#     def _process_links(self, text: str) -> List[Document]:
#         """Extract and process all types of links from text."""
#         documents = []
#         urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
#         for url in urls:
#             try:
#                 head_response = requests.head(url, timeout=5, allow_redirects=True)
#                 content_type = head_response.headers.get('Content-Type', '').split(';')[0].lower()
                
#                 if content_type.startswith('image/'):
#                     img_response = requests.get(url, timeout=10)
#                     img_response.raise_for_status()
#                     ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
#                     img_path = f"temp_img_{os.urandom(4).hex()}{ext}"
#                     with open(img_path, 'wb') as f:
#                         f.write(img_response.content)
                    
#                     docs = self._process_local_image(img_path)
#                     for doc in docs:
#                         doc.metadata["source_url"] = url
#                         if self.metadata:
#                             doc.metadata.update(self.metadata)
#                     documents.extend(docs)
#                     os.remove(img_path)
                
#                 elif content_type.startswith('video/'):
#                     # Enhanced video processing
#                     video_response = requests.get(url, timeout=10)
#                     video_response.raise_for_status()
#                     video_path = f"temp_video_{os.urandom(4).hex()}.mp4"
#                     with open(video_path, 'wb') as f:
#                         f.write(video_response.content)
                    
#                     docs = self._process_local_video(video_path)
#                     for doc in docs:
#                         doc.metadata["source_url"] = url
#                         if self.metadata:
#                             doc.metadata.update(self.metadata)
#                     documents.extend(docs)
#                     os.remove(video_path)
                
#                 else:
#                     response = requests.get(url, timeout=5)
#                     response.raise_for_status()
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     for script in soup(["script", "style"]):
#                         script.extract()
#                     text = soup.get_text(separator="\n")
#                     lines = (line.strip() for line in text.splitlines())
#                     chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
#                     clean_text = '\n'.join(chunk for chunk in chunks if chunk)
                    
#                     splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#                     docs = splitter.create_documents([clean_text])
                    
#                     for doc in docs:
#                         doc.metadata = {
#                             "media_type": "webpage",
#                             "source_url": url,
#                             "content_type": content_type
#                         }
#                         if self.metadata:
#                             doc.metadata.update(self.metadata)
#                     documents.extend(docs)
                    
#             except Exception as e:
#                 logger.warning(f"Failed to process link {url}: {str(e)}")
                
#         return documents

#     def process(self) -> List[Document]:
#         """Process the file, handling various types including multimedia."""
#         _, ext = os.path.splitext(self.file_path.lower())
        
#         if ext in ['.jpg', '.jpeg', '.png', '.mp4']:
#             return self._process_local_image(self.file_path) if ext in ['.jpg', '.jpeg', '.png'] else self._process_local_video(self.file_path)
        
#         try:
#             raw_documents = self._load_document(ext)
#             if not raw_documents:
#                 return []

#             full_text = "\n".join(doc.page_content for doc in raw_documents)

#             if self.splitter:
#                 split_documents = self.splitter.split_documents(raw_documents)
#             else:
#                 split_documents = raw_documents

#             self.documents = [self._add_metadata(doc) for doc in split_documents]

#             if ext in ['.txt', '.md', '.html', '.docx', '.pdf']:
#                 link_docs = self._process_links(full_text)
#                 self.documents.extend(link_docs)

#             return self.documents
        
#         except Exception as e:
#             logger.error(f"Error processing file {self.file_path}: {str(e)}")
#             return []

#     def _add_metadata(self, doc: Document) -> Document:
#         """Add metadata to a Document object."""
#         if self.metadata:
#             doc.metadata.update(self.metadata)
#         return doc

# # Factory to get the processor
# def get_document_processor(file_path: str, metadata: Dict = None) -> DocumentProcessor:
#     """Return a DocumentProcessor instance for the file."""
#     return DocumentProcessor(file_path, metadata)


#102

from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
    UnstructuredImageLoader,
)
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter
)
from langchain.schema import Document
from typing import List, Dict, Optional
import os
import logging
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from PIL import Image
import subprocess
from app.services.image_processor import EnhancedImageProcessor
from app.services.GoogleVideoProcessor import GoogleVideoProcessor  # New import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Class to manage document loading and splitting based on file type."""
    
    def __init__(self, file_path: str, metadata: Dict = None):
        self.file_path = file_path
        self.metadata = metadata or {}
        self.documents: List[Document] = []
        self._setup_splitter()
        self.image_processor = EnhancedImageProcessor()  # Initialize here
        self.video_processor = GoogleVideoProcessor(gcs_bucket_name=os.getenv("GCS_BUCKET_NAME"))  # New initialization

    def _setup_splitter(self):
        """Set up the appropriate text splitter based on file type."""
        _, ext = os.path.splitext(self.file_path.lower())
        self.splitter = self._get_splitter(ext)

    def _get_splitter(self, ext: str) -> Optional[object]:
        """Return the appropriate text splitter for the file extension."""
        splitters = {
            '.pdf': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
            '.docx': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
            '.html': RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
            '.md': MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200),
            '.txt': RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100),
            '.jpg': None,
            '.jpeg': None,
            '.png': None,
            '.mp4': None
        }
        return splitters.get(ext)

    def _load_document(self, ext: str) -> List[Document]:
        """Load the document using the appropriate LangChain loader."""
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.html': UnstructuredHTMLLoader,
            '.md': UnstructuredMarkdownLoader,
            '.txt': TextLoader,
            '.jpg': UnstructuredImageLoader,
            '.jpeg': UnstructuredImageLoader,
            '.png': UnstructuredImageLoader,
        }
        loader_class = loaders.get(ext)
        
        if not loader_class:
            if ext in ['.jpg', '.jpeg', '.png']:
                return self._process_local_image(self.file_path)
            elif ext == '.mp4':
                return self.video_processor.process_video(self.file_path)  # Updated to use GoogleVideoProcessor
            else:
                raise ValueError(f"Unsupported file type: {ext}")
                
        loader = loader_class(self.file_path)
        docs = loader.load()
        
        if ext in ['.jpg', '.jpeg', '.png']:
            doc = docs[0] if docs else Document()  # Assume single document per image
            if not doc.page_content or doc.page_content.isspace():
                doc.page_content = "No text extracted"
            processed_content = self.image_processor.process_image(self.file_path)
            doc.page_content = processed_content if processed_content else doc.page_content
            return [doc]
        
        return docs

    def _process_local_image(self, file_path: str) -> List[Document]:
        """Process local image file using EnhancedImageProcessor."""
        try:
            processed_content = self.image_processor.process_image(file_path)
            return [Document(
                page_content=processed_content or "IMAGE CONTENT: Processing error",
                metadata={
                    "media_type": "image",
                    "source_path": file_path,
                    "file_name": os.path.basename(file_path)
                }
            )]
        except Exception as e:
            logger.error(f"Failed to process image {file_path}: {str(e)}")
            return [Document(
                page_content="IMAGE CONTENT: Processing error",
                metadata={
                    "media_type": "image",
                    "source_path": file_path,
                    "error": str(e)
                }
            )]

    def _process_local_video(self, file_path: str) -> List[Document]:
        """Deprecated: Use video_processor.process_video instead."""
        logger.warning("Deprecated method _process_local_video called. Use video_processor.process_video.")
        return self.video_processor.process_video(file_path)  # Redirect to new method

    def _process_links(self, text: str) -> List[Document]:
        """Extract and process all types of links from text."""
        documents = []
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        for url in urls:
            try:
                head_response = requests.head(url, timeout=5, allow_redirects=True)
                content_type = head_response.headers.get('Content-Type', '').split(';')[0].lower()
                
                if content_type.startswith('image/'):
                    img_response = requests.get(url, timeout=10)
                    img_response.raise_for_status()
                    ext = os.path.splitext(urlparse(url).path)[1] or '.jpg'
                    img_path = f"temp_img_{os.urandom(4).hex()}{ext}"
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    docs = self._process_local_image(img_path)
                    for doc in docs:
                        doc.metadata["source_url"] = url
                        if self.metadata:
                            doc.metadata.update(self.metadata)
                    documents.extend(docs)
                    os.remove(img_path)
                
                elif content_type.startswith('video/'):
                    video_response = requests.get(url, timeout=10)
                    video_response.raise_for_status()
                    video_path = f"temp_video_{os.urandom(4).hex()}.mp4"
                    with open(video_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    docs = self.video_processor.process_video(video_path)  # Updated to use GoogleVideoProcessor
                    for doc in docs:
                        doc.metadata["source_url"] = url
                        if self.metadata:
                            doc.metadata.update(self.metadata)
                    documents.extend(docs)
                    os.remove(video_path)
                
                else:
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    for script in soup(["script", "style"]):
                        script.extract()
                    text = soup.get_text(separator="\n")
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    docs = splitter.create_documents([clean_text])
                    
                    for doc in docs:
                        doc.metadata = {
                            "media_type": "webpage",
                            "source_url": url,
                            "content_type": content_type
                        }
                        if self.metadata:
                            doc.metadata.update(self.metadata)
                    documents.extend(docs)
                    
            except Exception as e:
                logger.warning(f"Failed to process link {url}: {str(e)}")
                
        return documents

    def process(self) -> List[Document]:
        """Process the file, handling various types including multimedia."""
        _, ext = os.path.splitext(self.file_path.lower())
        
        if ext in ['.jpg', '.jpeg', '.png', '.mp4']:
            return self._process_local_image(self.file_path) if ext in ['.jpg', '.jpeg', '.png'] else self.video_processor.process_video(self.file_path)  # Updated
        
        try:
            raw_documents = self._load_document(ext)
            if not raw_documents:
                return []

            full_text = "\n".join(doc.page_content for doc in raw_documents)

            if self.splitter:
                split_documents = self.splitter.split_documents(raw_documents)
            else:
                split_documents = raw_documents

            self.documents = [self._add_metadata(doc) for doc in split_documents]

            if ext in ['.txt', '.md', '.html', '.docx', '.pdf']:
                link_docs = self._process_links(full_text)
                self.documents.extend(link_docs)

            return self.documents
        
        except Exception as e:
            logger.error(f"Error processing file {self.file_path}: {str(e)}")
            return []

    def _add_metadata(self, doc: Document) -> Document:
        """Add metadata to a Document object."""
        if self.metadata:
            doc.metadata.update(self.metadata)
        return doc

# Factory to get the processor
def get_document_processor(file_path: str, metadata: Dict = None) -> DocumentProcessor:
    """Return a DocumentProcessor instance for the file."""
    return DocumentProcessor(file_path, metadata)