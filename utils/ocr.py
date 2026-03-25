import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)

        cleaned_text = text.strip()
        return cleaned_text

    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {str(e)}")