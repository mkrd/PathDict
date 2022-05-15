from importlib.resources import path
from typing import Type
from path_dict import PathDict
import copy
import pytest



# def colored_str_by_color_code(s, color_code):
# 	res = "\033["
# 	res += f"{color_code}m{s}"
# 	res += "\033[0m"
# 	return res



# class test:
# 	""" A decorator that runs tests automatically and provides teardown and setup """
# 	def __init__(self, setup: Callable = lambda: None, teardown: Callable = lambda: None):
# 		self.setup = setup
# 		self.teardown = teardown

# 	def __call__(self, method):
# 		self.setup()
# 		try:
# 			t1 = time.time()
# 			method()
# 			t2 = time.time()
# 			ms = f"{((t2 - t1) * 1000):.1f}ms"
# 			print(colored_str_by_color_code(f"Test {method.__name__}() finished in {ms}", 92))
# 		except AssertionError:
# 			print(colored_str_by_color_code(f"Test {method.__name__}() failed!", 91))
# 			print(colored_str_by_color_code(traceback.format_exc(), 91))
# 			raise
# 		except BaseException:
# 			raise
# 		finally:
# 			self.teardown()


# Dict for testing purposes
users = {
	"total_users": 3,
	"premium_users": [1, 3],
	"users": {
		"1": {
			"name": "Joe",
			"age": 22,
		},
		"2": {
			"name": "Ben",
			"age": 49
		},
		"3": {
			"name": "Sue",
			"age": 32,
		},
	},
	"follows": [
		["Ben", "Sue"],
		["Joe", "Ben"],
		["Ben", "Joe"],
	]
}


def test_deepcopy():
	# Test deepcopy with object
	class TestObject():
		def __init__(self, data):
			self.data = data

		def __repr__(self):
			return f"TestObject({self.data})"

	pd = PathDict({})
	pd["test", "test"] = TestObject({"test": "test"})

	assert str(pd) == """PathDict({\n    "test": {\n        "test": "TestObject({'test': 'test'})"\n    }\n})"""

	try:
		pd_deepcopy = pd.deepcopy
		assert str(pd) == str(pd_deepcopy)
	except Exception:
		raise AssertionError("pd.deepcopy failed")


def test_referencing():
	p_table = {
		"p1": PathDict(),
		"p2": PathDict(),
		"p3": PathDict({}),
		"p4": PathDict({}),
	}
	for a in p_table:
		for b in p_table:
			if a != b:
				assert p_table[a].data is not p_table[b].data

	shared_d1 = {}
	p1_with_shared_d1 = PathDict(shared_d1)
	p2_with_shared_d1 = PathDict(shared_d1)
	assert p1_with_shared_d1.data is p2_with_shared_d1.data

	p_with_deep_copy_d1 = PathDict(shared_d1, deep_copy=True)
	p3_with_shared_d1 = PathDict(shared_d1)

	# Deep copy should have its own value
	assert p_with_deep_copy_d1.data is not p1_with_shared_d1.data
	# Ensure deep_copy is set to False again
	assert p3_with_shared_d1.data is p1_with_shared_d1.data


def test_initialization():
	# Pre-checks
	assert not isinstance(None, PathDict)
	assert PathDict().data == {}
	# Empty
	pd_empty = PathDict({})
	assert pd_empty.dict == {}
	# Wrong inits
	for wrong in ["", 1, [1]]:
		with pytest.raises(TypeError):
			PathDict(wrong)
	# Init with PathDict
	init_pd = PathDict({"test": 1})
	pd_from_pd = PathDict(init_pd)
	assert init_pd == pd_from_pd
	assert init_pd.data is pd_from_pd.data
	# Init with dict
	init_dict = copy.deepcopy(users)
	pd = PathDict(init_dict)
	assert pd.data is pd.dict
	assert pd.dict is init_dict
	assert pd is not init_dict
	assert pd == init_dict
	assert pd["users"].dict is init_dict["users"]
	assert isinstance(pd["premium_users"], list)
	assert pd["premium_users"] is init_dict["premium_users"]
	# Deep copy behavior
	dc_pd = PathDict(users, deep_copy=True)
	assert dc_pd.dict is not users
	dc_pd_deepcopy = dc_pd.deepcopy
	assert dc_pd is not dc_pd_deepcopy


def test_list_gets():
	users_dict = copy.deepcopy(users)
	users_pd = PathDict(users_dict)
	assert users_pd[["users", "2", "age"]] == 49


def test_get_path():
	users_dict = copy.deepcopy(users)
	users_pd = PathDict(users_dict)
	assert users_pd["total_users"] == 3
	assert users_pd["users", "1", "name"] == "Joe"
	# Non existent but correct paths return None
	assert users_pd["users", "-1", "name"] is None
	# Non path returns None
	with pytest.raises(TypeError):
		users_pd.get_path(2)

	assert users_pd[2] is None
	# If value is not a dict, return that value
	assert isinstance(users_pd["follows"], list)
	# If value is a dict, return a PathDict
	assert isinstance(users_pd["users"], PathDict)
	assert users_pd["users"].dict is users_dict["users"]
	# Wrong path accesses, eg. get key on list, raise an exception
	with pytest.raises(KeyError):
		users_pd["follows", 0]


def test_filter():
	users_pd = PathDict(users, deep_copy=True)

	users_filtered = users_pd.filtered("users", f=lambda k, v: v["age"] <= 30)
	assert users_filtered["users"] == {
		"1": {
			"age": 22,
			"name": "Joe"
		}
	}
	assert isinstance(users_filtered, PathDict)

	premium_users = users_pd["users"].filtered(f=lambda k, v: int(k) in users_pd["premium_users"])
	assert isinstance(premium_users, PathDict)

	assert premium_users == {
		"1": {
			"age": 22,
			"name": "Joe"
		},
		"3": {
			"age": 32,
			"name": "Sue"
		}
	}

	follows_includes_joe = users_pd.filtered("follows", f=lambda e: "Joe" in e)
	assert isinstance(follows_includes_joe["follows"], list)
	assert follows_includes_joe["follows"] == [
		["Joe", "Ben"],
		["Ben", "Joe"],
	]



def test_aggregate():
	users_pd = PathDict(users, deep_copy=True)
	users_ages = users_pd.aggregate("users", init=0, f=lambda k, v, a: a + v["age"])
	assert users_ages == 103


def test_PathDict():
	d = {
		"total_users": 3,
		"premium_users": [1, 3],
		"users": {
			"1": {"name": "Joe", "age": 22},
			"2": {"name": "Ben", "age": 49},
			"3": {"name": "Sue", "age": 32},
		},
		"follows": [
			["Ben", "Sue"],
			["Joe", "Ben"],
			["Ben", "Joe"],
		]
	}
	o = PathDict(d)
	# Getting attributes
	assert o["total_users"] == 3
	assert o["not_exists"] is None
	assert o["users"] == {
		"1": {"name": "Joe", "age": 22},
		"2": {"name": "Ben", "age": 49},
		"3": {"name": "Sue", "age": 32}}
	assert o["users", "1"] == {"name": "Joe", "age": 22}
	assert o["users", "3", "name"] == "Sue"
	assert o["follows"][0] == ["Ben", "Sue"]
	# Setting attributes
	o["total_users"] = 4
	assert o["total_users"] == 4
	o["users", "3", "age"] = 99
	assert o["users", "3", "age"] == 99
	o["users", "4"] = {"name": "Ron", "age": 62}
	assert o["users", "4"] == {"name": "Ron", "age": 62}
	o["1", "1", "1", "1"] = 1
	assert o["1", "1", "1"] == {"1": 1}
	# Apply functions
	o["follows"] = lambda x: [list(reversed(e)) for e in x]
	assert o["follows"] == [
		["Sue", "Ben"],
		["Ben", "Joe"],
		["Joe", "Ben"]]

	assert o.dict == {
		"1": {"1": {"1": {"1": 1}}},
		"total_users": 4,
		"premium_users": [1, 3],
		"users": {
			"1": {"name": "Joe", "age": 22},
			"2": {"name": "Ben", "age": 49},
			"3": {"name": "Sue", "age": 99},
			"4": {"name": "Ron", "age": 62},
		},
		"follows": [
			["Sue", "Ben"],
			["Ben", "Joe"],
			["Joe", "Ben"]]
	}


def test_star_operations():
	winners_original = PathDict({
		"2017": {
			"podium": {
				"17-place-1": {"name": "Joe", "age": 22},
				"17-place-2": {"name": "Ben", "age": 13},
				"17-place-3": {"name": "Sue", "age": 98},
			},
			"prices_list": ["Car", "Bike", "Plane"],
		},
		"2018": {
			"podium": {
				"18-place-1": {"name": "Bernd", "age": 50},
				"18-place-2": {"name": "Sara", "age": 32},
				"18-place-3": {"name": "Jan", "age": 26},
			},
			"prices_list": ["Beer", "Coffee", "Cigarette"],
		},
	})


	# Get names of all winners
	winners = winners_original.deepcopy
	assert winners["*", "podium", "*", "name"] == [
		"Joe", "Ben", "Sue", "Bernd", "Sara", "Jan"
	]



	# Increment age of all users by 1
	winners = winners_original.deepcopy
	winners["*", "podium", "*", "age"] = lambda x: x + 1
	assert winners["2017", "podium", "17-place-1", "age"] == 23
	assert winners["2017", "podium", "17-place-2", "age"] == 14
	assert winners["2017", "podium", "17-place-3", "age"] == 99
	assert winners["2018", "podium", "18-place-1", "age"] == 51
	assert winners["2018", "podium", "18-place-2", "age"] == 33
	assert winners["2018", "podium", "18-place-3", "age"] == 27

	# winners = winners_original.deepcopy
	# winners["*", "podium", "*"] = lambda x: x["age"] += 1 if "B" in x["name"] else x["age"] == 0

	# print("GO")
	# assert AssertionError()
	# print(winners)

	# names_2017 = winners["2017", "podium", "*", "name"]
	# print(names_2017)
	# assert names_2017 == ["Joe", "Ben", "Sue"]


def test_contains():
	users_dict = copy.deepcopy(users)
	users_pd = PathDict(users_dict)
	assert "" not in users_pd
	assert "total_users" in users_pd
	assert ["premium_users", 1] not in users_pd
	assert ["users", "1"] in users_pd
	assert ["users", "999999"] not in users_pd
	assert ["users", "1", "name"] in users_pd
	assert ["users", "999999", "name"] not in users_pd
	assert ["users", "1", "name", "joe"] not in users_pd
	assert ["users", "1", "name", "joe", "Brown"] not in users_pd  # too many paths
