from __future__ import annotations
from collections import UserDict
from typing import Union, Any
import json
import copy


class PathDict(UserDict):
	"""
		PathDict wraps a dict, with extra functions like
		working with paths.
	"""

	# FIX wrong behavior of standard library
	# <a>.pop(<b>, None) returns key error, if <b> not in <a>.
	# This fixes it.
	def pop(self, key, *args):
		return self.data.pop(key, *args)




	def __init__(self, data: dict = {}, deep_copy: bool = False):
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
		else:
			raise Exception("PathDict init: data must be a dict")
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
		dump = json.dumps(self.data, indent=2, sort_keys=True)
		return f"PathDict({dump})"


	def get_path(self, path: list) -> Union[PathDict, Any]:
		"""
			Get the value of the json object at the given path
			<PathDict>.get_path(["1", "2", "3"]) is like calling
			<dict>["1"]["2"]["3"].
			Empty paths ([]) or invalid paths return None.
		"""
		if not isinstance(path, list):
			return None
		if path == []:
			return self
		current = self.data
		for attr in path:
			if not isinstance(current, dict):
				raise Exception(f"Your path is not a path of dicts (value at key {attr} is of type {type(current)})")
			if attr not in current:
				return None
			current = current[attr]
		if isinstance(current, dict):
			return PathDict(current)
		return current


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
		last_path_attr = path.pop()
		for attr in path:
			if not isinstance(current, dict):
				raise Exception("Can't set the key of a non-dict")
			current.setdefault(attr, {})
			current = current[attr]
		if isinstance(value, PathDict):
			current[last_path_attr] = value.data
		else:
			current[last_path_attr] = value


	def apply_at_path(self, path: list, function: callable):
		"""
			At a given path, apply the given function
			to the value at that path.
		"""
		value = self.get_path(path)
		self.set_path(path, value=function(value))


	def __getitem__(self, path) -> Any:
		""" Subscript for <PathDict>.get_path() """
		# If PathDict["key1"], then path="key1"
		# PathDict["key1", "key2"], then path=tuple("key1", "key2")
		# We want path to be a list in any case
		path = list(path) if isinstance(path, tuple) else [path]
		return self.get_path(path)


	def __setitem__(self, path, value):
		""" Subscript for <PathDict>.get_path() and <PathDict>.apply_at_path() """
		path = list(path) if isinstance(path, tuple) else [path]
		if callable(value):
			self.apply_at_path(path, function=value)
		else:
			self.set_path(path, value=value)


	def filter(self, *path, f: callable = None):
		"""
			Only keep the mapping or list elements at path
			that satisfy f.
			For dicts: filter(path, f=lambda key, val: ...)
			For lists: filter(path, f=lambda ele: ...)
		"""
		path_val = self[path]
		if isinstance(path_val, PathDict):
			filtered = PathDict({})
			for k, v in path_val.items():
				if f(k, v):
					filtered[k] = v
			self[path] = filtered
		elif isinstance(path_val, list):
			self[path] = [x for x in list(path_val) if f(x)]


	def filtered(self, *path, f: callable = None):
		"""
			Like filter, but does not modify this object,
			but returns a filtered deepcopy.
		"""
		deepcopy = self.deepcopy
		deepcopy.filter(*path, f=f)
		return deepcopy


	def aggregate(self, *path, init=None, f: callable = None):
		"""
			Aggregate a value starting with init at the given path.
			f takes 3 arguments: key, values, and agg (initialized with init).
		"""
		path_val = self[path]
		if not isinstance(path_val, PathDict):
			raise Exception("Aggregate only works on dicts")
		agg = init
		for k, v in path_val.items():
			agg = f(k, v, agg)
		return agg