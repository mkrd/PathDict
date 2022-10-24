from __future__ import annotations
from typing import Any, Callable
from . path import Path
from . pd_handle import PDHandle


class PDMultiHandle:
	path_handle: Path
	root_data: dict | list


	def __init__(self, data: dict | list, path: Path):
		self.path_handle = path
		self.root_data = data


	def __repr__(self) -> str:
		return f"PDMultiHandle({self.root_data = }, {self.path_handle = })"


	############################################################################
	# Setters
	# Setters ALWAYS return a value
	############################################################################


	def gather(self, as_type="list", include_paths=False) -> dict | list:
		"""
		Get the actual value at the given path.

		:param as_pd: If true, return a PDHandle on the result. Else, return the dict or list itself.
		:param as_type: If list, return PDHandle on list of values. If dict, return PDHandle on dict that looks like {tuple(path): value}
		:param include_paths: If true and as_type is list, return a list of (path, value) tuples instead of just values.
		:return: PDHandle on the result.
		"""
		if as_type not in ["list", "dict"]:
			raise ValueError("Can only return as dict or list, not both")

		handle = PDHandle(self.root_data, self.path_handle)
		if as_type == "list":
			res = []
			for path in self.path_handle.expand(self.root_data):
				data = handle.at(path.path).get()
				res.append((tuple(path.path), data) if include_paths else data)
		# as_type == "dict"
		else:
			res = {}
			for path in self.path_handle.expand(self.root_data):
				res[tuple(path.path)] = handle.at(path.path).get()
		return res


	def gather_pd(self, as_type="list", include_paths=False) -> PDHandle:
		data = self.gather(as_type=as_type, include_paths=include_paths)
		return PDHandle(data, self.path_handle.copy(replace_path=[]))

	############################################################################
	# Setters
	# Setters ALWAYS return a handle, not the value.
	############################################################################


	def map(self, f: Callable) -> PDHandle:
		"""
		Map the result of f to the value at path previously set by ".at(path)".

		:return: The handle itself for further operations.
		"""
		for path in self.path_handle.expand(self.root_data):
			PDHandle(self.root_data, path).map(f)
		return PDHandle(self.root_data, self.path_handle)


	def reduce(self, f: Callable, aggregate: Any, as_type="list", include_paths=False) -> Any:
		"""
		Get all values of the given multi-path, and reduce them using f.
		"""
		return self.gather_pd(as_type=as_type, include_paths=include_paths).reduce(f, aggregate)


	############################################################################
	#### Filter
	############################################################################


	def filter(self, f: Callable, as_type="list", include_paths=False) -> PDHandle:
		"""
		At the current path only keep the elements for which f(key, value)
		is True for dicts, or f(value) is True for lists.
		"""
		return self.gather_pd(as_type=as_type, include_paths=include_paths).filter(f)


	# def filtered(self, f: Callable[[Any], bool], as_type="list", include_paths=False) -> PDHandle:
	# 	raise NotImplementedError


	############################################################################
	#### Useful shorthands
	############################################################################


	def sum(self) -> Any:
		"""
		Sum all values at the given multi-path.
		"""
		return sum(self.gather())


	def set(self, value: Any) -> PDHandle:
		for path in self.path_handle.expand(self.root_data):
			PDHandle(self.root_data, path).set(value)
		return self


	############################################################################
	#### Standard dict methods
	############################################################################
