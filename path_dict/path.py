from __future__ import annotations
from . utils import get_nested_keys_or_indices


class Path:
	path: list[str]
	raw: bool


	def __init__(self, *path, raw=False):
		# Careful, if the kwargs are passed as positional agrs, they are part of the path
		self.raw = raw

		# path is, whitout exceptions, always a tuple

		if len(path) == 1 and isinstance(path[0], list):
			# If the path is a list, then we are good to go
			self.path = path[0]
		else:
			self.path = list(path)

		# Clean up empty strings
		self.path = [x for x in self.path if x != ""]


	def __repr__(self) -> str:
		return f"Path(path={self.path}, raw={self.raw})"


	@property
	def has_wildcards(self):
		return "*" in self.path


	def __iter__(self):
		""" Iterate over path keys using a for in loop """
		return iter(self.path)


	def __len__(self):
		return len(self.path)


	def __getitem__(self, key):
		return self.path[key]


	def copy(self, replace_path=None, replace_raw=None) -> Path:
		path_copy = list(self.path) if replace_path is None else replace_path
		raw_copy = self.raw if replace_raw is None else replace_raw
		return Path(path_copy, raw=raw_copy)


	def expand(self, ref: dict | list) -> list[Path]:
		"""
		Expand the path to list[Path], using the ref as a reference.
		"""
		if not self.has_wildcards:
			return [self]

		paths = [[]]
		for key in self.path:
			if key != "*":
				# Extend all paths by the key if it is not "*"
				paths = [path + [key] for path in paths]
			else:
				# If key is "*", expand all paths by all keys at the respective path
				paths = [p + [k] for p in paths for k in get_nested_keys_or_indices(ref, p)]

		# Return empty list if no paths were found
		if paths == [[]]:
			return []
		return [Path(p, raw=self.raw) for p in paths]
