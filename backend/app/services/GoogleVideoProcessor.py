# #101
# import os
# import time
# from google.cloud import videointelligence
# from google.cloud import storage
# from google.api_core.exceptions import GoogleAPICallError
# import logging
# import tempfile
# from langchain.text_splitter import (
#     RecursiveCharacterTextSplitter,
#     MarkdownTextSplitter
# )
# from langchain.schema import Document

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\projects\CSE299\cortana\cortana\backend\youtube-api-461010-dbd270bbfb03.json"

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class GoogleVideoProcessor:
#     def __init__(self, gcs_bucket_name: str = None):
#         """
#         Initialize Google Video Intelligence API processor
        
#         Args:
#             gcs_bucket_name: Google Cloud Storage bucket name for video uploads
#         """
#         self.client = videointelligence.VideoIntelligenceServiceClient()
#         self.storage_client = storage.Client()
#         self.gcs_bucket_name = gcs_bucket_name or os.getenv("GCS_BUCKET_NAME")
        
#         if not self.gcs_bucket_name:
#             logger.warning("GCS bucket not specified. Videos must be under 10MB for direct processing.")

#     def process_video(self, video_path: str, features: list = None) -> list:
#         """Process video and return list of Document objects"""
#         """
#         Process video using Google Video Intelligence API
        
#         Args:
#             video_path: Path to local video file or GCS URI (gs://...)
#             features: List of features to analyze (default: all available)
            
#         Returns:
#             Analysis results dictionary
#         """
#         # Determine if we're using local file or GCS URI
#         if video_path.startswith("gs://"):
#             input_uri = video_path
#         else:
#             # Check file size
#             file_size = os.path.getsize(video_path) / (1024 * 1024)  # in MB
#             if file_size > 10 and not self.gcs_bucket_name:
#                 raise ValueError("Videos over 10MB require GCS bucket for processing")
                
#             input_uri = self._upload_to_gcs(video_path) if self.gcs_bucket_name else None
            
#             # For small videos (<10MB), we can use direct content upload
#             if not input_uri:
#                 return self._process_direct_content(video_path, features)
            
#         # Configure features
#         if not features:
#             features = [
#                 videointelligence.Feature.SPEECH_TRANSCRIPTION,
#                 videointelligence.Feature.LABEL_DETECTION,
#                 videointelligence.Feature.TEXT_DETECTION,
#                 videointelligence.Feature.SHOT_CHANGE_DETECTION
#             ]
        
#         # Configure speech transcription
#         speech_config = videointelligence.SpeechTranscriptionConfig(
#             language_code="en-US",
#             enable_automatic_punctuation=True,
#         )
        
#         # Configure video context
#         video_context = videointelligence.VideoContext(
#             speech_transcription_config=speech_config
#         )
#         # ... (existing processing logic)
#            # Start asynchronous processing
#         operation = self.client.annotate_video(
#             request={
#                 "features": features,
#                 "input_uri": input_uri,
#                 "video_context": video_context,
#             }
#         )
        
#         result = operation.result(timeout=600)
#         return self._parse_results(result, input_uri or video_path)
    
#     def _parse_results(self, result, source: str) -> list:
#         """Parse API results into list of Document objects with chunking"""
#         documents = []
#         annotation_result = result.annotation_results[0] if result.annotation_results else None
        
#         # 1. Enhanced transcript processing with chunking
#         transcript_chunks = []
#         if annotation_result:
#             # Extract transcript segments with timing information
#             transcript_segments = []
#             for speech in annotation_result.speech_transcriptions:
#                 for alt in speech.alternatives:
#                     transcript_segments.append({
#                         "text": alt.transcript,
#                         "start": alt.words[0].start_time.total_seconds() if alt.words else 0,
#                         "end": alt.words[-1].end_time.total_seconds() if alt.words else 0
#                     })
            
#             # Chunk transcript while preserving timing info
#             transcript_chunks = self._chunk_transcript(transcript_segments)

#         # 2. Enhanced label detection with confidence
#         labels = {}
#         if annotation_result:
#             for segment_label in annotation_result.segment_label_annotations:
#                 label = segment_label.entity.description
#                 confidence = max(segment.confidence for segment in segment_label.segments)
#                 labels[label] = confidence

#         # 3. Enhanced scene detection
#         scenes = []
#         if annotation_result:
#             for i, shot in enumerate(annotation_result.shot_annotations):
#                 scenes.append({
#                     "id": i,
#                     "start": shot.start_time_offset.total_seconds(),
#                     "end": shot.end_time_offset.total_seconds()
#                 })

#         # 4. Enhanced text detection
#         detected_texts = []
#         if annotation_result:
#             for text_annotation in annotation_result.text_annotations:
#                 detected_texts.append(text_annotation.text)

#         # Create documents
#         # Document 1: Transcript chunks
#         for i, chunk in enumerate(transcript_chunks):
#             metadata = {
#                 "source": source,
#                 "chunk_index": i,
#                 "total_chunks": len(transcript_chunks),
#                 "start_time": chunk["start"],
#                 "end_time": chunk["end"],
#                 "doc_type": "transcript_chunk"
#             }
#             documents.append(Document(
#                 page_content=chunk["text"],
#                 metadata=metadata
#             ))
        
#         # Document 2: Video metadata summary
#         metadata_doc = {
#             "transcript_chunks": len(transcript_chunks),
#             "scenes": scenes,
#             "labels": labels,
#             "detected_texts": detected_texts,
#             "source": source,
#             "doc_type": "video_metadata"
#         }
#         documents.append(Document(
#             page_content=self._generate_metadata_summary(metadata_doc),
#             metadata={"source": source, "doc_type": "video_metadata"}
#         ))
        
#         return documents
    
#     def _chunk_transcript(self, segments: list) -> list:
#         """Chunk transcript while preserving timing information"""
#         # First combine all text
#         full_text = " ".join(seg["text"] for seg in segments)
        
#         # Split with overlap
#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len
#         )
#         chunks = splitter.split_text(full_text)
        
#         # Map chunks to original timing info
#         chunked_segments = []
#         current_index = 0
        
#         for chunk in chunks:
#             # Find original segments that correspond to this chunk
#             chunk_text = ""
#             chunk_start = None
#             chunk_end = None
            
#             while current_index < len(segments) and len(chunk_text) < len(chunk):
#                 seg = segments[current_index]
#                 seg_text = seg["text"]
                
#                 if not chunk_start:
#                     chunk_start = seg["start"]
                
#                 # Calculate how much of this segment we need
#                 needed_length = len(chunk) - len(chunk_text)
#                 take_text = seg_text[:needed_length]
                
#                 chunk_text += take_text + " "
#                 chunk_end = seg["end"]
                
#                 # If we didn't use full segment, break and keep for next chunk
#                 if len(take_text) < len(seg_text):
#                     segments[current_index]["text"] = seg_text[len(take_text):]
#                     break
#                 else:
#                     current_index += 1
            
#             chunked_segments.append({
#                 "text": chunk_text.strip(),
#                 "start": chunk_start,
#                 "end": chunk_end
#             })
        
#         return chunked_segments
    
#     def _generate_metadata_summary(self, metadata: dict) -> str:
#         """Generate summary text for video metadata"""
#         summary = [
#             "VIDEO ANALYSIS METADATA:",
#             f"Source: {metadata['source']}",
#             f"Total transcript chunks: {metadata['transcript_chunks']}",
#             f"Scenes detected: {len(metadata['scenes'])}",
#             f"Labels identified: {len(metadata['labels'])}",
#             f"Text elements found: {len(metadata['detected_texts'])}",
#             "",
#             "TOP LABELS:"
#         ]
        
#         # Add top 5 labels by confidence
#         sorted_labels = sorted(metadata["labels"].items(), key=lambda x: x[1], reverse=True)[:5]
#         for label, conf in sorted_labels:
#             summary.append(f"- {label} ({conf:.2%})")
        
#         # Add detected texts
#         summary.append("\nDETECTED TEXTS:")
#         for text in metadata["detected_texts"][:10]:  # First 10 only
#             summary.append(f"- {text}")
            
#         return "\n".join(summary)



#     def _process_direct_content(self, video_path: str, features: list) -> dict:
#         """Process small video by uploading content directly"""
#         with open(video_path, "rb") as f:
#             video_content = f.read()
        
#         # Configure features
#         if not features:
#             features = [
#                 videointelligence.Feature.SPEECH_TRANSCRIPTION,
#                 videointelligence.Feature.LABEL_DETECTION
#             ]
        
#         # Configure speech transcription
#         speech_config = videointelligence.SpeechTranscriptionConfig(
#             language_code="en-US",
#             enable_automatic_punctuation=True,
#         )
        
#         # Configure video context
#         video_context = videointelligence.VideoContext(
#             speech_transcription_config=speech_config
#         )
        
#         # Start processing
#         operation = self.client.annotate_video(
#             request={
#                 "features": features,
#                 "input_content": video_content,
#                 "video_context": video_context,
#             }
#         )
        
#         logger.info(f"Processing video content directly: {video_path}")
#         result = operation.result(timeout=600)
        
#         return self._parse_results(result, video_path)

#     def _parse_results(self, result, source: str) -> dict:
#         """Parse API results into structured format"""
#         analysis = {
#             "transcript": "",
#             "labels": {},
#             "text": [],
#             "scenes": 0,
#             "metadata": {"source": source}
#         }
        
#         if not result.annotation_results:
#             return analysis
            
#         annotation_result = result.annotation_results[0]
        
#         # 1. Speech transcription
#         for speech_transcription in annotation_result.speech_transcriptions:
#             for alternative in speech_transcription.alternatives:
#                 analysis["transcript"] += alternative.transcript + " "
#         analysis["transcript"] = analysis["transcript"].strip()
        
#         # 2. Label detection
#         for segment_label in annotation_result.segment_label_annotations:
#             label = segment_label.entity.description
#             confidence = max(segment.confidence for segment in segment_label.segments)
#             analysis["labels"][label] = confidence
        
#         # 3. Text detection
#         for text_annotation in annotation_result.text_annotations:
#             analysis["text"].append(text_annotation.text)
        
#         # 4. Scene detection
#         analysis["scenes"] = len(annotation_result.shot_annotations)
        
#         return analysis

#     def _upload_to_gcs(self, local_path: str) -> str:
#         """Upload local video to Google Cloud Storage"""
#         try:
#             bucket = self.storage_client.bucket(self.gcs_bucket_name)
#             blob = bucket.blob(os.path.basename(local_path))
            
#             blob.upload_from_filename(local_path)
            
#             gcs_uri = f"gs://{self.gcs_bucket_name}/{blob.name}"
#             logger.info(f"Uploaded to GCS: {gcs_uri}")
#             return gcs_uri
            
#         except Exception as e:
#             logger.error(f"GCS upload failed: {str(e)}")
#             raise

#     def get_video_summary(self, analysis: dict) -> str:
#         """Generate text summary from analysis results"""
#         summary = [
#             "VIDEO ANALYSIS SUMMARY:",
#             f"Source: {analysis['metadata']['source']}",
#             f"Scenes detected: {analysis['scenes']}",
#             f"Labels identified: {len(analysis['labels'])}",
#             f"Text elements found: {len(analysis['text'])}",
#             "",
#             "TRANSCRIPT:",
#             analysis["transcript"][:2000] + ("..." if len(analysis["transcript"]) > 2000 else "")
#         ]
#         return "\n".join(summary)

#     def cleanup_gcs(self, gcs_uri: str):
#         """Clean up GCS file after processing"""
#         try:
#             if gcs_uri.startswith("gs://"):
#                 path = gcs_uri[5:].split("/", 1)
#                 if len(path) > 1:
#                     bucket_name = path[0]
#                     blob_name = path[1]
#                     bucket = self.storage_client.bucket(bucket_name)
#                     blob = bucket.blob(blob_name)
#                     blob.delete()
#                     logger.info(f"Deleted GCS file: {gcs_uri}")
#         except Exception as e:
#             logger.warning(f"GCS cleanup failed: {str(e)}")

# # Example usage
# if __name__ == "__main__":
#     # Initialize processor
#     processor = GoogleVideoProcessor(gcs_bucket_name="your-bucket-name")
    
#     try:
#         # Process video
#         result = processor.process_video("example_video.mp4")
        
#         # Generate summary
#         summary = processor.get_video_summary(result)
#         print(summary)
        
#         # Clean up if we uploaded to GCS
#         if "source" in result["metadata"] and result["metadata"]["source"].startswith("gs://"):
#             processor.cleanup_gcs(result["metadata"]["source"])
            
#     except Exception as e:
#         logger.error(f"Video processing failed: {str(e)}")

# 102

# import os
# import time
# from google.cloud import videointelligence
# from google.cloud import storage
# from google.api_core.exceptions import GoogleAPICallError
# import logging
# import tempfile
# from langchain.schema import Document
# from typing import List, Dict, Optional

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load credentials from environment or fallback
# credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", r"D:\projects\CSE299\cortana\cortana\backend\youtube-api-461010-dbd270bbfb03.json")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# class GoogleVideoProcessor:
#     def __init__(self, gcs_bucket_name: str = None):
#         """
#         Initialize Google Video Intelligence API processor.
        
#         Args:
#             gcs_bucket_name: Google Cloud Storage bucket name for video uploads
#         """
#         try:
#             self.client = videointelligence.VideoIntelligenceServiceClient()
#             self.storage_client = storage.Client()
#             self.gcs_bucket_name = gcs_bucket_name or os.getenv("GCS_BUCKET_NAME")
#             if not self.gcs_bucket_name:
#                 logger.warning("GCS bucket not specified. Videos over 10MB cannot be processed. Set GCS_BUCKET_NAME environment variable.")
#         except Exception as e:
#             logger.error(f"Failed to initialize Google clients: {str(e)}")
#             raise

#     def process_video(self, video_path: str, features: list = None) -> List[Document]:
#         """
#         Process video using Google Video Intelligence API and return as Documents.
        
#         Args:
#             video_path: Path to local video file or GCS URI (gs://...)
#             features: List of features to analyze
            
#         Returns:
#             List of Document objects containing analysis results
#         """
#         # Determine processing method
#         if video_path.startswith("gs://"):
#             input_uri = video_path
#         else:
#             file_size = os.path.getsize(video_path) / (1024 * 1024)  # in MB
#             if file_size > 10 and not self.gcs_bucket_name:
#                 raise ValueError("Videos over 10MB require a GCS bucket. Set GCS_BUCKET_NAME.")
#             input_uri = self._upload_to_gcs(video_path) if self.gcs_bucket_name and file_size > 10 else None

#         # Configure features
#         if not features:
#             features = [
#                 videointelligence.Feature.SPEECH_TRANSCRIPTION,
#                 videointelligence.Feature.LABEL_DETECTION,
#                 videointelligence.Feature.TEXT_DETECTION,
#                 videointelligence.Feature.SHOT_CHANGE_DETECTION
#             ]

#         # Configure speech transcription
#         speech_config = videointelligence.SpeechTranscriptionConfig(
#             language_code="en-US",
#             enable_automatic_punctuation=True,
#         )
#         video_context = videointelligence.VideoContext(speech_transcription_config=speech_config)

#         # Process video
#         try:
#             operation = self.client.annotate_video(
#                 request={
#                     "features": features,
#                     "input_uri": input_uri or video_path,
#                     "video_context": video_context,
#                 } if input_uri else {
#                     "features": [videointelligence.Feature.SPEECH_TRANSCRIPTION, videointelligence.Feature.LABEL_DETECTION],
#                     "input_content": open(video_path, "rb").read(),
#                     "video_context": video_context,
#                 }
#             )
#             logger.info(f"Processing video: {input_uri or video_path}")
#             result = operation.result(timeout=600)
#             documents = self._parse_results_to_documents(result, input_uri or video_path)
#             if input_uri:
#                 self.cleanup_gcs(input_uri)
#             return documents
#         except GoogleAPICallError as e:
#             logger.error(f"API call failed for {video_path}: {str(e)}")
#             return [Document(page_content=f"VIDEO PROCESSING ERROR: {str(e)}", metadata={"source": video_path})]
#         except Exception as e:
#             logger.error(f"Unexpected error processing {video_path}: {str(e)}")
#             return [Document(page_content="VIDEO PROCESSING ERROR: Unexpected failure", metadata={"source": video_path})]

#     def _parse_results_to_documents(self, result, source: str) -> List[Document]:
#         """Parse API results into a list of Document objects."""
#         documents = []
#         if not result.annotation_results:
#             return [Document(page_content="No analysis results", metadata={"source": source})]

#         annotation_result = result.annotation_results[0]
        
#         # 1. Speech transcription
#         transcript = ""
#         for speech_transcription in annotation_result.speech_transcriptions:
#             for alternative in speech_transcription.alternatives:
#                 transcript += alternative.transcript + " "
#         transcript = transcript.strip() or "No transcript detected"

#         # 2. Label detection
#         labels = {label.entity.description: max(seg.confidence for seg in label.segments)
#                  for label in annotation_result.segment_label_annotations}

#         # 3. Text detection
#         text_content = "\n".join(text.text for text in annotation_result.text_annotations) or "No text detected"

#         # 4. Scene detection
#         scenes = len(annotation_result.shot_annotations)

#         # Create summary document
#         summary = (
#             f"VIDEO ANALYSIS SUMMARY:\n"
#             f"Source: {source}\n"
#             f"Scenes detected: {scenes}\n"
#             f"Labels identified: {len(labels)}\n"
#             f"Text elements found: {len(annotation_result.text_annotations)}\n\n"
#             f"TRANSCRIPT:\n{transcript[:2000]}{'...' if len(transcript) > 2000 else ''}\n\n"
#             f"TEXT DETECTION:\n{text_content}"
#         )
#         documents.append(Document(page_content=summary, metadata={"source": source, "media_type": "video"}))

#         return documents

#     def _upload_to_gcs(self, local_path: str) -> str:
#         """Upload local video to Google Cloud Storage."""
#         try:
#             if not self.gcs_bucket_name:
#                 raise ValueError("GCS bucket not configured")
#             bucket = self.storage_client.bucket(self.gcs_bucket_name)
#             blob_name = os.path.basename(local_path)
#             blob = bucket.blob(blob_name)
#             blob.upload_from_filename(local_path)
#             gcs_uri = f"gs://{self.gcs_bucket_name}/{blob_name}"
#             logger.info(f"Uploaded to GCS: {gcs_uri}")
#             return gcs_uri
#         except Exception as e:
#             logger.error(f"GCS upload failed: {str(e)}")
#             raise

#     def cleanup_gcs(self, gcs_uri: str):
#         """Clean up GCS file after processing."""
#         try:
#             if gcs_uri and gcs_uri.startswith("gs://"):
#                 bucket_name, blob_name = gcs_uri[5:].split("/", 1)
#                 bucket = self.storage_client.bucket(bucket_name)
#                 blob = bucket.blob(blob_name)
#                 blob.delete()
#                 logger.info(f"Deleted GCS file: {gcs_uri}")
#         except Exception as e:
#             logger.warning(f"GCS cleanup failed: {str(e)}")


# #102*
# import os
# import time
# from google.cloud import videointelligence
# from google.cloud import storage
# from google.api_core.exceptions import GoogleAPICallError
# import logging
# import tempfile
# from langchain.schema import Document
# from typing import List, Dict, Optional

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load credentials from environment or fallback
# credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", r"D:\projects\CSE299\cortana\cortana\backend\youtube-api-461010-dbd270bbfb03.json")
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# class GoogleVideoProcessor:
#     def __init__(self, gcs_bucket_name: str = None):
#         """Initialize Google Video Intelligence API processor."""
#         try:
#             self.client = videointelligence.VideoIntelligenceServiceClient()
#             self.storage_client = storage.Client()
#             self.gcs_bucket_name = gcs_bucket_name or os.getenv("GCS_BUCKET_NAME")
#             if not self.gcs_bucket_name:
#                 logger.warning("GCS bucket not specified. Videos over 10MB cannot be processed. Set GCS_BUCKET_NAME.")
#         except Exception as e:
#             logger.error(f"Failed to initialize Google clients: {str(e)}")
#             raise

#     def process_video(self, video_path: str, features: list = None) -> List[Document]:
#         """Process video using Google Video Intelligence API and return as Documents."""
#         if video_path.startswith("gs://"):
#             input_uri = video_path
#         else:
#             file_size = os.path.getsize(video_path) / (1024 * 1024)  # in MB
#             if file_size > 10 and not self.gcs_bucket_name:
#                 raise ValueError("Videos over 10MB require a GCS bucket. Set GCS_BUCKET_NAME.")
#             input_uri = self._upload_to_gcs(video_path) if self.gcs_bucket_name and file_size > 10 else None

#         if not features:
#             features = [
#                 videointelligence.Feature.SPEECH_TRANSCRIPTION,
#                 videointelligence.Feature.LABEL_DETECTION,
#                 videointelligence.Feature.TEXT_DETECTION,
#                 videointelligence.Feature.SHOT_CHANGE_DETECTION
#             ]

#         # Enhanced speech and video context configuration
#         speech_config = videointelligence.SpeechTranscriptionConfig(
#             language_code="en-US",  # Optimized for Fireship English
#             enable_automatic_punctuation=True,
#             enable_speaker_diarization=True,
#             audio_tracks=[0],  # Target first audio track
#             # alternative_language_codes=["en-GB", "en-AU"]  # English variants for YouTube
#         )
#         video_context = videointelligence.VideoContext(
#             speech_transcription_config=speech_config,
#             label_detection_config=videointelligence.LabelDetectionConfig(
#                 # stationarity_status=videointelligence.StationarityStatus.STATIONARY_OR_MOVING
#             ),
#             text_detection_config=videointelligence.TextDetectionConfig(
#                 language_hints=["en"]  # Hint for English text
#             )
#         )

#         try:
#             operation = self.client.annotate_video(
#                 request={
#                     "features": features,
#                     "input_uri": input_uri or video_path,
#                     "video_context": video_context,
#                 } if input_uri else {
#                     "features": [videointelligence.Feature.SPEECH_TRANSCRIPTION, videointelligence.Feature.LABEL_DETECTION],
#                     "input_content": open(video_path, "rb").read(),
#                     "video_context": video_context,
#                 }
#             )
#             logger.info(f"Processing video: {input_uri or video_path} with features: {features}")
#             result = operation.result(timeout=600)
#             documents = self._parse_results_to_documents(result, input_uri or video_path)
#             for doc in documents:
#                 doc.metadata["file_id"] = hash(video_path)
#                 doc.metadata["chunk_id"] = int(doc.metadata.get("chunk_id", 0))
#             if input_uri:
#                 self.cleanup_gcs(input_uri)
#             return documents
#         except GoogleAPICallError as e:
#             logger.error(f"API call failed for {video_path}: {str(e.details if e.details else str(e))}")
#             return [Document(page_content=f"VIDEO PROCESSING ERROR: {str(e)}", metadata={"source": video_path})]
#         except Exception as e:
#             logger.error(f"Unexpected error processing {video_path}: {str(e)}")
#             return [Document(page_content="VIDEO PROCESSING ERROR: Unexpected failure", metadata={"source": video_path})]

#     def _parse_results_to_documents(self, result, source: str) -> List[Document]:
#         documents = []
#         if not result.annotation_results:
#             return [Document(page_content="No analysis results", metadata={"source": source})]

#         annotation_result = result.annotation_results[0]
        
#         # 1. Speech transcription
#         transcript = ""
#         for speech_transcription in annotation_result.speech_transcriptions:
#             for alternative in speech_transcription.alternatives:
#                 speaker_tag = alternative.words[0].speaker_tag if alternative.words else "Unknown"
#                 transcript += f"Speaker {speaker_tag}: {alternative.transcript} " if alternative.words else alternative.transcript + " "
#         transcript = transcript.strip() or "No transcript detected (check audio language or format)"

#         # 2. Label detection
#         labels = {label.entity.description: max(seg.confidence for seg in label.segments)
#                  for label in annotation_result.segment_label_annotations}
#         label_summary = ", ".join(f"{label} ({confidence:.2f})" for label, confidence in labels.items()) or "No labels detected"

#         # 3. Text detection
#         text_content = "\n".join(text.text for text in annotation_result.text_annotations) or "No text detected"

#         # 4. Scene detection
#         scenes = len(annotation_result.shot_annotations)

#         # Create summary document
#         summary = (
#             f"VIDEO ANALYSIS SUMMARY:\n"
#             f"Source: {source}\n"
#             f"Scenes detected: {scenes}\n"
#             f"Labels identified: {label_summary}\n"
#             f"Text elements found: {len(annotation_result.text_annotations)}\n\n"
#             f"TRANSCRIPT:\n{transcript[:2000]}{'...' if len(transcript) > 2000 else ''}\n\n"
#             f"TEXT DETECTION:\n{text_content}"
#         )
#         documents.append(Document(page_content=summary, metadata={"source": source, "media_type": "video", "chunk_id": 0}))

#         return documents

#     def _upload_to_gcs(self, local_path: str) -> str:
#         """Upload local video to Google Cloud Storage."""
#         try:
#             if not self.gcs_bucket_name:
#                 raise ValueError("GCS bucket not configured")
#             bucket = self.storage_client.bucket(self.gcs_bucket_name)
#             blob_name = os.path.basename(local_path)
#             blob = bucket.blob(blob_name)
#             blob.upload_from_filename(local_path)
#             gcs_uri = f"gs://{self.gcs_bucket_name}/{blob_name}"
#             logger.info(f"Uploaded to GCS: {gcs_uri}")
#             return gcs_uri
#         except Exception as e:
#             logger.error(f"GCS upload failed: {str(e)}")
#             raise

#     def cleanup_gcs(self, gcs_uri: str):
#         """Clean up GCS file after processing."""
#         try:
#             if gcs_uri and gcs_uri.startswith("gs://"):
#                 bucket_name, blob_name = gcs_uri[5:].split("/", 1)
#                 bucket = self.storage_client.bucket(bucket_name)
#                 blob = bucket.blob(blob_name)
#                 blob.delete()
#                 logger.info(f"Deleted GCS file: {gcs_uri}")
#         except Exception as e:
#             logger.warning(f"GCS cleanup failed: {str(e)}")


#104
import os
import time
from google.cloud import videointelligence
from google.cloud import storage
from google.api_core.exceptions import GoogleAPICallError
import logging
import tempfile
from langchain.schema import Document
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials from environment or fallback
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", r"D:\projects\CSE299\cortana\cortana\backend\youtube-api-461010-dbd270bbfb03.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

class GoogleVideoProcessor:
    def __init__(self, gcs_bucket_name: str = None):
        """
        Initialize Google Video Intelligence API processor.
        
        Args:
            gcs_bucket_name: Google Cloud Storage bucket name for video uploads
        """
        try:
            self.client = videointelligence.VideoIntelligenceServiceClient()
            self.storage_client = storage.Client()
            self.gcs_bucket_name = gcs_bucket_name or os.getenv("GCS_BUCKET_NAME")
            if not self.gcs_bucket_name:
                logger.warning("GCS bucket not specified. Videos over 10MB cannot be processed. Set GCS_BUCKET_NAME environment variable.")
        except Exception as e:
            logger.error(f"Failed to initialize Google clients: {str(e)}")
            raise

    def process_video(self, video_path: str, features: list = None) -> List[Document]:
        """
        Process video using Google Video Intelligence API and return as Documents.
        
        Args:
            video_path: Path to local video file or GCS URI (gs://...)
            features: List of features to analyze
            
        Returns:
            List of Document objects containing analysis results
        """
        # Determine processing method
        if video_path.startswith("gs://"):
            input_uri = video_path
        else:
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # in MB
            if file_size > 10 and not self.gcs_bucket_name:
                raise ValueError("Videos over 10MB require a GCS bucket. Set GCS_BUCKET_NAME.")
            input_uri = self._upload_to_gcs(video_path) if self.gcs_bucket_name and file_size > 10 else None

        # Configure features
        if not features:
            features = [
                videointelligence.Feature.SPEECH_TRANSCRIPTION,
                videointelligence.Feature.LABEL_DETECTION,
                videointelligence.Feature.TEXT_DETECTION,
                videointelligence.Feature.SHOT_CHANGE_DETECTION
            ]

        # Configure speech transcription
        speech_config = videointelligence.SpeechTranscriptionConfig(
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        video_context = videointelligence.VideoContext(speech_transcription_config=speech_config)

        # Process video
        try:
            operation = self.client.annotate_video(
                request={
                    "features": features,
                    "input_uri": input_uri or video_path,
                    "video_context": video_context,
                } if input_uri else {
                    "features": [videointelligence.Feature.SPEECH_TRANSCRIPTION, videointelligence.Feature.LABEL_DETECTION],
                    "input_content": open(video_path, "rb").read(),
                    "video_context": video_context,
                }
            )
            logger.info(f"Processing video: {input_uri or video_path}")
            result = operation.result(timeout=600)
            documents = self._parse_results_to_documents(result, input_uri or video_path)
            if input_uri:
                self.cleanup_gcs(input_uri)
            return documents
        except GoogleAPICallError as e:
            logger.error(f"API call failed for {video_path}: {str(e)}")
            return [Document(page_content=f"VIDEO PROCESSING ERROR: {str(e)}", metadata={"source": video_path})]
        except Exception as e:
            logger.error(f"Unexpected error processing {video_path}: {str(e)}")
            return [Document(page_content="VIDEO PROCESSING ERROR: Unexpected failure", metadata={"source": video_path})]

    def _parse_results_to_documents(self, result, source: str) -> List[Document]:
        """Parse API results into a list of Document objects with chunked transcript."""
        documents = []
        if not result.annotation_results:
            return [Document(page_content="No analysis results", metadata={"source": source})]

        annotation_result = result.annotation_results[0]
        
        # 1. Speech transcription
        transcript = ""
        for speech_transcription in annotation_result.speech_transcriptions:
            for alternative in speech_transcription.alternatives:
                transcript += alternative.transcript + " "
        transcript = transcript.strip() or "No transcript detected"

        # 2. Label detection
        labels = {label.entity.description: max(seg.confidence for seg in label.segments)
                 for label in annotation_result.segment_label_annotations}

        # 3. Text detection
        text_content = "\n".join(text.text for text in annotation_result.text_annotations) or "No text detected"

        # 4. Scene detection
        scenes = len(annotation_result.shot_annotations)

        # Initialize text splitter for transcript
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        # Create base summary without transcript
        base_summary = (
            f"VIDEO ANALYSIS SUMMARY:\n"
            f"Source: {source}\n"
            f"Scenes detected: {scenes}\n"
            f"Labels identified: {len(labels)}\n"
            f"Text elements found: {len(annotation_result.text_annotations)}\n\n"
            f"TEXT DETECTION:\n{text_content}"
        )

        # Chunk the transcript and create documents
        if transcript:
            transcript_chunks = text_splitter.split_text(transcript)
            for i, chunk in enumerate(transcript_chunks):
                full_content = f"{base_summary}\n\nTRANSCRIPT:\n{chunk}"
                documents.append(Document(page_content=full_content, metadata={"source": source, "media_type": "video", "chunk_id": i}))
        else:
            documents.append(Document(page_content=f"{base_summary}\n\nTRANSCRIPT:\n{transcript}", metadata={"source": source, "media_type": "video", "chunk_id": 0}))

        return documents

    def _upload_to_gcs(self, local_path: str) -> str:
        """Upload local video to Google Cloud Storage."""
        try:
            if not self.gcs_bucket_name:
                raise ValueError("GCS bucket not configured")
            bucket = self.storage_client.bucket(self.gcs_bucket_name)
            blob_name = os.path.basename(local_path)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            gcs_uri = f"gs://{self.gcs_bucket_name}/{blob_name}"
            logger.info(f"Uploaded to GCS: {gcs_uri}")
            return gcs_uri
        except Exception as e:
            logger.error(f"GCS upload failed: {str(e)}")
            raise

    def cleanup_gcs(self, gcs_uri: str):
        """Clean up GCS file after processing."""
        try:
            if gcs_uri and gcs_uri.startswith("gs://"):
                bucket_name, blob_name = gcs_uri[5:].split("/", 1)
                bucket = self.storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.delete()
                logger.info(f"Deleted GCS file: {gcs_uri}")
        except Exception as e:
            logger.warning(f"GCS cleanup failed: {str(e)}")


# Example usage
if __name__ == "__main__":
    processor = GoogleVideoProcessor(gcs_bucket_name="taslim-video-data")
    try:
        documents = processor.process_video("C:\\Users\\Hp\\Downloads\\slow.mp4")
        for doc in documents:
            print(doc.page_content)
    except Exception as e:
        logger.error(f"Video processing failed: {str(e)}")