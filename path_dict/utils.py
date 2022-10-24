from __future__ import annotations
from typing import Any
import copy


def fast_deepcopy(obj):
	"""
	Makes a fast deep copy of the object.
	dict, list, tuple, set, str, int, float and bool are truly copied.
	Everything else is just copied by reference.

	:param obj: The object to be copied
	"""
	# Fast exit for immutable types
	if isinstance(obj, (int, str, bool, float)):
		return obj
	# Copy key and value for dicts
	if isinstance(obj, dict):
		return {fast_deepcopy(k): fast_deepcopy(v) for k, v in obj.items()}
	# Copy all other supported types
	if (t := type(obj)) in (list, tuple, set):
		return t(fast_deepcopy(v) for v in obj)
	# Everything else is copied by reference
	return obj


def safe_list_get(current, key):
	try:
		return current[int(key)]
	except (ValueError, IndexError) as e:
		raise KeyError(f"PathDict: invalid path ({key} not in {current})") from e


def guarded_get(current: dict | list, key: Any):
	"""
	Get the value at the given key. If current is a dict, return None if the key
	does not exist. If current is a list, return a KeyError if a problem occurs.

	:param: current: The current dictionary or list we're looking at
	:param: key: The key to look up
	"""

	if isinstance(current, dict):
		return None if key not in current else current[key]
	if isinstance(current, list):
		return safe_list_get(current, key)
	raise KeyError(
		f"PathDict: The path is not a stack of nested dicts and lists "
		f"(value at key {key} has type {type(current)})"
	)


def guarded_descent(current, key):
	"""
	Like guarded_get, but create new empty dicts on the way down if necessary.
	"""

	if isinstance(current, dict):
		current.setdefault(key, {})
		return current[key]
	if isinstance(current, list):
		return safe_list_get(current, key)
	raise KeyError("Can't set the key of a non-dict")


def get_nested_keys_or_indices(ref: dict | list, path: list):
	"""
	:param ref: The reference dictionary or list
	:param path: The path to object or list we want to get the keys or indices of

	If the nested object is a list, the return a list of all list indices.

	If the path does not exist, return [].

	If there is something in path where we cannot continue to traverse the
	tree of dicts and lists (e.g. due to trying to get a string key from a list),
	a KeyError is raised.
	"""

	current = ref
	# Traverse the path of dicts and lists.
	for key in path:
		current = guarded_get(current, key)
		if current is None:
			return []

	# Return keys or indices or raise KeyError
	if isinstance(current, dict):
		return list(current.keys())
	if isinstance(current, list):
		return list(range(len(current)))
	raise KeyError(
		f"PathDict: The path is not a stack of nested dicts and lists "
		f"(value at key {key} has type {type(current)})"
	)
