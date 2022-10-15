from __future__ import annotations
from collections import UserDict
from typing import Any, Callable
import json
import copy



class PathDict(UserDict):
	"""
		PathDict wraps a dict, with extra functions like
		working with paths.
	"""
	# Explicitly define data attribute
	data = None



	def pop(self, key, *args):
		# FIX wrong behavior of standard library of UserDict
		# <a>.pop(<b>, None) returns key error, if <b> not in <a>.
		# This fixes it.
		return self.data.pop(key, *args)



	def __init__(self, data: dict | PathDict = None, deep_copy: bool = False):
		"""
			Initialize with a dict or another PathDict.
			This will reference the original dict or PathDict,
			so changes will also happen to them.
			If you do not want this set deep_copy to True.
		"""
		if isinstance(data, PathDict):
			self.data = data.data
		elif isinstance(data, dict):
			self.data = data
		elif data is None:
			self.data = {}
		else:
			raise TypeError("PathDict init: data argument must be a dict or PathDict")

		# If deep_copy is True, make a deep copy of the data
		if deep_copy:
			self.data = copy.deepcopy(self.data)



	@property
	def dict(self) -> dict:
		"""
			Returns a reference to the internal dict.
		"""
		return self.data



	@property
	def deepcopy(self) -> PathDict:
		"""
			Create a complete copy of a PathDict
		"""
		return PathDict(self, deep_copy=True)



	def __repr__(self) -> str:
		"""
			Returns a pretty indented string representation.
		"""
		dump = json.dumps(self.data, indent=4, sort_keys=True, default=str)
		return f"PathDict({dump})"


	####
	####
	####
	####
	############################################################################
	#### Utils
	############################################################################


	def _convert_path_to_list(self, path) -> list:
		"""
		Check path type and convert to list type.
		"""
		# If tuple, convert to list
		if isinstance(path, tuple):
			return list(path)

		# If list, leave as is
		if isinstance(path, list):
			return path

		# Else, convert to single item list
		return [path]



	def _expand_star_path(self, path: list) -> list[list]:
		"""
			Expand the given path containing "*" to a list of paths where all "*" have been expanded by all keys.
		"""
		paths = [[]]
		for key in path:
			if key != "*":
				# Extend all paths by the key if it is not "*"
				paths = [path + [key] for path in paths]
			else:
				# If key is "*", expand all paths by all keys at the respective path
				paths = [p + [k] for p in paths for k in self.get_path(p).keys()]

		# Return empty list if no paths were found
		# paths = paths if paths != [[]] else []
		return paths


	####
	####
	####
	####
	############################################################################
	#### Getters
	############################################################################


	def get_path(self, path: list) -> PathDict | Any:
		"""
			Get the value of the json object at the given path
			<PathDict>.get_path(["1", "2", "3"]) is like calling
			<dict>["1"]["2"]["3"].
			Empty paths ([]) or invalid paths return None.
		"""
		if not isinstance(path, list):
			raise TypeError("PathDict.get_path: path must be a list")
		if not path:
			return self

		# Iterate over the path to safely get the value
		current = self.data
		for key in path:
			if not isinstance(current, dict):
				raise KeyError(
					f"The path {path} is not a stack of nested "
					f"dicts (value at key {key} has type {type(current)})"
				)
			if key not in current:
				return None
			current = current[key]
		if isinstance(current, dict):
			return PathDict(current)
		return current


	def __getitem__(self, path) -> Any | PathDict | list:
		""" Subscript for <PathDict>.get_path() """
		# We want path to be a list in any case
		path_list = self._convert_path_to_list(path)

		# Use normal get_path if no wildcards are used
		if "*" not in path_list:
			return self.get_path(path_list)

		# If wildcards are used, return a list of all values
		expanded_paths = self._expand_star_path(path_list)
		return [self.get_path(p) for p in expanded_paths]


	####
	####
	####
	####
	############################################################################
	#### Setters and Apply
	############################################################################


	def set_path(self, path: list, value=None):
		"""
			Set the value of the json object at the given path
			<PathDict>.set_path(["1", "2", "3"], value) is like calling
			<dict>["1"]["2"]["3"] = value.
			If a path does not exist, it will be created.
			Empty or invalid paths, or if value is None, do nothing.
		"""
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


	def set_at_star_path(self, path: list, value=None):
		# print(path, self._expand_star_path(path))
		for expanded_path in self._expand_star_path(path):
			self.set_path(expanded_path, value)


	def apply_at_star_path(self, path: list, function: Callable):
		"""
			At a given path, apply the given function
			to the value at that path.
		"""
		for expanded_path in self._expand_star_path(path):
			applied = function(self.get_path(expanded_path))
			self.set_path(expanded_path, value=applied)



	def __setitem__(self, path, value: Callable | Any):
		""" Subscript for <PathDict>.get_path() and <PathDict>.apply_at_star_path() """
		path = self._convert_path_to_list(path)
		if callable(value):
			self.apply_at_star_path(path, function=value)
		else:
			self.set_at_star_path(path, value=value)






	def filter(self, *path, f: Callable = None):
		"""
			Only keep the mapping or list elements at path
			that satisfy f.
			For dicts: filter(path, f=lambda key, val: ...)
			For lists: filter(path, f=lambda ele: ...)
		"""

		path_list = self._convert_path_to_list(path)

		# If the f=... kwarg is forgotten and the function is passed as the
		# last positional argument, we pop it from the path list and set it as f
		if len(path_list) > 0 and callable(path_list[-1]) and f is None:
			f = path_list.pop()

		path_val = self[path_list]
		if isinstance(path_val, PathDict):
			filtered = PathDict({})
			for k, v in path_val.items():
				if f(k, v):
					filtered[k] = v

			self[path_list] = filtered
		elif isinstance(path_val, list):
			self[path_list] = [x for x in list(path_val) if f(x)]


	def filtered(self, *path, f: Callable = None):
		"""
			Like filter, but does not modify this object,
			but returns a filtered deepcopy.
		"""
		deepcopy = self.deepcopy
		deepcopy.filter(*path, f=f)
		return deepcopy


	def aggregate(self, *path, init=None, f: Callable = None):
		"""
			Aggregate a value starting with init at the given path.
			f takes 3 arguments: key, values, and agg (initialized with init).
		"""
		path_val = self[path]
		if not isinstance(path_val, PathDict):
			raise LookupError("Aggregate only works on dicts")
		agg = init
		for k, v in path_val.items():
			agg = f(k, v, agg)
		return agg


	def __contains__(self, path) -> bool:
		"""Check if the path is contained."""
		path = self._convert_path_to_list(path)
		temp = self.dict
		for k in path:
			if not isinstance(temp, dict):
				return False

			if k not in temp:
				return False

			temp = temp[k]

		return True
