
import hashlib
import itertools as it

from typing import Iterable, Generator

def md5(text: str) -> str:
    """md5 hash function.

    Used for creating ``filenames`` based
    on ``table_names``.

    :param text: String to hash
    :return: Hex digest of ``text``
    """
    return hashlib.md5(text.encode()).hexdigest()

def iter_limit(itr: Iterable, limit: int) -> Generator:
    """Generator function that limits the results.

    :param itr: Iterable to limit
    :param limit: Max number of values to yield
        from ``itr``. Must be a positive integer.
    :yields: Up to ``limit`` values from ``itr``.
    """
    for i, v in zip(it.count(),itr):
        if i >= limit: break
        yield v
