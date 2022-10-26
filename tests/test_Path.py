from path_dict.path import Path


def test_Path():
	path = Path("users/1/friends")
	assert path.path == ["users", "1", "friends"]
	assert len(path) == 3
	assert Path("test/*").has_wildcards
	# A Path without wildcards expands to a list of itself
	assert path.expand({}) == [path]
