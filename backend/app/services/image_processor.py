# from transformers import BlipProcessor, BlipForConditionalGeneration
# from transformers import pipeline
# from PIL import Image
# import torch
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class EnhancedImageProcessor:
#     def __init__(self):
#         # Initialize models
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
#         # BLIP for general captioning
#         self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
#         self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(self.device)
        
#         # Object detection model
#         self.detector = pipeline(
#             "object-detection", 
#             model="facebook/detr-resnet-50",
#             device=0 if torch.cuda.is_available() else -1
#         )

#     def generate_detailed_caption(self, image_path: str) -> str:
#         try:
#             image = Image.open(image_path).convert("RGB")
            
#             # Generate general caption
#             inputs = self.blip_processor(images=image, return_tensors="pt").to(self.device)
#             outputs = self.blip_model.generate(**inputs)
#             general_caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            
#             # Detect objects and count them
#             detection_results = self.detector(image)
#             counts = {}
            
#             for result in detection_results:
#                 label = result['label']
#                 counts[label] = counts.get(label, 0) + 1
            
#             object_counts = ", ".join(
#                 [f"{count} {label}{'s' if count > 1 else ''}" 
#                  for label, count in counts.items()]
#             ) if counts else "No objects detected"
            
#             # Combine information
#             return (
#                 f"Description: {general_caption}\n"
#                 # f"Objects: {object_counts}"
#             )
            
#         except Exception as e:
#             logger.error(f"Image processing failed: {str(e)}")
#             return "Could not generate detailed image description"

# # Example usage:
# if __name__ == "__main__":
#     processor = EnhancedImageProcessor()
#     caption = processor.generate_detailed_caption("D:\\projects\\CSE299\\cortana\\cortana\\backend\\temp_docs\\687218925c5f3b9f37cb95d2\\1sU4DIlxy8WG-MLriZZIVm65j4YSjG8nF.png")
#     print(caption)


# from transformers import BlipProcessor, BlipForConditionalGeneration
# from transformers import pipeline
# from PIL import Image
# import torch
# import pytesseract
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class EnhancedImageProcessor:
#     def __init__(self):
#         """Initialize the EnhancedImageProcessor with models and device settings."""
#         # Device configuration
#         self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
#         # BLIP for general captioning
#         self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
#         self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(self.device)
        
#         # Object detection model
#         self.detector = pipeline(
#             "object-detection",
#             model="facebook/detr-resnet-50",
#             device=0 if torch.cuda.is_available() else -1
#         )

#     def extract_text(self, image_path: str) -> str:
#         """Extract text from an image using OCR."""
#         try:
#             image = Image.open(image_path).convert("RGB")
#             extracted_text = pytesseract.image_to_string(image)
#             return extracted_text.strip() if extracted_text.strip() else "No text detected"
#         except Exception as e:
#             logger.error(f"OCR failed for {image_path}: {str(e)}")
#             return "No text detected"

#     def generate_detailed_caption(self, image_path: str) -> str:
#         """Generate a detailed caption including general description and object detection."""
#         try:
#             image = Image.open(image_path).convert("RGB")
            
#             # Generate general caption
#             inputs = self.blip_processor(images=image, return_tensors="pt").to(self.device)
#             outputs = self.blip_model.generate(**inputs)
#             general_caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            
#             # Detect objects and count them
#             detection_results = self.detector(image)
#             counts = {}
#             for result in detection_results:
#                 label = result['label']
#                 counts[label] = counts.get(label, 0) + 1
            
#             object_counts = ", ".join(
#                 [f"{count} {label}{'s' if count > 1 else ''}" 
#                  for label, count in counts.items()]
#             ) if counts else "No objects detected"
            
#             # Combine information
#             return (
#                 f"Description: {general_caption}\n"
#                 f"Objects: {object_counts}"
#             )
#         except Exception as e:
#             logger.error(f"Image processing failed: {str(e)}")
#             return "Could not generate detailed image description"

#     def process_image(self, image_path: str) -> str:
#         """Process an image to extract text and generate a detailed caption."""
#         extracted_text = self.extract_text(image_path)
#         detailed_caption = self.generate_detailed_caption(image_path)
#         return f"{extracted_text}\n{detailed_caption}" if extracted_text != "No text detected" else detailed_caption

# # Example usage:
# if __name__ == "__main__":
#     processor = EnhancedImageProcessor()
#     result = processor.process_image("D:\\projects\\CSE299\\cortana\\cortana\\backend\\temp_docs\\687218925c5f3b9f37cb95d2\\1sU4DIlxy8WG-MLriZZIVm65j4YSjG8nF.png")
#     print(result)

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import pytesseract
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedImageProcessor:
    def __init__(self):
        """Initialize the EnhancedImageProcessor with models and device settings."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # BLIP for general captioning
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(self.device)

    def extract_text(self, image_path: str) -> str:
        """Extract text from an image using OCR."""
        try:
            image = Image.open(image_path).convert("RGB")
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text.strip() if extracted_text.strip() else "No text detected"
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {str(e)}")
            return "No text detected"

    def generate_detailed_caption(self, image_path: str) -> str:
        """Generate a detailed caption using only BLIP description."""
        try:
            image = Image.open(image_path).convert("RGB")
            
            # Generate general caption
            inputs = self.blip_processor(images=image, return_tensors="pt").to(self.device)
            outputs = self.blip_model.generate(**inputs)
            general_caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            
            return f"Description: {general_caption}"
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return "Could not generate image description"

    def process_image(self, image_path: str) -> str:
        """Process an image to extract text and generate a detailed caption."""
        extracted_text = self.extract_text(image_path)
        detailed_caption = self.generate_detailed_caption(image_path)
        return f"{extracted_text}\n{detailed_caption}" if extracted_text != "No text detected" else detailed_caption

# Example usage:
if __name__ == "__main__":
    processor = EnhancedImageProcessor()
    result = processor.process_image("D:\\projects\\CSE299\\cortana\\cortana\\backend\\temp_docs\\687218925c5f3b9f37cb95d2\\1sU4DIlxy8WG-MLriZZIVm65j4YSjG8nF.png")
    print(result)