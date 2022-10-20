from __future__ import annotations
from . path import Path
from . pd_handle import PDHandle


def pd(data: dict | list, str_sep="/", raw=False) -> PDHandle:
    """
    Creates and returns a handle on the given data.

    Args:
    - `data` - Must be a list or dict.
    - `str_sep` - Look within path strings for this separator and use it to split the path.
    - `raw` - If `True`, do not interpret paths. So wildcards (`*`) are interpreted as a usual key, and tuples will be interpreted as keys  as well.

    Returns:
    - A handle that references the root of the given data dict or list.
    """
    path = Path([], str_sep=str_sep, raw=raw)
    return PDHandle(data, path)

################################################################################
# To be used like this:
# pd(db).at("u1", "meta", "last_login").get()
# pd(db).at("*", "meta").get()
# pd(db).at("u10", "meta", "last_login").set(1234567890)
# pd(db).at("u10", "meta", "last_login").delete()
# pd(db).at("u10", "meta", "last_login").exists()

# We need some kind of FloatingHandle that is returned by the PathDict.at() method
# This handle will be used to get, set, delete, etc. the value at the path.
# If the pat in at() is a wildcard, then a FloatingWildcardHandle will be returned instead
# This handle will be used to get, set, delete, etc. the values at the paths that match the wildcard

# The workflow is always .at().do_something()
# Except for pd(x).do_something(), then at() is implied to just select x

# So we must just use the same Handle for all situations.
# The Handle then needs to be able to handle all situations.
# For the .do_something() after .at(), we need to tell the do_something() method
# what the path is and wheater or not it is a wildcard path.

# If .at(path) has wildcards, then we really need a PDMultiHandle
# After the .do_something(), a regular PDHandle will be returned, at its previous path
