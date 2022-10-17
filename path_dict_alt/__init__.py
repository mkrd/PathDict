from __future__ import annotations
from collections import UserDict
from tkinter.messagebox import NO
from typing import Any, Callable
import json
import copy
import sys




def universal_path(path: tuple | list | str, str_sep=None, raw=False) -> list:
	"""
		Returns the path as a list or list of lists.
		:param: str_sep: The separator to use when splitting the path that then must be passed as a string
		:param: raw: If true, wildcards (*) will not be interpreted as such, but as the actual key value. Also, if the path is a tuple, it will remain a tuple

	"""

	# If the path is a string with separators, split it up
	if str_sep is not None:
		if not isinstance(path, str):
			raise TypeError("Path must be a string if str_sep is not None")
		return path.split(str_sep)

	if raw:
		if isinstance(path, tuple):
			return [path]
		else:



	# If tuple, convert to list
	if isinstance(path, tuple):
		return list(path)

	# If list, leave as is
	if isinstance(path, list):
		return path

	# Else, convert to single item list
	return [path]




class PathDictHandle():
	data: dict | list | Any

	def __init__(self, data: dict | list) -> None:
		if not isinstance(data, (dict, list)):
			raise TypeError("PathDict init: data argument must be a dict or list")
		self.root_data = data
		self.data = data

	def at(self, *path, str_sep=None, raw=False) -> PathDictHandle:

		self.path_from_root = universal_path(*path, str_sep, raw)

		for key in self.path_from_root:
			if isinstance(self.data, (dict, list)):
				self.data = self.data[key]
			else:
				raise TypeError("PathDict at: nested data must be a dict or list")

		return self

	def get(self, *path, default=None, str_sep=None, raw=False) -> Any:
		"""
		Get the actual value at the given path.
		"""
		return self.at(*path, str_sep, raw).data

	def get_root(self) -> list | dict:
		"""
		Get the original data that was passed to the first PathDictHandle
		"""
		return self.root_data

	def root(self) -> PathDictHandle:
		"""
		Get a PathDictHandle on the root data.
		Useful if you are in a nested handle but also want to do something on the root data.

		Example:
		>>> d = {"a": {"b": {"c": 1}}}
		>>> pd(d).at("a/b").filter(lambda k,v: v > 1).root().filter(lambda k,v: k == "a").get()
		"""
		return PathDictHandle(self.root_data)





	def deepcopy(self) -> PathDictHandle:
		self.data = copy.deepcopy(self.data)




	def filter(self, f: Callable) -> PathDictHandle:
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


	def map(f: Callable):
		"""
		applyies f to all values at path
		If it is applied on a list, f looks like: f = lambda ele: return new_ele
		If it is applied on a dict, f looks like: f = lambda key, val: return (new_val, new_key)
		"""
		raise NotImplementedError

	def mapped(f: Callable):
		raise NotImplementedError


	def set(self, *path, value, str_sep=None, raw=False) -> PathDictHandle:
		if not isinstance(path, list) or value is None:
			return
		if path == []:
			if isinstance(value, PathDict):
				self.data = value.data
			else:
				self.data = value
			return
		current = self.data
		last_path_key = path.pop()
		for key in path:
			if not isinstance(current, dict):
				raise KeyError("Can't set the key of a non-dict")
			current.setdefault(key, {})
			current = current[key]
		if not isinstance(current, dict):
			raise KeyError("Can't set the key of a non-dict")
		if isinstance(value, PathDict):
			current[last_path_key] = value.data
		else:
			current[last_path_key] = value


	############################################################################
	#### Standard dict methods
	############################################################################

	def keys(self): return self.data.keys()
	def values(self): return self.data.values()
	def items(self): return self.data.items()
	def __iter__(self): return iter(self.data)







class CallableModule():
	def __call__(self, x: dict | list) -> PathDictHandle:
		return PathDictHandle(x)



sys.modules[__name__] = CallableModule()


# deleted_posts = pd(crawler_output).at("posts").filtered(lambda x: x["meta", "deleted"]).get("posts")
