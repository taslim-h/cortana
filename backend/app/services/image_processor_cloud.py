import os
import logging
from typing import List, Dict, Optional
from google.cloud import vision
import openai
from PIL import Image
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudImageProcessor:
    def __init__(self):
        """
        Initialize cloud-based image processing services
        
        Requires:
        - GOOGLE_APPLICATION_CREDENTIALS env var set
        - OPENAI_API_KEY env var set
        """
        # Initialize Google Vision client
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Configure OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

    def process_image(self, image_source) -> Dict:
        """
        Process image using cloud services
        
        Args:
            image_source: Can be either:
                - File path (str)
                - Image URL (str)
                - PIL.Image object
        
        Returns:
            {
                "text": extracted text,
                "objects": detected objects,
                "description": AI-generated description,
                "metadata": image info
            }
        """
        try:
            # Prepare the image
            if isinstance(image_source, str):
                if image_source.startswith(('http://', 'https://')):
                    image = self._get_image_from_url(image_source)
                else:
                    image = self._get_image_from_file(image_source)
            elif isinstance(image_source, Image.Image):
                image = image_source
            else:
                raise ValueError("Unsupported image source type")

            # Process with both APIs in parallel
            google_results = self._google_vision_analysis(image)
            openai_results = self._openai_analysis(image)
            
            return {
                "text": google_results.get("text", ""),
                "objects": google_results.get("objects", {}),
                "description": openai_results.get("description", ""),
                "metadata": {
                    "dimensions": image.size,
                    "mode": image.mode
                }
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {
                "error": str(e),
                "text": "",
                "objects": {},
                "description": ""
            }

    def _google_vision_analysis(self, image: Image.Image) -> Dict:
        """Analyze image using Google Vision API"""
        try:
            # Convert PIL Image to Google Vision format
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            content = img_byte_arr.getvalue()
            vision_image = vision.Image(content=content)
            
            # Perform text detection
            text_response = self.vision_client.text_detection(image=vision_image)
            texts = [text.description for text in text_response.text_annotations]
            
            # Perform object detection
            object_response = self.vision_client.object_localization(image=vision_image)
            objects = {}
            for obj in object_response.localized_object_annotations:
                objects[obj.name.lower()] = objects.get(obj.name.lower(), 0) + 1
            
            return {
                "text": "\n".join(texts) if texts else "",
                "objects": objects
            }
            
        except Exception as e:
            logger.error(f"Google Vision API failed: {str(e)}")
            return {"text": "", "objects": {}}

    def _openai_analysis(self, image: Image.Image) -> Dict:
        """Generate description using OpenAI's GPT-4 Vision"""
        try:
            # Convert PIL Image to base64
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_base64 = img_byte_arr.getvalue()
            
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in detail including any text and objects"},
                            {
                                "type": "image_url",
                                "image_url": f"data:image/png;base64,{img_base64}"
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            return {
                "description": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"OpenAI API failed: {str(e)}")
            return {"description": ""}

    def _get_image_from_url(self, url: str) -> Image.Image:
        """Download image from URL"""
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    def _get_image_from_file(self, file_path: str) -> Image.Image:
        """Load image from file"""
        return Image.open(file_path)

# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = CloudImageProcessor()
    
    # Process image from URL
    result = processor.process_image("https://example.com/image.jpg")
    print("Google Vision Text:", result["text"])
    print("Detected Objects:", result["objects"])
    print("OpenAI Description:", result["description"])
    
    # Process local image
    # result = processor.process_image("local_image.jpg")


    #setup guide 
    # pip install google-cloud-vision
    # export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"