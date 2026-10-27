import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp'}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage, upload_folder: str):
    os.makedirs(upload_folder, exist_ok=True)
    orig_name = secure_filename(file_storage.filename)
    ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else 'pdf'
    unique_filename = f"doc_{uuid.uuid4().hex[:12]}.{ext}"
    dest_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(dest_path)
    file_size = os.path.getsize(dest_path)
    return orig_name, unique_filename, dest_path, file_size
