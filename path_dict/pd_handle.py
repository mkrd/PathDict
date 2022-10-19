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

	def __init__(self, data: dict | list, path: Path) -> None:
		"""
		A PDHandle always refers to a dict or list.
		It is used to get data or perform operations at a given path.
		When initialized, the current path is the root path.
		"""

		if not isinstance(data, (dict, list)):
			raise TypeError(
				f"PathDict init: data must be dict or list but is {type(data)} "
				f"({data})"
			)

		self.root_data = data  # The original data that was passed to the first PDHandle
		self.data = data
		self.path_handle = path


	def copy(self, from_root=False) -> PDHandle:
		"""
		Return a deep copy of the data at the current path or from the root.

		:param from_root: If True, copy the root data instead of the current.
		The current path handle will stay the same.
		"""
		path = self.path_handle.copy(path=None if from_root else [])
		copied_data = copy.deepcopy(self.data if from_root else self.get())
		return PDHandle(copied_data, path)



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
	# Getters ALWAYS return actual values, not handles.
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
	# Setters ALWAYS return a handle, not the value.
	############################################################################


	def set(self, value) -> PDHandle:
		# Setting nothing is a no-op
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

		key = self.path_handle[-1]
		if isinstance(current, dict):
			current[key] = value
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
	# Filter ALWAYS return a handle, not the value.
	############################################################################


	def filter(self, f: Callable) -> PDHandle:
		"""
		At the current path only keep the elements for which f(key, value)
		is True for dicts, or f(value) is True for lists.
		"""
		get_at_current = self.get()
		if isinstance(get_at_current, dict):
			return self.set({k: v for k, v in get_at_current.items() if f(k, v)})
		if isinstance(get_at_current, list):
			return self.set([x for x in get_at_current if f(x)])
		raise TypeError("PathDict filter: must be applied to a dict or list")



	def filtered(self, f: Callable) -> PDHandle:
		"""
		Shortcut for:
		>>> copy().filter(f)
		"""

		return self.copy().filter(f)


	############################################################################
	# Reduce
	############################################################################


	def reduce(self, f: Callable, aggregate=None) -> Any:
		"""
		Reduce a value starting with init at the given path.
		If at the selected path is a dict, the function f will be called with
		(key, value, aggregate) as arguments.
		If at the selected path is a list, the function f will be called with
		(value, aggregate) as arguments.
		"""

		agg = aggregate
		get_at_current = self.get()
		if isinstance(get_at_current, dict):
			for k, v in get_at_current.items():
				agg = f(k, v, agg)
			return agg
		if isinstance(get_at_current, list):
			for v in get_at_current:
				agg = f(v, agg)
			return agg
		raise TypeError("PathDict reduce: must be applied to a dict or list")


	def sum(self) -> Any:
		"""
		Sum the elements at the given path.
		"""
		get_at_current = self.get()
		if isinstance(get_at_current, dict):
			return sum(v for k, v in get_at_current.items())
		if isinstance(get_at_current, list):
			return sum(get_at_current)
		raise TypeError("PathDict sum: must be applied to a dict or list")


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
		return f"PDHandle({self.data = }, {self.root_data = }, {self.path_handle = })"


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