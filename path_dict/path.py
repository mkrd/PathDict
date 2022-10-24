from __future__ import annotations
import copy
from . utils import get_nested_keys_or_indices


class Path:
	path: list[str]
	str_sep: str
	raw: bool


	def __init__(self, *path, str_sep="/", raw=False):
		# Careful, if the kwargs are passed as positional agrs, they are part of the path
		self.str_sep = str_sep
		self.raw = raw

		# path is, whitout exceptions, always a tuple

		if len(path) == 1 and isinstance(path[0], list):
			# If the path is a list, then we are good to go
			self.path = path[0]
		else:
			# In raw mode, a tuple is considered a key
			self.path = [path] if raw else list(path)


		# If the contains strings with str_sep, split them up if not in raw mode
		if not self.raw:
			new_path = []
			for key in self.path:
				if isinstance(key, str) and str_sep in key:
					new_path.extend(key.split(str_sep))
				else:
					new_path.append(key)
			self.path = new_path

		# Clean up empty strings
		self.path = [x for x in self.path if x != ""]


	def __repr__(self) -> str:
		return f"Path(path={self.path}, str_sep={self.str_sep}, raw={self.raw})"


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


	def copy(self, replace_path=None, replace_str_sep=None, replace_raw=None) -> Path:
		path_copy = list(self.path) if replace_path is None else replace_path
		str_sep_copy = str(self.str_sep) if replace_str_sep is None else replace_str_sep
		raw_copy = self.raw if replace_raw is None else replace_raw
		return Path(path_copy, str_sep=str_sep_copy, raw=raw_copy)


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
		paths = paths if paths != [[]] else []
		return [Path(path, str_sep=self.str_sep, raw=self.raw) for path in paths]
