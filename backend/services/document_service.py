import os
from extensions import db
from models.document import Document
from models.student import Student
from utils.hash_utils import calculate_sha256
from utils.file_utils import save_uploaded_file, is_allowed_file

class DocumentService:
    @staticmethod
    def upload_document(student_id, college_id, file_storage, document_type, document_title, upload_folder):
        if not is_allowed_file(file_storage.filename):
            return None, "Unsupported file format. Please upload PDF, PNG, JPG, JPEG, or WEBP."

        orig_name, unique_name, dest_path, file_size = save_uploaded_file(file_storage, upload_folder)
        file_hash = calculate_sha256(dest_path)
        ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'pdf'
        mime_type = "application/pdf" if ext == 'pdf' else f"image/{ext}"

        doc = Document(
            student_id=student_id,
            college_id=college_id,
            name=document_title or orig_name,
            document_type=document_type or "Other Academic Document",
            original_filename=orig_name,
            stored_filename=unique_name,
            file_path=dest_path,
            file_hash=file_hash,
            file_size=file_size,
            mime_type=mime_type,
            verification_status="Not Verified"
        )
        db.session.add(doc)
        db.session.commit()
        return doc, None

    @staticmethod
    def delete_document(doc_id, student_id=None, college_id=None):
        query = Document.query.filter_by(id=doc_id)
        if student_id:
            query = query.filter_by(student_id=student_id)
        if college_id:
            query = query.filter_by(college_id=college_id)

        doc = query.first()
        if not doc:
            return False, "Document not found or unauthorized."

        # Remove physical file
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass

        db.session.delete(doc)
        db.session.commit()
        return True, None
