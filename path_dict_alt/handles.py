from __future__ import annotations
from typing import Any, Callable
import copy
from .path import Path


class PDHandle():
	data: dict | list | Any

	def __init__(self, data: dict | list, str_sep="/", raw=False) -> None:
		"""
		A PDHandle always refers to a dict or list.
		"""

		print(f"🟡PDHandle.__init__: {type(data) = }")

		if not isinstance(data, (dict, list)):
			raise TypeError("PathDict init: data argument must be a dict or list")

		self.root_data = data  # The original data that was passed to the first PDHandle
		self.data = data
		self.path_from_root = Path([], str_sep=str_sep, raw=raw)


	def at(self, *path, str_sep=None, raw=None) -> PDHandle | PDMultiHandle:
		"""
		Calling at() returns a handle at the given path.
		This handle provides functions to do or get something at the path.
		"""
		print(f"🟡PDHandle.at: {path = }")
		self.path_from_root = Path(*path,
			str_sep=str_sep or self.path_from_root.str_sep,
			raw=raw or self.path_from_root.raw,
		)

		if self.path_from_root.has_wildcards:
			return PDMultiHandle(self.root_data, self.path_from_root)
		return self

	def at_root(self) -> PDHandle:
		return self.at()


	def get(self, default=None) -> Any:
		"""
		Get the actual value at the given path.
		"""
		# Iterate over the path to safely get the value
		current = self.data
		for key in self.path_from_root:
			if isinstance(current, list):
				if not isinstance(key, int):
					raise KeyError("PDHandle get(): key must be an int for lists")
				if key >= len(current):
					raise IndexError("PDHandle get(): list key out of range")
				current = current[key]
			elif isinstance(current, dict):
				if key not in current:
					return default
				current = current[key]
			else:
				raise KeyError(
					f"The path {path} is not a stack of nested "
					f"dicts (value at key {key} has type {type(current)})"
				)
		return current


	def get_root(self) -> list | dict:
		"""
		Get the original data that was passed to the first PDHandle
		"""
		return self.root_data


	def root(self) -> PDHandle:
		"""
		Get a PDHandle on the root data.
		Useful if you are in a nested handle but also want to do something on the root data.

		Example:
		>>> d = {"a": {"b": {"c": 1}}}
		>>> pd(d).at("a/b").filter(lambda k,v: v > 1).root().filter(lambda k,v: k == "a").get()
		"""
		return PDHandle(self.root_data)





	def deepcopy(self) -> PDHandle:
		return PDHandle(
			copy.deepcopy(self.data),
			str_sep=self.path_from_root.str_sep,
			raw=self.path_from_root.raw
		)



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
		return self


	def filtered(self, *path, f: Callable = None):
		"""
			Like filter, but does not modify the dict,
			but creates a deepcopy with filter applied to it.
		"""
		deepcopy = self.deepcopy
		deepcopy.filter(*path, f=f)
		return deepcopy


	# def map(f: Callable):
	# 	"""
	# 	applyies f to all values at path
	# 	If it is applied on a list, f looks like: f = lambda ele: return new_ele
	# 	If it is applied on a dict, f looks like: f = lambda key, val: return (new_val, new_key)
	# 	"""
	# 	raise NotImplementedError

	# def mapped(f: Callable):
	# 	raise NotImplementedError


	def set(self, value) -> PDHandle:
		if value is None:
			return self
		if len(self.path_from_root) == 0:
			if isinstance(self.data, dict) and isinstance(value, dict):
				self.data.clear()
				self.data.update(value)
				return self
			if isinstance(self.data, list) and isinstance(value, list):
				self.data.clear()
				self.data.extend(value)
				return self
			raise TypeError("PathDict set: At the root level, you can only set a dict to a dict or a list to a list")




		current = self.data
		for key in self.path_from_root[:-1]:
			if isinstance(current, dict):
				current.setdefault(key, {})
				current = current[key]
			elif isinstance(current, list):
				current = current[key]
			else:
				raise KeyError("Can't set the key of a non-dict")

		if not isinstance(current, (dict, list)):
			raise KeyError("Only dicts and lists can be set")
		current[self.path_from_root[-1]] = value
		return self



	def apply(self, f: Callable):
		"""
		Apply f to the value at the given path.
		"""
		self.set(f(self.get()))

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


	def __getitem__(self, path):
		at = self.at(*path) if isinstance(path, tuple) else self.at(path)
		res = at.get()
		self.at_root()
		return res


	def __setitem__(self, path, value):
		at = self.at(*path) if isinstance(path, tuple) else self.at(path)
		at.apply(value) if callable(value) else at.set(value)
		self.at_root()




class PDMultiHandle:
	def __init__(self, data: dict | list, path: Path):
		self.path_from_root = path
		self.root_data = data






	def get(self, *path, as_dict=True, as_list=False, include_paths=True) -> dict | list:
		"""
		Get the actual value at the given path.
		"""
		if as_dict and as_list:
			raise ValueError("Can only return as dict or list, not both")

		if as_dict and not include_paths:
			raise ValueError("Can only return as dict if include_paths is True")

		if as_list:
			res = []
			for path in self.path_from_root.expand(self.root_data):
				if include_paths:
					data = PDHandle(self.root_data, path).at(path).get()
					# TODO: Automatically recognize if the user wanta the path
					# as a string or list
					res.append((path.path, data))
				else:
					res.append(PDHandle(self.root_data, path).at(path).get())
			return res

		if as_dict:
			res = {}
			for path in self.path_from_root.expand(self.root_data):
				res[path.path] = PDHandle(self.root_data, path).at(path).get()
			return res
