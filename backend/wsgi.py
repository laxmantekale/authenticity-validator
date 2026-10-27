"""
WSGI entrypoint for production deployments (Gunicorn / Render / Railway / Docker).
Authentication Validator - Secure Academic Document Verification Platform
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
