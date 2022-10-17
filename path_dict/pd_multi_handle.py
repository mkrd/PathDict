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
				# TODO: Automatically recognize if the user wanta the path
				# as a string or list
				res.append((tuple(path.path), data) if include_paths else data)
			return res

		else:
			# as_type == "dict"
			res = {}
			for path in self.path_handle.expand(self.root_data):
				res[tuple(path.path)] = PDHandle(self.root_data, path).get()
			return res



	# def filtered(self, f: Callable[[Any], bool], as_type="list", include_paths=False) -> PDHandle:
	# 	if as_type not in ["list", "dict"]:
	# 		raise ValueError("Can only return as dict or list, not both")

	# 	if as_type == "list":
	# 		res = []
	# 		for path in self.path_handle.expand(self.root_data):
	# 			data = PDHandle(
	# 				self.root_data,
	# 				str_sep=self.path_handle.str_sep,
	# 				raw=self.path_handle.raw
	# 			).at(path).get()
	# 			# TODO: Automatically recognize if the user wanta the path
	# 			# as a string or list
	# 			if f(data):
	# 				res.append((tuple(path.path), data) if include_paths else data)
	# 		return res

	# 	else:
	# 		# as_type == "dict"
	# 		res = {}
	# 		for path in self.path_handle.expand(self.root_data):
	# 			data = PDHandle(self.root_data).at(path).get()
	# 			if f(data):
	# 				res[tuple(path.path)] = data
	# 		return res


	# def reduce(self, f: Callable[[Any, Any], Any], initial=None) -> PDHandle:
	# 	"""
	# 	Reduce the values at the given path with the given function.
	# 	"""
	# 	for path in self.path_handle.expand(self.root_data):
	# 		data = PDHandle(self.root_data, path).at(path).get()
	# 		initial = f(initial, data)
	# 	return initial


	# def reduced(self, f: Callable[[Any, Any], Any], initial=None) -> PDHandle:
	# 	"""
	# 	Reduce the values at the given path with the given function.
	# 	"""
	# 	copy = self.copy()
	# 	copy.reduce(f, initial)
	# 	return copy
