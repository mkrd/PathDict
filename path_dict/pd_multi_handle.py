from __future__ import annotations
from typing import Any, Callable
from . path import Path
from . pd_handle import PDHandle


class PDMultiHandle:
	def __init__(self, data: dict | list, path: Path):
		self.path_handle = path
		self.root_data = data


	def get_all(self, as_type="list", include_paths=False) -> dict | list:
		"""
		Get the actual value at the given path.
		"""
		if as_type not in ["list", "dict"]:
			raise ValueError("Can only return as dict or list, not both")

		if as_type == "list":
			res = []
			for path in self.path_handle.expand(self.root_data):
				data = PDHandle(self.root_data, path).get()
				# TODO: Automatically recognize if the user wants the path
				# as a string or list
				res.append((tuple(path.path), data) if include_paths else data)
			return res

		else:
			# as_type == "dict"
			res = {}
			for path in self.path_handle.expand(self.root_data):
				res[tuple(path.path)] = PDHandle(self.root_data, path).get()
			return res


	def map(self, f: Callable) -> PDHandle:
		"""
		Map the result of f to the value at path previously set by ".at(path)".

		:return: The handle itself for further operations.
		"""
		for path in self.path_handle.expand(self.root_data):
			PDHandle(self.root_data, path).map(f)
		return PDHandle(self.root_data, self.path_handle)



	# def filtered(self, f: Callable[[Any], bool], as_type="list", include_paths=False) -> PDHandle:
	# 	raise NotImplementedError


	# def reduce(self, f: Callable[[Any, Any], Any], initial=None) -> PDHandle:
	# 	"""
	# 	Reduce the values at the given path with the given function.
	# 	"""

	# 	# for path in self.path_handle.expand(self.root_data):
	# 	# 	data = PDHandle(self.root_data, path).at(path).get()
	# 	# 	initial = f(initial, data)
	# 	# return initial
	# 	raise NotImplementedError


	# def reduced(self, f: Callable[[Any, Any], Any], initial=None) -> PDHandle:
	# 	"""
	# 	Reduce the values at the given path with the given function.
	# 	"""
	# 	# 	copy = self.copy()
	# 	# 	copy.reduce(f, initial)
	# 	# 	return copy
	# 	raise NotImplementedError
