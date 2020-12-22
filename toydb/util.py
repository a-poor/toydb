
import hashlib
import itertools as it

def md5(text: str) -> str:
    """md5 hash function.

    Used for creating ``filenames`` based
    on ``table_names``.

    :param text: String to hash
    :return: Hex digest of ``text``
    """
    return hashlib.md5(text.encode()).hexdigest()

def iter_limit(itr, limit=None):
    for i, v in zip(it.count(),itr):
        if i >= limit: break
        yield v
