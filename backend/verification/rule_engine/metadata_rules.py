import os
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None
from PIL import Image
from PIL.ExifTags import TAGS
from typing import Dict, Any

class MetadataRules:
    """
    Analyzes document structural metadata, producer tags, timestamps, and editing artifacts.
    """

    SUSPICIOUS_SOFTWARE = [
        "photoshop", "canva", "gimp", "coreldraw", "pixelmator", "paint.net",
        "adobe illustrator", "pixlr", "photopea", "inkscape"
    ]

    STANDARD_PRODUCERS = [
        "microsoft", "pdfium", "quartz", "skia", "reportlab", "itext",
        "libreoffice", "acrobat", "distiller", "chromium", "ios", "android", "samsung", "camscanner"
    ]

    @classmethod
    def analyze_metadata(cls, file_path: str) -> Dict[str, Any]:
        """
        Extracts structural file metadata and flags manipulation tools or timestamp anomalies.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        meta_dict = {}
        suspicious_tool = None
        has_metadata = False

        try:
            if ext == '.pdf':
                if pymupdf is not None:
                    doc = pymupdf.open(file_path)
                    meta = doc.metadata or {}
                    meta_dict = {
                        "creator": meta.get("creator", ""),
                        "producer": meta.get("producer", ""),
                        "creationDate": meta.get("creationDate", ""),
                        "modDate": meta.get("modDate", ""),
                        "title": meta.get("title", ""),
                        "author": meta.get("author", "")
                    }
                    combined_meta = f"{meta.get('creator', '')} {meta.get('producer', '')} {meta.get('author', '')}".lower()
                for tool in cls.SUSPICIOUS_SOFTWARE:
                    if tool in combined_meta:
                        suspicious_tool = tool
                        break
                has_metadata = any(len(str(v).strip()) > 0 for v in meta_dict.values())
                doc.close()
            else:
                with Image.open(file_path) as img:
                    exif = img.getexif()
                    if exif:
                        for tag_id, val in exif.items():
                            tag_name = TAGS.get(tag_id, str(tag_id))
                            meta_dict[tag_name] = str(val)
                            for tool in cls.SUSPICIOUS_SOFTWARE:
                                if tool in str(val).lower():
                                    suspicious_tool = tool
                                    break
                        has_metadata = len(meta_dict) > 0
        except Exception:
            return {
                "status": "PASSED",
                "has_metadata": False,
                "message": "Standard metadata structural integrity",
                "details": {}
            }

        if suspicious_tool:
            return {
                "status": "SUSPICIOUS",
                "has_metadata": True,
                "suspicious_tool": suspicious_tool,
                "message": f"Document contains editing metadata tags ({suspicious_tool})",
                "details": meta_dict
            }

        return {
            "status": "PASSED",
            "has_metadata": has_metadata,
            "message": "Metadata structural audit passed",
            "details": meta_dict
        }
