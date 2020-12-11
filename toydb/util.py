
import hashlib

def md5(text: str) -> str:
    """md5 hash

    :param text: String to hash
    :return: Hex 
    """
    return hashlib.md5(text.encode()).hexdigest()
