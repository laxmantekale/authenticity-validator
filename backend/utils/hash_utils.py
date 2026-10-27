import hashlib

def calculate_sha256(file_path_or_bytes):
    """
    Calculates SHA-256 hash of a file or byte stream.
    """
    sha256_hash = hashlib.sha256()
    if isinstance(file_path_or_bytes, bytes):
        sha256_hash.update(file_path_or_bytes)
        return sha256_hash.hexdigest()

    with open(file_path_or_bytes, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
