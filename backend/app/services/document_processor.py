from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader
)
# from langchain_community.document_loaders import DocxLoader
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
            '.txt': RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)  # Smaller chunks for text with links
        }
        return splitters.get(ext)

    def _load_document(self, ext: str) -> List[Document]:
        """Load the document using the appropriate LangChain loader."""
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.html': UnstructuredHTMLLoader,
            '.md': UnstructuredMarkdownLoader,
            '.txt': TextLoader
        }
        loader_class = loaders.get(ext)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {ext}")
        loader = loader_class(self.file_path)
        return loader.load()

    # def _process_links(self, text: str) -> List[Document]:
    #     """Extract and scrape content from links in text files."""
    #     documents = []
    #     urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    #     for url in urls:
    #         try:
    #             logger.info(f"Scraping content from {url}")
    #             response = requests.get(url, timeout=5)
    #             response.raise_for_status()
    #             soup = BeautifulSoup(response.content, 'html.parser')
    #             scraped_text = soup.get_text(separator="\n")
    #             doc = Document(page_content=scraped_text, metadata={"file_type": "scraped", "source_url": url})
    #             if self.metadata:
    #                 doc.metadata.update(self.metadata)
    #             documents.append(doc)
    #         except requests.RequestException as e:
    #             logger.warning(f"Failed to scrape {url}: {str(e)}")
    #     return documents

    def _process_links(self, text: str) -> List[Document]:
        """Extract and scrape content from links in text files, splitting into manageable chunks."""
        documents = []
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Consistent with other splitters
        for url in urls:
            try:
                logger.info(f"Scraping content from {url}")
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                scraped_text = soup.get_text(separator="\n")
                # Split the scraped text into chunks
                split_texts = splitter.split_text(scraped_text)
                for i, split_text in enumerate(split_texts):
                    doc = Document(page_content=split_text, metadata={
                        "file_type": "scraped",
                        "source_url": url,
                        "chunk_id": i
                    })
                    if self.metadata:
                        doc.metadata.update(self.metadata)
                    documents.append(doc)
            except requests.RequestException as e:
                logger.warning(f"Failed to scrape {url}: {str(e)}")
        return documents

    def process(self) -> List[Document]:
        """Process the file, apply splitting, and handle links for text files."""
        _, ext = os.path.splitext(self.file_path.lower())
        
        # Load the document
        raw_documents = self._load_document(ext)
        if not raw_documents:
            return []

        # Combine all pages into a single text for initial processing
        full_text = "\n".join(doc.page_content for doc in raw_documents)

        # Apply splitting
        if self.splitter:
            split_documents = self.splitter.split_documents(raw_documents)
        else:
            split_documents = raw_documents

        # Add metadata to all split documents
        self.documents = [self._add_metadata(doc) for doc in split_documents]

        # Special handling for text files with links
        if ext == '.txt':
            link_docs = self._process_links(full_text)
            self.documents.extend(link_docs)

        return self.documents

    def _add_metadata(self, doc: Document) -> Document:
        """Add metadata to a Document object."""
        if self.metadata:
            doc.metadata.update(self.metadata)
        return doc

# Factory to get the processor (simplified since we use one class)
def get_document_processor(file_path: str, metadata: Dict = None) -> DocumentProcessor:
    """Return a DocumentProcessor instance for the file."""
    return DocumentProcessor(file_path, metadata)