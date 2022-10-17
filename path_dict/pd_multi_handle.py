from __future__ import annotations
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
			print("❤️")
			for path in self.path_handle.expand(self.root_data):
				print(path.path)
			for path in self.path_handle.expand(self.root_data):
				data = PDHandle(
					self.root_data,
					str_sep=self.path_handle.str_sep,
					raw=self.path_handle.raw
				).at(path).get()
					# TODO: Automatically recognize if the user wanta the path
					# as a string or list
				res.append((tuple(path.path), data) if include_paths else data)
			return res

		else:
			# as_type == "dict"
			res = {}
			for path in self.path_handle.expand(self.root_data):
				res[tuple(path.path)] = PDHandle(self.root_data, path).at(path).get()
			return res
