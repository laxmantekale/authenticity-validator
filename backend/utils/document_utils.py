import os
import re
import cv2
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None
from PIL import Image
import numpy as np
from typing import List

def mask_sensitive_data(text: str) -> str:
    """
    Masks PII such as Aadhaar and PAN numbers in extracted OCR text.
    """
    if not text:
        return text
    # Mask Aadhaar numbers (12 digits) -> XXXX XXXX 1234
    masked = re.sub(r'\b(\d{4})[\s\-](\d{4})[\s\-](\d{4})\b', r'XXXX XXXX \3', text)
    masked = re.sub(r'\b(\d{8})(\d{4})\b', r'XXXX XXXX \2', masked)
    # Mask PAN numbers (5 letters, 4 digits, 1 letter) -> XXXXX1234X
    masked = re.sub(r'\b([A-Z]{5})(\d{4})([A-Z])\b', r'XXXXX\2\3', masked, flags=re.IGNORECASE)
    return masked

def convert_pdf_to_images(pdf_path: str, max_pages: int = 5, dpi: int = 150) -> List[Image.Image]:
    """
    Renders pages of a PDF document to PIL Images.
    """
    images = []
    try:
        if pymupdf is None:
            return images
        doc = pymupdf.open(pdf_path)
        for page_num in range(min(len(doc), max_pages)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=dpi)
            if pix.n == 4:
                img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples).convert("RGB")
            elif pix.n == 1:
                img = Image.frombytes("L", [pix.width, pix.height], pix.samples).convert("RGB")
            else:
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
    except Exception:
        pass
    return images

def get_pil_images_from_file(file_path: str, max_pages: int = 5) -> List[Image.Image]:
    """
    Returns a list of PIL Images from either PDF or image files.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return convert_pdf_to_images(file_path, max_pages=max_pages)
    try:
        img = Image.open(file_path).convert('RGB')
        return [img]
    except Exception:
        return []

def get_cv2_images_from_file(file_path: str, max_pages: int = 5) -> List[np.ndarray]:
    """
    Returns a list of BGR numpy images ready for OpenCV processing.
    """
    pil_images = get_pil_images_from_file(file_path, max_pages=max_pages)
    cv_images = []
    for pil_img in pil_images:
        try:
            arr_rgb = np.array(pil_img)
            arr_bgr = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
            cv_images.append(arr_bgr)
        except Exception:
            pass
    return cv_images
