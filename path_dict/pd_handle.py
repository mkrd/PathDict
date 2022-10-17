from __future__ import annotations
from typing import Any, Callable, Union
import copy
import json
from . import utils
from . path import Path


class PDHandle:
	root_data: dict | list | Any
	data:      dict | list | Any
	path_handle: Path

	def __init__(self, data: dict | list, str_sep="/", raw=False) -> None:
		"""
		A PDHandle always refers to a dict or list.
		It is used to get data or perform operations at a given path.
		When initialized, the current path is the root path.
		"""

		if not isinstance(data, (dict, list)):
			raise TypeError("PathDict init: data argument must be a dict or list")

		self.root_data = data  # The original data that was passed to the first PDHandle
		self.data = data
		self.path_handle = Path([], str_sep=str_sep, raw=raw)


	def copy(self, at_root=False) -> PDHandle:
		"""
		Return a deep copy of the data at the current path or from the root.

		:param at_root: If True, copy the root data instead of the current
		path handle value.
		"""
		if at_root:
			return PDHandle(
				copy.deepcopy(self.data),
				str_sep=self.path_handle.str_sep,
				raw=self.path_handle.raw
			)
		else:
			return PDHandle(
				copy.deepcopy(self.get()),
				str_sep=self.path_handle.str_sep,
				raw=self.path_handle.raw
			)


	############################################################################
	# Moving the handle
	############################################################################


	def at(self, *path, str_sep=None, raw=None) -> Union[PDHandle, PDMultiHandle]:
		"""
		Calling at(path) moves the handle to the given path, and returns the
		handle.

		A path can be a string, a list or a tuple. For example, the following
		are equivalent:
		>>> d = {"a": {"b": {"c": 1}}}
		>>>	pd(d).at("a/b/c").get() # -> 1
		>>> pd(d).at(["a", "b", "c"]).get() # -> 1
		>>> pd(d).at("a", "b", "c").get() # -> 1

		The path can also contain wildcards (*) to select everything at a given
		level, and [a|b|c] to select multiple keys at a given level.
		In this case, the result is a PDMultiHandle, which can perform
		operations on all the selected elements at once.

		:param path: The path to move to.
		:param str_sep: The separator to use if there are separators in the path.
		:param raw: If True, the path is not parsed, and is used as is. For
		example, "*" will not be interpreted as a wildcard, but as a usual key.
		"""

		self.path_handle = Path(*path,
			str_sep=str_sep or self.path_handle.str_sep,
			raw=raw or self.path_handle.raw,
		)

		if self.path_handle.has_wildcards:
			return PDMultiHandle(self.root_data, self.path_handle)
		return self


	def at_root(self) -> PDHandle:
		"""
		Move the handle back to the root of the data and return it.
		Equivalent to
		>>> <PDHandle>.at()

		Useful if you are in a nested handle but also want to do something on the root data.

		Example:
		>>> d = {"a": {"b": {"c": 1}}}
		>>> pd(d).at("a/b").filter(lambda k,v: v > 1).root().filter(lambda k,v: k == "a").get()
		"""
		return self.at()


	def at_parent(self) -> PDHandle:
		"""
		Move the handle to the parent of the current path and return it.
		"""
		return self.at(self.path_handle.path[:-1])


	def at_children(self) -> PDMultiHandle:
		"""
		Return a PDMultiHandle that refers to all the children of the current
		path.
		"""
		return self.at(self.path_handle.path + ["*"])


	############################################################################
	# Getters
	############################################################################


	def get(self, default=None) -> list | dict | Any:
		"""
		Get the actual value at the given path.
		If the path is vaild but does not exist, return None (default).
		If the path is invalid (e.g. accessing string key on list), raise an
		error.

		Example:
		>>> d = {"a": {"b": {"c": [1]}}}
		>>> pd(d).at("a/b/c").get()    # -> [1] (Valid path)
		>>> pd(d).at("a/b/d").get()    # -> None (Valid path, but does not exist)
		>>> pd(d).at("a/b/c/d").get()  # -> KeyError (Invalid path - cannot get key "d" on a list)
		>>> pd(d).at("a/b/c/0").get()  # -> 1 (Valid path)

		Shorthand syntax:
		>>> pd(d).at("a/b/c")[:]
		You can use [:] to get the value at the current path.
		Beware: using the subscript [...] will move the handle back to the root
		of the data.

		:param default: The default value to return if the path is valid but
		does not exist.
		"""
		# Iterate over the path to safely get the value
		current = self.data
		for key in self.path_handle:
			current = utils.guarded_get(current, key)
			if current is None:
				return default
		return current


	def get_root(self) -> list | dict:
		"""
		Get the original data that was passed to the first PDHandle
		"""
		return self.root_data


	def get_at(self, *path) -> list | dict | Any:
		"""
		Get the value at the given path.
		"""
		return self.at(*path).get()


	############################################################################
	# Setters
	############################################################################


	def set(self, value) -> PDHandle:
		if value is None:
			return self

		# If handle is at root, replace the whole data
		if len(self.path_handle) == 0:
			if isinstance(self.data, dict) and isinstance(value, dict):
				self.data.clear()
				self.data.update(value)
				return self
			if isinstance(self.data, list) and isinstance(value, list):
				self.data.clear()
				self.data.extend(value)
				return self
			raise TypeError("PathDict set: At the root level, you can only set a dict to a dict or a list to a list")

		# Iterate over all keys except the last one
		current = self.data
		for key in self.path_handle[:-1]:
			current = utils.guarded_descent(current, key)

		if not isinstance(current, (dict, list)):
			raise KeyError("PathDict set: Only dicts and lists can be set")

		key = self.path_handle[-1]
		if isinstance(current, dict):
			try:
				current[key] = value
			except (ValueError, IndexError) as e:
				raise KeyError(f"PDHandle.set: invalid path {self.path_handle}") from e
		elif isinstance(current, list):
			try:
				current[int(key)] = value
			except (ValueError, IndexError, TypeError) as e:
				raise KeyError(f"PDHandle.set: invalid path {self.path_handle}") from e

		return self


	def map(self, f: Callable) -> PDHandle:
		"""
		Map the result of f to the value at path previously set by ".at(path)".

		:return: The handle itself for further operations.
		"""
		self.set(f(self.get()))
		return self


	def mapped(self, f: Callable) -> PDHandle:
		"""
		Makes a copy of your root data, moves the handle to the previously
		set path, applies map with f at that path, and returns the handle.
		"""
		current_handle = self.path_handle
		return self.at().copy().at(current_handle.path).map(f)


	############################################################################
	# Filter
	############################################################################


	def filter(self, f: Callable) -> PDHandle:
		"""
		At the current path only keep the elements for which f(key, value)
		is True for dicts, or f(value) is True for lists.
		"""
		if isinstance(self.data, dict):
			self.data = {k: v for k, v in self.data.items() if f(k, v)}
		elif isinstance(self.data, list):
			self.data = [x for x in self.data if f(x)]
		else:
			raise TypeError("PathDict filter: must be applied to a dict or list")
		self.root_data = self.data
		return self


	def filtered(self, f: Callable) -> PDHandle:
		"""
		Like filter, but does not modify the dict,
		but creates a copy with filter applied to it.
		"""
		copy = self.copy()
		copy.filter(f)
		return copy



	# def aggregate(self, *path, init=None, f: Callable = None):
	# 	"""
	# 		Aggregate a value starting with init at the given path.
	# 		f takes 3 arguments: key, values, and agg (initialized with init).
	# 	"""
	# 	path_val = self[path]
	# 	if not isinstance(path_val, PathDict):
	# 		raise LookupError("Aggregate only works on dicts")
	# 	agg = init
	# 	for k, v in path_val.items():
	# 		agg = f(k, v, agg)
	# 	return agg



	############################################################################
	#### Standard dict methods
	############################################################################

	# def keys(self):
	# 	return self.data.keys()


	# def values(self):
	# 	return self.data.values()


	# def items(self):
	# 	return self.data.items()


	# def __iter__(self):
	# 	return iter(self.data)


	def __repr__(self) -> str:
		"""
			Returns a pretty indented string representation.
		"""
		data = json.dumps(self.data, indent=4, sort_keys=True, default=str)
		root_data = json.dumps(self.data, indent=4, sort_keys=True, default=str)
		return f"PDHandle({data = },\n{root_data = },\n{self.path_handle = })"


	def __getitem__(self, path):
		at = self.at(*path) if isinstance(path, tuple) else self.at(path)
		res = at.get()
		self.at_root()
		return res


	def __setitem__(self, path, value):
		at = self.at(*path) if isinstance(path, tuple) else self.at(path)
		at.map(value) if callable(value) else at.set(value)
		self.at_root()

	def __contains__(self, *path):
		try:
			return self.at(*path).get() is not None
		except KeyError:
			return False


# Import PDMultiHandle at the end of the file to avoid circular imports
from . pd_multi_handle import PDMultiHandle
