import os
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None
from PIL import Image

class FileValidator:
    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

    def validate(self, file_path: str):
        """
        Validates file existence, format, size, readability, and page count.
        """
        if not os.path.exists(file_path):
            return {"status": "Failed", "message": "File does not exist", "page_count": 0}

        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE:
            return {"status": "Failed", "message": "File exceeds 16MB limit", "file_size": file_size}

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return {"status": "Failed", "message": f"Unsupported extension: {ext}"}

        page_count = 1
        readable = False
        try:
            if ext == '.pdf':
                if pymupdf is not None:
                    doc = pymupdf.open(file_path)
                    page_count = len(doc)
                    if page_count > 0:
                        readable = True
                    doc.close()
                else:
                    return {"status": "Failed", "message": "PDF engine not available", "page_count": 0}
            else:
                with Image.open(file_path) as img:
                    img.verify()
                readable = True
        except Exception as e:
            return {"status": "Failed", "message": f"Corrupted file: {str(e)}", "page_count": 0}

        return {
            "status": "Passed" if readable else "Failed",
            "file_size": file_size,
            "page_count": page_count,
            "format": ext.replace('.', '').upper(),
            "readable": readable
        }
