# Unnecessary chunking removed
import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure as ConnectionError
from datetime import datetime, timedelta, timezone
from multiprocessing import Process
import logging
from dateutil import parser as dateutil_parser
import pytz
import warnings
import atexit
from collections import deque
import hashlib
import json
from typing import List, Dict, Optional
import re
import threading
import signal
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('pymongo').setLevel(logging.WARNING)

# Import for Pinecone and OpenAI
try:
    from pinecone import Pinecone
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    PINECONE_AVAILABLE = True
    logger.info("✓ Pinecone and OpenAI modules loaded successfully")
except ImportError as e:
    logger.warning(f"Pinecone or OpenAI not installed: {e}")
    PINECONE_AVAILABLE = False

# Suppress ResourceWarning for undetected_chromedriver on Windows
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message=".*unclosed.*")

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "meeting_assistant"

# Timezone Configuration
LOCAL_TZ = pytz.timezone('Asia/Dhaka')
ASSUME_DB_TIMES_ARE_LOCAL = True

# Pinecone Configuration
if PINECONE_AVAILABLE:
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
    
    # Log environment variables (without exposing sensitive data)
    logger.info(f"PINECONE_API_KEY: {'✓ Set' if PINECONE_API_KEY else '❌ Not set'}")
    logger.info(f"PINECONE_INDEX_NAME: {PINECONE_INDEX_NAME if PINECONE_INDEX_NAME else '❌ Not set'}")
    logger.info(f"OPENAI_API_KEY: {'✓ Set' if OPENAI_API_KEY else '❌ Not set'}")
    logger.info(f"EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    
    # Initialize OpenAI
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        logger.info("✓ OpenAI API key set")
    else:
        logger.error("❌ OpenAI API key not found in environment variables")

# Global variable to track active drivers for cleanup
active_drivers = []
cleanup_lock = threading.Lock()

# Improved cleanup function
def cleanup_chrome_processes():
    """Clean up Chrome processes and active drivers"""
    global active_drivers
    
    with cleanup_lock:
        # First, quit active drivers properly
        for driver in active_drivers[:]:  # Make a copy to avoid modification during iteration
            try:
                if driver and hasattr(driver, 'quit'):
                    logger.info("Cleaning up Chrome driver...")
                    driver.quit()
                    active_drivers.remove(driver)
            except Exception as e:
                logger.debug(f"Error cleaning up driver: {e}")
    
    # Then kill any remaining Chrome processes
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    proc.terminate()
                    logger.debug(f"Terminated Chrome process {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        logger.debug("psutil not available for process cleanup")
    except Exception as e:
        logger.debug(f"Error in Chrome process cleanup: {e}")

# Register cleanup functions
atexit.register(cleanup_chrome_processes)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Received shutdown signal, cleaning up...")
    cleanup_chrome_processes()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Chrome Setup Function
def setup_undetected_chrome():
    """Set up an undetected Chrome instance using undetected-chromedriver."""
    global active_drivers
    
    try:
        import undetected_chromedriver as uc
        
        warnings.filterwarnings("ignore", category=ResourceWarning)
        
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        # Add more stability options
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # Remove this if you need JS
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        
        driver = uc.Chrome(options=options, version_main=None)
        
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        driver.implicitly_wait(10)
        
        # Add to active drivers list for cleanup
        with cleanup_lock:
            active_drivers.append(driver)
        
        logger.info("✓ Undetected Chrome ready!")
        return driver
    except ImportError as e:
        logger.error(f"❌ Install: pip install undetected-chromedriver - Error: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Chrome setup failed: {e}")
        return None

# Updated Caption Processor Class
class CaptionProcessor:
    def __init__(self, meeting_id: str, user_id: str):
        self.meeting_id = meeting_id
        self.user_id = user_id
        self.processed_captions = {}
        self.conversation_buffer = deque(maxlen=50)
        self.chunk_start_time = datetime.now(timezone.utc)
        self.current_chunk = []
        self.chunk_word_count = 0
        # Optimized thresholds for near real-time processing
        self.min_chunk_words = 8   # Much lower threshold for faster uploads
        self.max_chunk_words = 50  # Smaller chunks for faster processing
        self.max_chunk_seconds = 8  # Force chunk every 8 seconds for real-time response
        self.chunk_counter = 0
        self.pinecone_client = None
        self.pinecone_index = None
        # Timeout for partial sentences
        self.last_caption_time = datetime.now(timezone.utc)
        self.incomplete_sentence_timeout = 5  # Much shorter timeout for responsiveness
        
        # Real-time processing settings
        self.rapid_mode = True  # Enable rapid upload mode
        self.last_chunk_time = datetime.now(timezone.utc)
        self.pending_uploads = []  # Queue for background uploads
        
        # Initialize Pinecone if available
        if PINECONE_AVAILABLE and PINECONE_API_KEY and PINECONE_INDEX_NAME:
            try:
                logger.info(f"Initializing Pinecone with index: {PINECONE_INDEX_NAME}")
                self.pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
                
                # List available indexes to verify connection
                available_indexes = self.pinecone_client.list_indexes()
                logger.info(f"Available Pinecone indexes: {[idx.name for idx in available_indexes]}")
                
                # Check if our index exists
                index_exists = any(idx.name == PINECONE_INDEX_NAME for idx in available_indexes)
                if not index_exists:
                    logger.error(f"❌ Index '{PINECONE_INDEX_NAME}' not found in Pinecone")
                    self.pinecone_client = None
                    return
                
                self.pinecone_index = self.pinecone_client.Index(PINECONE_INDEX_NAME)
                
                # Test the index with a describe_index_stats call
                stats = self.pinecone_index.describe_index_stats()
                logger.info(f"✓ Pinecone index connected. Current vectors: {stats.get('total_vector_count', 0)}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Pinecone: {e}")
                import traceback
                logger.error(traceback.format_exc())
                self.pinecone_client = None
                self.pinecone_index = None
        else:
            logger.warning("⚠ Pinecone not initialized - missing API key or index name")
    
    def _generate_hash(self, text: str, speaker: str, timestamp: str) -> str:
        """Generate unique hash for caption entry"""
        content = f"{speaker}:{text}:{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_chunk_id(self) -> str:
        """Generate unique chunk ID"""
        self.chunk_counter += 1
        timestamp = int(datetime.now(timezone.utc).timestamp())
        return f"{self.meeting_id}_chunk_{self.chunk_counter:04d}_{timestamp}"
    
    def _is_complete_sentence(self, text: str) -> bool:
        """Check if text appears to be a complete sentence/phrase"""
        if text.strip().endswith(('.', '!', '?', '。', '？', '！')):
            return True
        if len(text.split()) >= 3:  # Reduced threshold for testing
            return True
        return False
    
    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding using OpenAI"""
        if not PINECONE_AVAILABLE or not OPENAI_API_KEY:
            logger.error("❌ Cannot create embedding - OpenAI not configured")
            return None
        
        try:
            logger.info(f"Creating embedding for text: {text[:100]}...")
            
            # Try new OpenAI client first
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=text
                )
                embedding = response.data[0].embedding
                logger.info(f"✓ Created embedding with {len(embedding)} dimensions")
                return embedding
            except Exception as e:
                logger.info(f"New OpenAI client failed, trying legacy method: {e}")
                # Fallback for older versions
                response = openai.Embedding.create(
                    model=EMBEDDING_MODEL,
                    input=text
                )
                embedding = response['data'][0]['embedding']
                logger.info(f"✓ Created embedding with {len(embedding)} dimensions (legacy)")
                return embedding
                
        except Exception as e:
            logger.error(f"❌ Failed to create embedding: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _format_conversation_chunk(self, chunk: List[Dict], chunk_id: str) -> str:
        """Format conversation chunk for better LLM understanding"""
        if not chunk:
            return ""
        
        start_time = chunk[0]['timestamp']
        end_time = chunk[-1]['timestamp']
        
        formatted = f"Meeting conversation timestamp '{start_time}' to '{end_time}'\n"
        formatted += f"Chunk ID: {chunk_id}\n\n"
        
        for entry in chunk:
            formatted += f"Timestamp: {entry['timestamp']}\n"
            formatted += f"{entry['speaker']}:\n"
            formatted += f"Speech: {entry['text']}\n\n"
        
        return formatted.strip()
    
    def _upload_to_pinecone(self, chunk_text: str, chunk_data: List[Dict], chunk_id: str, retry_count: int = 0):
        """Upload chunk to Pinecone with retry logic and background processing"""
        if not self.pinecone_index:
            logger.error("❌ Cannot upload - Pinecone index not initialized")
            return
        
        max_retries = 2  # Reduced retries for faster processing
        
        try:
            logger.info(f"📤 Starting RAPID upload for chunk {chunk_id}")
            
            # Create embedding
            embedding = self._create_embedding(chunk_text)
            if not embedding:
                logger.error("❌ Failed to create embedding for chunk")
                return
            
            # Prepare metadata with conversation context
            metadata = {
                'meeting_id': self.meeting_id,
                'user_id': self.user_id,
                'text': chunk_text[:1500],  # More text for better context
                'chunk_id': chunk_id,
                'chunk_number': self.chunk_counter,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'chunk_start': chunk_data[0]['timestamp'] if chunk_data else '',
                'chunk_end': chunk_data[-1]['timestamp'] if chunk_data else '',
                'speaker_count': len(set(entry['speaker'] for entry in chunk_data)),
                'word_count': sum(len(entry['text'].split()) for entry in chunk_data),
                'processing_mode': 'rapid_real_time',
                'upload_delay_seconds': (datetime.now(timezone.utc) - self.last_chunk_time).total_seconds()
            }
            
            logger.info(f"📋 RAPID upload - {metadata['word_count']} words, {metadata['speaker_count']} speakers, {metadata['upload_delay_seconds']:.1f}s delay")
            
            # Upload to Pinecone immediately
            self.pinecone_index.upsert(
                vectors=[(chunk_id, embedding, metadata)]
            )
            
            upload_time = datetime.now(timezone.utc)
            time_since_conversation = (upload_time - dateutil_parser.parse(chunk_data[-1]['timestamp'])).total_seconds()
            
            logger.info(f"✅ RAPID upload complete for chunk {chunk_id}! Available for RAG in ~{time_since_conversation:.1f}s from conversation")
            
            # Update timing for next chunk
            self.last_chunk_time = upload_time
            
        except Exception as e:
            logger.error(f"❌ Failed RAPID upload for chunk {chunk_id}: {e}")
            
            if retry_count < max_retries:
                wait_time = 1  # Much shorter retry delay
                logger.info(f"🔄 Rapid retry in {wait_time}s...")
                time.sleep(wait_time)
                self._upload_to_pinecone(chunk_text, chunk_data, chunk_id, retry_count + 1)
            else:
                logger.error(f"❌ RAPID upload failed after {max_retries} retries for chunk {chunk_id}")
    
    def process_caption(self, speaker: str, text: str, timestamp: Optional[str] = None):
        """Process new caption entry with rapid upload optimization"""
        if not text.strip():
            return
        
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        caption_hash = self._generate_hash(text, speaker, timestamp)
        
        if caption_hash in self.processed_captions:
            return
        
        caption_data = {
            'speaker': speaker,
            'text': text.strip(),
            'timestamp': timestamp,
            'hash': caption_hash
        }
        
        self.processed_captions[caption_hash] = caption_data
        self.conversation_buffer.append(caption_data)
        self.current_chunk.append(caption_data)
        
        self.chunk_word_count += len(text.split())
        self.last_caption_time = datetime.now(timezone.utc)
        
        logger.info(f"📝 RAPID: {speaker}: {text[:50]}... (Chunk: {self.chunk_word_count} words)")
        
        # RAPID MODE: More aggressive chunking for real-time RAG
        should_chunk = False
        time_elapsed = (datetime.now(timezone.utc) - self.chunk_start_time).seconds
        
        # Force chunk on time threshold (highest priority for real-time)
        if time_elapsed >= self.max_chunk_seconds:
            logger.info(f"⚡ RAPID: Time threshold reached ({time_elapsed}s) - FORCE UPLOAD")
            should_chunk = True
        
        # Chunk on minimum words + complete sentence (faster than waiting for more)
        elif self._is_complete_sentence(text) and self.chunk_word_count >= self.min_chunk_words:
            logger.info(f"⚡ RAPID: Semantic boundary + min words ({self.chunk_word_count}) - UPLOAD NOW")
            should_chunk = True
        
        # Chunk on incomplete sentence timeout (much shorter)
        elif time_elapsed >= self.incomplete_sentence_timeout and self.current_chunk:
            logger.info(f"⚡ RAPID: Incomplete timeout ({time_elapsed}s) - UPLOAD PARTIAL")
            should_chunk = True
        
        # Emergency chunk on max words
        elif self.chunk_word_count >= self.max_chunk_words:
            logger.info(f"⚡ RAPID: Max words reached ({self.chunk_word_count}) - EMERGENCY UPLOAD")
            should_chunk = True
        
        if should_chunk and len(self.current_chunk) > 0:
            conversation_age = (datetime.now(timezone.utc) - dateutil_parser.parse(self.current_chunk[0]['timestamp'])).total_seconds()
            logger.info(f"🚀 RAPID UPLOAD: {conversation_age:.1f}s from first caption to upload")
            self._create_and_upload_chunk()
    
    def _create_and_upload_chunk(self):
        """Create a chunk from current buffer and upload to Pinecone"""
        if not self.current_chunk:
            logger.info("⚠ No captions in current chunk")
            return
        
        logger.info(f"📦 Creating chunk with {len(self.current_chunk)} captions")
        
        chunk_id = self._generate_chunk_id()
        chunk_text = self._format_conversation_chunk(self.current_chunk, chunk_id)
        
        logger.info(f"📝 Formatted chunk text ({len(chunk_text)} chars):")
        logger.info(f"{chunk_text[:200]}...")
        
        self._upload_to_pinecone(chunk_text, self.current_chunk, chunk_id)
        
        # Reset for next chunk
        self.current_chunk = []
        self.chunk_word_count = 0
        self.chunk_start_time = datetime.now(timezone.utc)
        logger.info("✓ Chunk processing complete, ready for next chunk")
    
    def finalize(self):
        """Upload any remaining captions"""
        logger.info(f"🏁 Finalizing caption processor...")
        if self.current_chunk:
            logger.info(f"📦 Processing final chunk with {len(self.current_chunk)} captions")
            self._create_and_upload_chunk()
        else:
            logger.info("✓ No remaining captions to process")
        
        logger.info(f"✅ Finalized caption processing for meeting {self.meeting_id} with {self.chunk_counter} chunks")

# Updated Caption Capture Class
class CaptionCapture:
    def __init__(self, driver, processor: CaptionProcessor):
        self.driver = driver
        self.processor = processor
        self.running = False
        self.capture_thread = None
        # Track all seen captions with their full text to detect updates
        self.speaker_last_text = {}  # speaker -> last complete text we processed
        self.speaker_current_text = {}  # speaker -> current text in the UI
        self.processed_captions = set()  # Track processed caption hashes to avoid duplicates

    def start_capture(self):
        """Start capturing captions in a loop"""
        self.running = True
        logger.info("🎤 Started caption capture")
        
        # Wait for captions to be available before starting
        caption_container = None
        for attempt in range(30):  # Try for 30 seconds
            try:
                caption_container = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "div[aria-label='Captions']"
                )
                logger.info("✓ Found caption container")
                break
            except NoSuchElementException:
                logger.debug(f"Caption container not found, attempt {attempt + 1}/30")
                time.sleep(1)
        
        if not caption_container:
            logger.error("❌ Caption container not found after 30 seconds")
            self.running = False
            return
        
        while self.running:
            try:
                # Find the captions container using aria-label
                container = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "div[aria-label='Captions']"
                )
                
                # Get all caption segments
                segments = container.find_elements(
                    By.CSS_SELECTOR, 
                    "div.nMcdL.bj4p3b"
                )
                
                # Process all visible segments to catch updates
                current_speakers = set()
                
                for segment in segments:
                    try:
                        # Extract speaker name
                        speaker_elem = segment.find_element(
                            By.CSS_SELECTOR, 
                            "span.NWpY1d"
                        )
                        speaker = speaker_elem.text.strip()
                        
                        # Extract caption text
                        text_elem = segment.find_element(
                            By.CSS_SELECTOR, 
                            "div.ygicle.VbkSUe"
                        )
                        text = text_elem.text.strip()
                        
                        if speaker and text:
                            current_speakers.add(speaker)
                            self._process_caption_update(speaker, text)
                            
                    except Exception as e:
                        logger.debug(f"Skipping segment: {e}")
                        continue
                
                # Check for speakers that are no longer visible (finished speaking)
                finished_speakers = set(self.speaker_current_text.keys()) - current_speakers
                for speaker in finished_speakers:
                    if speaker in self.speaker_current_text:
                        final_text = self.speaker_current_text[speaker]
                        logger.info(f"🎯 Speaker {speaker} finished, processing final text: {final_text[:50]}...")
                        self._finalize_speaker_caption(speaker, final_text)
                
                time.sleep(0.2)  # Even faster checking for real-time response
                
            except NoSuchElementException:
                logger.debug("Caption container temporarily not found")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in caption capture: {e}")
                time.sleep(1)

    def _process_caption_update(self, speaker: str, current_text: str):
        """Process caption updates for a speaker with improved duplicate detection"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Get previous text for this speaker
        previous_text = self.speaker_current_text.get(speaker, "")
        
        # Skip if text hasn't changed at all
        if current_text == previous_text:
            return
            
        # Update current text for this speaker
        self.speaker_current_text[speaker] = current_text
        
        # Create a unique hash for this exact text to prevent duplicates
        text_hash = hashlib.md5(f"{speaker}:{current_text}".encode()).hexdigest()
        
        # Skip if we've already processed this exact text for this speaker
        if text_hash in self.processed_captions:
            logger.debug(f"🔄 Skipping duplicate text for {speaker}: {current_text[:50]}...")
            return
        
        logger.debug(f"📝 Caption update for {speaker}: '{previous_text[:30]}...' -> '{current_text[:30]}...'")
        
        # Check if this is a significant update worth processing
        should_process = False
        
        # Process if it's a complete sentence and we haven't seen this exact text
        if self._is_sentence_complete(current_text):
            logger.info(f"✅ Complete sentence detected for {speaker}: {current_text[:50]}...")
            should_process = True
            
        # Process if the text got significantly longer (substantial addition)
        elif len(current_text) > len(previous_text) + 15:  # At least 15 more characters
            # Check if we have a sentence boundary in the addition
            added_text = current_text[len(previous_text):]
            if any(punct in added_text for punct in ['.', '!', '?']):
                logger.info(f"🔄 Sentence boundary found in update for {speaker}: {current_text[:50]}...")
                should_process = True
        
        # Only process if we determined it's worth processing AND we haven't seen this text
        if should_process:
            self._process_complete_caption(speaker, current_text, timestamp)

    def _is_sentence_complete(self, text: str) -> bool:
        """Check if text appears to be a complete sentence"""
        text = text.strip()
        if not text:
            return False
            
        # Check for ending punctuation
        if text.endswith(('.', '!', '?', '。', '？', '！')):
            return True
            
        # Check for reasonable length (likely complete thought)
        if len(text.split()) >= 8:  # 8 or more words suggests completeness
            return True
            
        return False

    def _process_complete_caption(self, speaker: str, text: str, timestamp: str):
        """Process a complete caption with enhanced duplicate prevention"""
        # Create a comprehensive hash to avoid processing the same caption twice
        caption_hash = hashlib.md5(f"{speaker}:{text.strip()}".encode()).hexdigest()
        
        # Check if we've already processed this exact caption
        if caption_hash in self.processed_captions:
            logger.debug(f"🚫 Skipping duplicate caption for {speaker}: {text[:50]}...")
            return
        
        # Mark this caption as processed
        self.processed_captions.add(caption_hash)
        
        # Update our tracking
        self.speaker_last_text[speaker] = text
        
        # Send to processor
        logger.info(f"🎯 Processing NEW caption for {speaker}: {text[:100]}...")
        self.processor.process_caption(speaker, text, timestamp)

    def _finalize_speaker_caption(self, speaker: str, final_text: str):
        """Finalize caption when speaker is no longer visible"""
        # Create hash for final caption
        text_hash = hashlib.md5(f"{speaker}:{final_text.strip()}".encode()).hexdigest()
        
        # Only process if we haven't seen this exact text AND it's different from last processed
        if (text_hash not in self.processed_captions and 
            final_text.strip() != self.speaker_last_text.get(speaker, "").strip() and
            final_text.strip()):
            
            timestamp = datetime.now(timezone.utc).isoformat()
            self.processed_captions.add(text_hash)
            self.speaker_last_text[speaker] = final_text
            
            logger.info(f"🏁 Final NEW caption for {speaker}: {final_text[:50]}...")
            self.processor.process_caption(speaker, final_text, timestamp)
        else:
            logger.debug(f"🚫 Skipping duplicate final caption for {speaker}: {final_text[:50]}...")
        
        # Clean up tracking for this speaker
        self.speaker_current_text.pop(speaker, None)

    def stop_capture(self):
        """Stop capturing captions"""
        self.running = False
        
        # Process any remaining captions from speakers still visible
        for speaker, text in self.speaker_current_text.items():
            if text and text != self.speaker_last_text.get(speaker, ""):
                logger.info(f"🏁 Processing remaining caption for {speaker}: {text}")
                timestamp = datetime.now(timezone.utc).isoformat()
                self.processor.process_caption(speaker, text, timestamp)
        
        self.processor.finalize()
        logger.info("🛑 Stopped caption capture")

        
# Google Meet Bot Class
class GoogleMeetBot:
    def __init__(self, driver):
        self.driver = driver
        self.caption_capture = None
        self.caption_processor = None
        self.capture_thread = None

    def join_meeting(self, meet_link, guest_name="Guest User"):
        logger.info(f"📍 Joining Meeting: {meet_link}")
        logger.info(f"👤 Guest name: {guest_name}")
        try:
            self.driver.get(meet_link)
            wait = WebDriverWait(self.driver, 30)
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Handle "Continue without microphone" if present
            try:
                span = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//span[text()='Continue without microphone and camera']")
                ))
                button = span.find_element(By.XPATH, "./ancestor::button")
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("✓ Clicked 'Continue without microphone and camera'")
                time.sleep(1)
            except TimeoutException:
                logger.info("ℹ 'Continue without microphone and camera' not needed")

            # Dismiss Google sign-in suggestion if present
            try:
                got_it_button = self.driver.find_element(By.XPATH, "//button[contains(text(),'Got it')]")
                self.driver.execute_script("arguments[0].click();", got_it_button)
                logger.info("✓ Dismissed Google sign-in suggestion")
                time.sleep(2)
            except:
                pass

            # Enter guest name - try multiple selectors
            name_input = None
            name_selectors = [
                "//input[@placeholder='Your name']",
                "//input[@aria-label='Your name']",
                "//input[contains(@class, 'whsOnd')]",
                "//input[@type='text']"
            ]
            
            for selector in name_selectors:
                try:
                    name_input = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    logger.info(f"✓ Found name input with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not name_input:
                logger.error("❌ Name input not found with any selector")
                self.driver.save_screenshot("meet_error_screenshot.png")
                logger.info("Screenshot saved as meet_error_screenshot.png")
                return False
            
            # Clear and enter name with JavaScript as backup
            try:
                name_input.click()
                time.sleep(0.5)
                name_input.clear()
            except:
                logger.info("Using JavaScript to clear input field")
                self.driver.execute_script("arguments[0].value = '';", name_input)
                self.driver.execute_script("arguments[0].focus();", name_input)
            
            # Enter name character by character
            for char in guest_name:
                try:
                    name_input.send_keys(char)
                except:
                    self.driver.execute_script("arguments[0].value += arguments[1];", name_input, char)
                time.sleep(random.uniform(0.05, 0.15))
            
            logger.info(f"✓ Entered name: {guest_name}")

            time.sleep(2)
            
            # Turn off microphone
            try:
                mic_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='microphone' i], button[aria-label*='mic' i]")
                for mic_button in mic_buttons:
                    try:
                        aria_label = mic_button.get_attribute("aria-label")
                        if aria_label and ("Turn off" in aria_label or "turn off" in aria_label):
                            self.driver.execute_script("arguments[0].click();", mic_button)
                            logger.info("✓ Muted microphone")
                            break
                    except:
                        continue
            except:
                logger.warning("⚠ Microphone button not found or already muted")

            # Turn off camera
            try:
                camera_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='camera' i], button[aria-label*='video' i]")
                for camera_button in camera_buttons:
                    try:
                        aria_label = camera_button.get_attribute("aria-label")
                        if aria_label and ("Turn off" in aria_label or "turn off" in aria_label):
                            self.driver.execute_script("arguments[0].click();", camera_button)
                            logger.info("✓ Turned off camera")
                            break
                    except:
                        continue
            except:
                logger.warning("⚠ Camera button not found or already off")

            # Click "Ask to join" - improved reliability
            attempts = 0
            max_attempts = 15
            join_clicked = False
            
            while attempts < max_attempts and not join_clicked:
                try:
                    join_selectors = [
                        "//button[.//span[text()='Ask to join']]",
                        "//button[.//span[contains(text(),'Ask to join')]]",
                        "//button[contains(@aria-label,'Ask to join')]",
                        "//button[contains(text(),'Ask to join')]"
                    ]
                    
                    for selector in join_selectors:
                        try:
                            buttons = self.driver.find_elements(By.XPATH, selector)
                            for button in buttons:
                                if button.is_displayed() and button.is_enabled():
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                    time.sleep(0.5)
                                    self.driver.execute_script("arguments[0].click();", button)
                                    logger.info("✅ Successfully clicked 'Ask to join'")
                                    join_clicked = True
                                    break
                        except:
                            continue
                        if join_clicked:
                            break
                    
                    if not join_clicked:
                        time.sleep(2)
                        attempts += 1
                        logger.info(f"Waiting for join button... attempt {attempts}/{max_attempts}")
                except Exception as e:
                    logger.debug(f"Join button attempt {attempts} failed: {e}")
                    time.sleep(2)
                    attempts += 1
                    
            if not join_clicked:
                logger.error("❌ Could not find or click join button")
                self.driver.save_screenshot("join_button_error.png")
                logger.info("Screenshot saved as join_button_error.png")
                return False

            # Wait a bit for meeting to load
            time.sleep(5)

            # Enable captions - with better error handling
            caption_attempts = 0
            captions_enabled = False
            
            while caption_attempts < 5 and not captions_enabled:  # Increased attempts
                try:
                    # Try multiple caption button selectors
                    caption_selectors = [
                        "//button[@aria-label='Turn on captions' or @aria-label='Turn on captions (c)']",
                        "//button[contains(@aria-label, 'captions')]",
                        "//button[contains(@aria-label, 'Captions')]",
                        "//button[@data-tooltip='Turn on captions']"
                    ]
                    
                    cc_button = None
                    for selector in caption_selectors:
                        try:
                            cc_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            break
                        except TimeoutException:
                            continue
                    
                    if cc_button:
                        self.driver.execute_script("arguments[0].click();", cc_button)
                        logger.info("✓ Captions enabled")
                        captions_enabled = True
                        break
                    else:
                        logger.warning(f"Caption button not found, attempt {caption_attempts + 1}/5")
                        
                except Exception as e:
                    logger.debug(f"Caption attempt {caption_attempts + 1} failed: {e}")
                
                caption_attempts += 1
                time.sleep(3)
                

            if not captions_enabled:
                logger.warning("⚠ Could not enable captions - continuing anyway")
                # enabling caption with c key
                try:
                    #human like delay
                    time.sleep(1)
                    #press 'esc' to close any popups
                    self.driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
                    self.driver.find_element(By.CSS_SELECTOR, "body").send_keys("c")
                    logger.info("✓ Captions enabled with 'c' key")
                    captions_enabled = True
                except Exception as e:
                    logger.error(f"❌ Failed to enable captions with 'c' key: {e}")

            


            # Wait for captions to be available
            logger.info("⏳ Waiting for caption elements to load...")
            caption_loaded = False
            for attempt in range(15):  # Try for 30 seconds
                try:
                    caption_container = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label='Captions']")
                    if caption_container.is_displayed():
                        caption_loaded = True
                        logger.info("✓ Caption container found and visible")
                        break
                except:
                    pass
                logger.debug(f"Waiting for captions... attempt {attempt + 1}/15")
                time.sleep(2)
            
            if not caption_loaded:
                logger.warning("⚠ Caption container not found - captions may not work")
            
            return True, captions_enabled

        except Exception as e:
            logger.error(f"❌ Error joining meeting: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def start_caption_capture(self, meeting_id: str, user_id: str):
        """Start capturing captions"""
        try:
            self.caption_processor = CaptionProcessor(meeting_id, user_id)
            self.caption_capture = CaptionCapture(self.driver, self.caption_processor)
            
            # Start capture in a separate thread
            self.capture_thread = threading.Thread(
                target=self.caption_capture.start_capture,
                daemon=True
            )
            self.capture_thread.start()
            logger.info("✓ Caption capture started")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start caption capture: {e}")
            return False
    
    def stop_caption_capture(self):
        """Stop capturing captions"""
        try:
            if self.caption_capture:
                self.caption_capture.stop_capture()
                logger.info("✓ Caption capture stopped")
                
            # Wait for capture thread to finish
            if self.capture_thread and self.capture_thread.is_alive():
                logger.info("Waiting for caption capture thread to finish...")
                self.capture_thread.join(timeout=5)
                if self.capture_thread.is_alive():
                    logger.warning("Caption capture thread did not finish cleanly")
                    
        except Exception as e:
            logger.error(f"❌ Error stopping caption capture: {e}")
    
    def leave_meeting(self):
        """Leave meeting and stop caption capture"""
        self.stop_caption_capture()
        
        try:
            leave_selectors = [
                "//button[@aria-label='Leave call']",
                "//button[contains(@aria-label, 'Leave')]",
                "//button[contains(@aria-label, 'leave')]",
                "//button[contains(@class, 'leave')]"
            ]
            
            for selector in leave_selectors:
                try:
                    leave_button = self.driver.find_element(By.XPATH, selector)
                    if leave_button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", leave_button)
                        logger.info("✓ Successfully left the meeting")
                        time.sleep(1)
                        return
                except:
                    continue
                    
            logger.warning("⚠ Could not find leave button, closing browser")
        except Exception as e:
            logger.error(f"❌ Error leaving meeting: {e}")

# Database Manager Class
class DatabaseManager:
    def __init__(self, mongo_url, db_name):
        self.client = MongoClient(mongo_url)
        try:
            self.client.server_info()
            self.db = self.client[db_name]
            self.meetings = self.db['meetings']
            logger.info(f"✓ Connected to MongoDB database: {db_name}")
        except ConnectionError as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error during MongoDB connection: {e}")
            raise

    def get_upcoming_meetings(self, now):
        """Fetch meetings starting within the next 24 hours or recently created."""
        next_window = now + timedelta(hours=24)
        recent_threshold = now - timedelta(seconds=30)
        
        meetings = self.meetings.find({
            "$or": [
                {
                    "start_time": {"$gte": now, "$lt": next_window},
                    "bot_started": {"$ne": True}
                },
                {
                    "created_at": {"$gte": recent_threshold},
                    "start_time": {"$gte": now, "$lt": next_window},
                    "bot_started": {"$ne": True}
                }
            ],
            "meeting_link": {"$ne": None}
        }).sort("start_time")
        
        logger.info(f"Querying meetings from {now} (UTC) to {next_window} (UTC)")
        
        upcoming_meetings = []
        for meeting in meetings:
            start_time = parse_datetime_with_tz(meeting['start_time'], assume_local_if_naive=ASSUME_DB_TIMES_ARE_LOCAL)
            local_start_time = start_time.astimezone(LOCAL_TZ)
            
            logger.info(f"Found meeting: {meeting.get('title', 'No title')} at {start_time} UTC / {local_start_time} local")
            upcoming_meetings.append(meeting)
            
        if not upcoming_meetings:
            logger.info("No upcoming meetings found")
        return upcoming_meetings

    def mark_bot_started(self, meeting_id):
        result = self.meetings.update_one({'_id': meeting_id}, {'$set': {'bot_started': True}})
        if result.modified_count > 0:
            logger.info(f"✓ Marked meeting {meeting_id} as bot_started")
        else:
            logger.warning(f"⚠ No update for meeting {meeting_id}")

# Helper function to parse datetime with timezone
def parse_datetime_with_tz(dt, assume_local_if_naive=True):
    if isinstance(dt, str):
        parsed_dt = dateutil_parser.parse(dt)
    else:
        parsed_dt = dt
    
    if parsed_dt.tzinfo is None:
        if assume_local_if_naive:
            logger.warning(f"No timezone info for datetime {dt}, assuming LOCAL time (Asia/Dhaka)")
            parsed_dt = LOCAL_TZ.localize(parsed_dt)
        else:
            logger.warning(f"No timezone info for datetime {dt}, assuming UTC")
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
    else:
        if parsed_dt.tzinfo == timezone.utc:
            local_now = datetime.now()
            utc_now = datetime.now(timezone.utc)
            
            time_diff_if_utc = abs((parsed_dt - utc_now).total_seconds())
            time_diff_if_local = abs((parsed_dt.replace(tzinfo=None) - local_now).total_seconds())
            
            if time_diff_if_local < time_diff_if_utc and time_diff_if_local < 3600:
                logger.warning(f"Time {dt} marked as UTC but appears to be local time, correcting...")
                parsed_dt = parsed_dt.replace(tzinfo=None)
                parsed_dt = LOCAL_TZ.localize(parsed_dt)
    
    return parsed_dt

# Meeting Bot Factory Function
def run_meeting_bot(meeting):
    driver = None
    try:
        driver = setup_undetected_chrome()
        if driver is None:
            logger.error(f"❌ Failed to initialize driver for meeting {meeting.get('title', 'No title')}")
            return
        
        bot = GoogleMeetBot(driver)
        meet_link = meeting['meeting_link']
        user_id = meeting['user_id']
        guest_name = f"Bot for {user_id}"

        start_time = parse_datetime_with_tz(meeting['start_time'], assume_local_if_naive=ASSUME_DB_TIMES_ARE_LOCAL)
        end_time = parse_datetime_with_tz(meeting['end_time'], assume_local_if_naive=ASSUME_DB_TIMES_ARE_LOCAL)
        
        now = datetime.now(timezone.utc)
        local_now = now.astimezone(LOCAL_TZ)
        local_start = start_time.astimezone(LOCAL_TZ)
        local_end = end_time.astimezone(LOCAL_TZ)
        
        logger.info(f"Starting bot for meeting '{meeting.get('title', 'No title')}'")
        logger.info(f"Current time: {now} UTC / {local_now} local")
        logger.info(f"Meeting start: {start_time} UTC / {local_start} local")
        logger.info(f"Meeting end: {end_time} UTC / {local_end} local")
        
        if now < start_time:
            wait_time = (start_time - now).total_seconds()
            logger.info(f"Waiting {wait_time:.1f} seconds ({wait_time/60:.1f} minutes) until start time")
            time.sleep(wait_time)
        else:
            logger.warning("Meeting start time is in the past, joining immediately")

        success = bot.join_meeting(meet_link, guest_name)
        if success:
            logger.info(f"✓ Successfully joined meeting '{meeting.get('title', 'No title')}'")
            
            caption_success = bot.start_caption_capture(
                meeting_id=str(meeting['_id']),
                user_id=user_id
            )
            
            if caption_success:
                logger.info("✓ Caption capture initialized")
            else:
                logger.warning("⚠ Caption capture failed to initialize, continuing without captions")
            
            # Stay in meeting until end time
            while datetime.now(timezone.utc) < end_time:
                remaining = (end_time - datetime.now(timezone.utc)).total_seconds()
                if remaining <= 0:
                    break
                
                sleep_time = min(60, remaining)  # Check every minute or remaining time
                logger.info(f"Remaining in meeting for {remaining/60:.1f} more minutes")
                time.sleep(sleep_time)
                
            logger.info("Meeting time ended, leaving...")
            bot.leave_meeting()
        else:
            logger.error(f"❌ Failed to join meeting '{meeting.get('title', 'No title')}'")
        
    except Exception as e:
        logger.error(f"❌ Error in bot process for meeting '{meeting.get('title', 'No title')}': {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Ensure driver cleanup
        if driver:
            try:
                global active_drivers
                with cleanup_lock:
                    if driver in active_drivers:
                        active_drivers.remove(driver)
                driver.quit()
                logger.info("✓ Driver cleaned up successfully")
            except Exception as e:
                logger.debug(f"Driver cleanup error: {e}")
        
        logger.info(f"✓ Bot for meeting '{meeting.get('title', 'No title')}' completed")

# Main Workflow
def main():
    try:
        db_manager = DatabaseManager(MONGODB_URL, DATABASE_NAME)
        logger.info("✓ Starting meeting bot scheduler...")
        logger.info(f"Local timezone: {LOCAL_TZ}")
        
        while True:
            try:
                now = datetime.now(timezone.utc)
                local_now = now.astimezone(LOCAL_TZ)
                logger.info(f"\n--- Checking for upcoming meetings at {now} UTC / {local_now} local ---")
                
                meetings = db_manager.get_upcoming_meetings(now)
                if meetings:
                    for meeting in meetings:
                        logger.info(f"✓ Scheduling bot for meeting '{meeting.get('title', 'No title')}'")
                        
                        p = Process(target=run_meeting_bot, args=(meeting,))
                        p.start()
                        
                        db_manager.mark_bot_started(meeting['_id'])
                else:
                    logger.info("No upcoming meetings found")
                    
                logger.info("Sleeping for 60 seconds before next check...")
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                import traceback
                logger.error(traceback.format_exc())
                time.sleep(60)
                
    except Exception as e:
        logger.error(f"❌ Scheduler failed to start: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()