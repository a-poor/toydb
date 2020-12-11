
import hashlib

def md5(text: str) -> str:
    """md5 hash function.

    Used for creating ``filenames`` based
    on ``table_names``.

    :param text: String to hash
    :return: Hex digest of ``text``
    """
    return hashlib.md5(text.encode()).hexdigest()
