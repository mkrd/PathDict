from __future__ import annotations


def util_get_keys_nested(ref: dict | list, path: list):
	"""
	Get the keys of a nested dict at the given path.
	If the nested object is a list, the return a list of all list indices.
	If the path does not exist, return [].
	"""
	current = ref
	for key in path:
		if isinstance(current, dict):
			current = current.get(key, None)
		elif isinstance(current, list):
			try:
				current = current[key]
			except IndexError:
				current = None
		else:
			raise KeyError(
				f"The path {path} is not a stack of nested "
				f"dicts (value at key {key} has type {type(current)})"
			)
		if current is None:
			return []
	if isinstance(current, dict):
		return list(current.keys())
	if isinstance(current, list):
		return list(range(len(current)))


class Path:
	path: list[str]
	str_sep: str
	raw: bool


	def __init__(self, *path, str_sep="/", raw=False):
		print(f"🟢Path.__init__: path=(<{path}> {type(path)}) str_sep={str_sep} raw={raw}")
		self.str_sep = str_sep
		self.raw = raw

		if isinstance(path, tuple) and len(path) == 1 and isinstance(path[0], list):
			# If the path is a list, then we are good to go
			self.path = path[0]
		elif isinstance(path, tuple):
			if raw:
				# In raw mode, a tuple is considered a key
				self.path = [path]
			else:
				self.path = list(path)
		else:
			# Single item path
			self.path = [path]

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

		print("🟢 --->", self.path)


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
				paths = [p + [k] for p in paths for k in util_get_keys_nested(ref, p)]

		# Return empty list if no paths were found
		paths = paths if paths != [[]] else []
		return [Path(path) for path in paths]
