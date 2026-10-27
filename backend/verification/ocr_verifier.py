import os
import re
import shutil
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

from utils.document_utils import mask_sensitive_data
from verification.field_extractor import FieldExtractionService

logger = logging.getLogger(__name__)

def configure_tesseract() -> Tuple[bool, Optional[str]]:
    """
    Auto-discovers and configures the Tesseract OCR executable for pytesseract on Windows/Linux/macOS.
    Discovery order:
    1. TESSERACT_CMD environment variable
    2. PATH lookup (shutil.which('tesseract') / shutil.which('tesseract.exe'))
    3. Standard Windows installation paths
    Returns (is_available, configured_path)
    """
    if pytesseract is None:
        return False, None

    candidate_paths = [
        os.environ.get("TESSERACT_CMD"),
        shutil.which("tesseract"),
        shutil.which("tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe")
    ]

    for path in candidate_paths:
        if path and os.path.isfile(path):
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                tessdata_dir = os.path.join(os.path.dirname(path), "tessdata")
                if os.path.isdir(tessdata_dir) and not os.environ.get("TESSDATA_PREFIX"):
                    os.environ["TESSDATA_PREFIX"] = tessdata_dir
                return True, path
            except Exception as e:
                logger.warning(f"Failed to configure Tesseract at {path}: {e}")

    return False, None

# Initialize Tesseract configuration on module load
_TESSERACT_AVAILABLE, _TESSERACT_PATH = configure_tesseract()


class OCRVerifier:
    """
    Evidence-based Multi-Page Document Text Extraction & Structured Field Parser.
    Hybrid pipeline: native PyMuPDF embedded text extraction + rasterized Tesseract OCR
    with deskewing, blur detection, noise reduction, and adaptive thresholding.
    """

    @staticmethod
    def is_text_sufficient(text: str) -> bool:
        """
        Determines if extracted text has sufficient informational density.
        Evaluates character count, alphanumeric tokens, recognizable words, and filters scanner watermarks.
        """
        if not text:
            return False

        clean = text.strip()
        if len(clean) < 60:
            return False

        # Check for meaningful alphanumeric words
        words = re.findall(r'\b[A-Za-z0-9]{2,}\b', clean)
        if len(words) < 8:
            return False

        # Filter out trivial scanner watermarks (e.g., 'Scanned with ACE Scanner')
        non_watermark_words = [
            w for w in words
            if w.lower() not in ['scanned', 'with', 'ace', 'camscanner', 'scanner', 'adobe', 'scan', 'document']
        ]
        if len(non_watermark_words) < 5:
            return False

        return True

    @staticmethod
    def detect_blur(cv_img: np.ndarray, threshold: float = 65.0) -> Tuple[bool, float]:
        """
        Computes Laplacian variance to detect blurred or out-of-focus scans.
        Returns (is_blurry, variance).
        """
        if cv2 is None or cv_img is None or cv_img.size == 0:
            return False, 100.0

        try:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
            var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            is_blurry = var < threshold
            return is_blurry, round(var, 2)
        except Exception:
            return False, 100.0

    @staticmethod
    def deskew_image(cv_img: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Detects document skew angle and rotates horizontally for optimal OCR character recognition.
        Returns (deskewed_cv_img, skew_angle).
        """
        if cv2 is None or cv_img is None or cv_img.size == 0:
            return cv_img, 0.0

        try:
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
            # Threshold to find text contours
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 100:
                return cv_img, 0.0

            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle

            if 0.5 < abs(angle) < 45.0:
                h, w = cv_img.shape[:2]
                center = (w // 2, h // 2)
                m = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    cv_img, m, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
                return rotated, round(angle, 2)
        except Exception as e:
            logger.debug(f"Deskew exception: {e}")

        return cv_img, 0.0

    @classmethod
    def preprocess_image_for_ocr(cls, pil_img: Image.Image) -> Tuple[Image.Image, List[str]]:
        """
        Applies comprehensive image enhancement pipeline:
        - Grayscale conversion
        - Blur detection
        - Deskewing
        - Noise reduction (median filter)
        - Contrast enhancement via CLAHE / Adaptive stretching
        - Adaptive thresholding
        Returns (enhanced_pil_img, image_warnings)
        """
        warnings = []
        try:
            # Convert PIL to OpenCV BGR
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR) if cv2 is not None else None

            if cv_img is not None:
                # 1. Blur check
                is_blurry, blur_var = cls.detect_blur(cv_img)
                if is_blurry:
                    warnings.append(f"Scan quality is low or blurred (focus sharpness index: {blur_var:.1f})")

                # 2. Deskew check
                deskewed_cv, angle = cls.deskew_image(cv_img)
                if abs(angle) >= 0.5:
                    warnings.append(f"Document skew corrected ({angle:+.1f}°)")
                    cv_img = deskewed_cv

                # 3. Grayscale
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                # 4. Noise reduction
                denoised = cv2.medianBlur(gray, 3)

                # 5. Contrast enhancement with CLAHE
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced_gray = clahe.apply(denoised)

                # 6. Adaptive thresholding for crisp text boundaries
                # Blend enhanced gray with adaptive threshold to keep subtle anti-aliased character edges
                thresh = cv2.adaptiveThreshold(
                    enhanced_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 15, 6
                )
                blended = cv2.addWeighted(enhanced_gray, 0.7, thresh, 0.3, 0)

                return Image.fromarray(blended), warnings

        except Exception as e:
            logger.debug(f"OpenCV enhancement fallback to PIL: {e}")

        # Fallback pure PIL enhancement if OpenCV is unavailable
        try:
            gray = pil_img.convert('L')
            contrast = ImageEnhance.Contrast(gray)
            enhanced = contrast.enhance(1.8)
            sharpness = ImageEnhance.Sharpness(enhanced)
            return sharpness.enhance(1.5), warnings
        except Exception:
            return pil_img, warnings

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Cleans and normalizes extracted text:
        - Removes zero-width and unusual unicode spaces
        - Normalizes smart quotes and hyphens
        - Preserves alphanumeric tokens, case, and essential punctuation
        """
        if not text:
            return ""

        # Normalize unicode spaces & artifacts
        text = re.sub(r'[\u00a0\u200b\u200c\u200d\u3000\ufeff]', ' ', text)
        # Normalize smart quotes
        text = re.sub(r'[\u2018\u2019\u201a\u201b`]', "'", text)
        text = re.sub(r'[\u201c\u201d\u201e\u201f«»]', '"', text)
        # Normalize dashes
        text = re.sub(r'[\u2013\u2014\u2015\u2212]', '-', text)
        # Normalize excessive horizontal whitespace per line
        lines = text.split('\n')
        cleaned_lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in lines]
        return '\n'.join(cleaned_lines).strip()

    def calculate_extraction_quality(self, text: str, total_pages: int, ocr_used: bool, warnings: List[str]) -> float:
        """
        Calculates an objective Extraction Quality percentage score (0.0 to 100.0%)
        based on character density, token coherence, page count, and scan clarity.
        """
        if not text or len(text.strip()) == 0:
            return 0.0

        clean = text.strip()
        char_count = len(clean)

        # 1. Base score from character count relative to page count
        expected_chars = max(1, total_pages) * 200
        coverage_ratio = min(1.0, char_count / expected_chars)
        base_score = coverage_ratio * 60.0

        # 2. Token coherence: proportion of recognized alphanumeric words
        words = re.findall(r'\b[A-Za-z0-9]{2,}\b', clean)
        word_count = len(words)
        if word_count >= 20:
            coherence_score = 30.0
        elif word_count >= 10:
            coherence_score = 20.0
        elif word_count >= 5:
            coherence_score = 10.0
        else:
            coherence_score = 5.0

        # 3. Native vector text bonus (+10 pts)
        method_bonus = 10.0 if not ocr_used else 5.0

        total_quality = base_score + coherence_score + method_bonus

        # 4. Penalty for warnings (e.g. severe blur or skew)
        penalty = len([w for w in warnings if 'blurred' in w.lower() or 'low quality' in w.lower()]) * 15.0
        total_quality = max(5.0, min(99.0, total_quality - penalty))

        return round(total_quality, 1)

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts multi-page text from PDF or Image file.
        Uses PyMuPDF for native embedded text with rasterized Tesseract OCR fallback.
        Preserves page numbers, warnings, and extraction quality metrics.
        """
        global _TESSERACT_AVAILABLE, _TESSERACT_PATH
        if not _TESSERACT_AVAILABLE:
            _TESSERACT_AVAILABLE, _TESSERACT_PATH = configure_tesseract()

        raw_text = ""
        total_pages = 0
        pages_ocr_processed = 0
        ocr_used = False
        embedded_chars_total = 0
        embedded_sufficient = True
        engine_type = "none"
        extraction_warnings: List[str] = []
        page_details: List[Dict[str, Any]] = []

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        try:
            if ext == '.pdf':
                if pymupdf is not None:
                    doc = pymupdf.open(file_path)
                    total_pages = len(doc)
                    page_texts: List[str] = []

                    for page_num in range(total_pages):
                        page = doc[page_num]
                        p_text = page.get_text() or ""
                        p_char_count = len(p_text.strip())
                        embedded_chars_total += p_char_count

                        # Determine if page embedded text is sufficient
                        page_sufficient = self.is_text_sufficient(p_text)
                        page_ocr_run = False

                        if not page_sufficient:
                            embedded_sufficient = False

                            # Run high-resolution OCR fallback if Tesseract is available
                            if _TESSERACT_AVAILABLE and pytesseract is not None:
                                try:
                                    img = None
                                    # Check if page contains a high-resolution embedded image
                                    page_images = page.get_images()
                                    if page_images:
                                        xref = page_images[0][0]
                                        base_img = doc.extract_image(xref)
                                        if base_img and base_img.get("width", 0) >= 800:
                                            import io
                                            img = Image.open(io.BytesIO(base_img["image"]))

                                    # Otherwise, render page pixmap with 200 DPI
                                    if img is None:
                                        pix = page.get_pixmap(dpi=200)
                                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                                    # Preprocess image (deskew, blur detect, contrast, adaptive threshold)
                                    preprocessed, p_warnings = self.preprocess_image_for_ocr(img)
                                    extraction_warnings.extend(p_warnings)

                                    # OCR with PSM 6 (block of text) and fallback to PSM 3 (auto)
                                    ocr_page_text = pytesseract.image_to_string(preprocessed, config='--psm 6')
                                    if len(ocr_page_text.strip()) < 30:
                                        ocr_page_text = pytesseract.image_to_string(preprocessed, config='--psm 3')

                                    if len(ocr_page_text.strip()) > len(p_text.strip()):
                                        if len(p_text.strip()) > 10:
                                            p_text = f"{p_text}\n{ocr_page_text}"
                                        else:
                                            p_text = ocr_page_text
                                        ocr_used = True
                                        pages_ocr_processed += 1
                                        page_ocr_run = True
                                except Exception as ocr_err:
                                    msg = f"Page {page_num + 1}: OCR processing exception: {ocr_err}"
                                    logger.warning(msg)
                                    extraction_warnings.append(msg)
                            else:
                                extraction_warnings.append(
                                    f"Page {page_num + 1}: Embedded text is sparse and Tesseract OCR engine is not configured."
                                )

                        page_texts.append(p_text)
                        page_details.append({
                            "page_number": page_num + 1,
                            "char_count": len(p_text.strip()),
                            "ocr_applied": page_ocr_run,
                            "sufficient": page_sufficient or page_ocr_run
                        })

                    raw_text = "\n\n".join(page_texts)
                    engine_type = "pymupdf+tesseract" if ocr_used else "pymupdf_embedded"
                    doc.close()
                else:
                    raw_text = ""
                    extraction_warnings.append("PyMuPDF engine not available on server.")
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                total_pages = 1
                if _TESSERACT_AVAILABLE and pytesseract is not None:
                    try:
                        img = Image.open(file_path)
                        preprocessed, p_warnings = self.preprocess_image_for_ocr(img)
                        extraction_warnings.extend(p_warnings)

                        raw_text = pytesseract.image_to_string(preprocessed, config='--psm 6')
                        if len(raw_text.strip()) < 30:
                            raw_text = pytesseract.image_to_string(preprocessed, config='--psm 3')

                        ocr_used = True
                        pages_ocr_processed = 1
                        engine_type = "tesseract_image"
                        page_details.append({
                            "page_number": 1,
                            "char_count": len(raw_text.strip()),
                            "ocr_applied": True,
                            "sufficient": len(raw_text.strip()) > 30
                        })
                    except Exception as img_err:
                        logger.error(f"Image OCR processing failed for {file_path}: {img_err}")
                        raw_text = ""
                        extraction_warnings.append(f"Image OCR failed: {img_err}")
                else:
                    raw_text = ""
                    extraction_warnings.append("Pytesseract OCR engine not available for image processing.")
        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {e}")
            raw_text = ""
            extraction_warnings.append(f"Extraction error: {str(e)}")

        # Clean duplicates in warnings
        unique_warnings = list(dict.fromkeys(extraction_warnings))

        # Normalize text
        normalized_text = self.normalize_text(raw_text)

        # Calculate extraction quality
        extraction_quality = self.calculate_extraction_quality(
            text=normalized_text,
            total_pages=total_pages,
            ocr_used=ocr_used,
            warnings=unique_warnings
        )

        # Parse structured universal fields
        structured = FieldExtractionService.extract_fields(normalized_text)

        status = "Passed" if len(normalized_text.strip()) > 0 else "Skipped"
        if len(normalized_text.strip()) == 0 and not _TESSERACT_AVAILABLE:
            status = "Unavailable"

        return {
            "raw_text": normalized_text,
            "raw_text_masked": mask_sensitive_data(normalized_text),
            "structured": structured,
            "status": status,
            "extraction_quality": extraction_quality,
            "warnings": unique_warnings,
            "metadata": {
                "total_pages": total_pages,
                "char_count": len(normalized_text),
                "ocr_used": ocr_used,
                "pages_ocr_processed": pages_ocr_processed,
                "engine": engine_type,
                "page_details": page_details,
                "tesseract_available": _TESSERACT_AVAILABLE
            }
        }

    def parse_academic_fields(self, text: str) -> Dict[str, Any]:
        """
        Extracts structured fields across universal categories.
        Defers to FieldExtractionService.
        """
        return FieldExtractionService.extract_fields(text)


ocr_verifier = OCRVerifier()
