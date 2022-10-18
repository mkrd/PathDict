from path_dict import pd
import pytest
import copy


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


db = {
	"meta": {
		"version": 1,
	},
	"users": {
		"1": {
			"name": "John",
			"age": 20,
			"friends": ["2", "3"],
		},
		"2": {
			"name": "Jane",
			"age": 21,
			"friends": ["1", "3"],
		},
		"3": {
			"name": "Jack",
			"age": 22,
			"friends": ["1", "2"],
		},
	},
}


def test_Path():
	from path_dict.path import Path
	path = Path("users/1/friends")
	assert path.path == ["users", "1", "friends"]
	assert len(path) == 3
	assert Path("test/*").has_wildcards
	# A Path without wildcards expands to a list of itself
	assert path.expand({}) == [path]


def test_initialization():

	# Empty
	assert pd({}).get() == {}

	# Wrong inits
	for wrong in ["", 1, 1.0, True, None, (), set()]:
		with pytest.raises(TypeError):
			pd(wrong)

	# Check data
	init_dict = copy.deepcopy(users)
	p = pd(init_dict)
	assert p.data is init_dict
	assert p is not init_dict
	assert p.get() == init_dict
	assert p["users"] is init_dict["users"]
	assert isinstance(p["premium_users"], list)
	assert p["premium_users"] is init_dict["premium_users"]


def test_at():
	assert pd(db).at().path_handle.path == []
	assert pd(db).at([]).path_handle.path == []
	assert pd(db).at("users").path_handle.path == ["users"]
	assert pd(db).at(["users"]).path_handle.path == ["users"]
	assert pd(db).at("users", "1").path_handle.path == ["users", "1"]
	assert pd(db).at("users/1", "friends").path_handle.path == ["users", "1", "friends"]
	assert pd(db, str_sep="-").at("users-1", "friends").path_handle.path == ["users", "1", "friends"]
	assert pd(db).at(["users/1", "friends"]).path_handle.path == ["users", "1", "friends"]


def test_at_parent():
	assert pd(db).at("users/1").at_parent().path_handle.path == ["users"]
	pd(db).at_parent().get() is None


def test_at_children():
	assert pd(db).at("users").at_children().get_all() == [u for u in db["users"].values()]


def test_simple_get():
	assert pd(db).get() == db
	assert pd(db).at("").get() == db
	assert pd(db).at().get() == db
	assert pd(db).at("users/1/name").get() == "John"
	assert pd(db).at("users/9/name").get() is None
	assert pd(db).at(2).get() is None
	assert pd(db).at("users/9/name").get("default") == "default"


def test_referencing():
	j_table = {
		"j1": {},
		"j2": {},
		"j3": {},
		"j4": {},
	}

	for a in j_table:
		for b in j_table:
			p1, p2 = pd(j_table[a]).get(), pd(j_table[b]).get()
			assert p1 is not p2 if a != b else p1 is p2

	shared_dict = {}
	p1_shared_dict = pd(shared_dict)
	p2_shared_dict = pd(shared_dict)
	assert p1_shared_dict.data is p2_shared_dict.data

	# Deep copy should have its own value
	copy = pd(shared_dict).copy()
	assert copy.get() is not p1_shared_dict.get()


def test_get_path():
	users_dict = copy.deepcopy(users)
	users_pd = pd(users_dict)
	assert users_pd["total_users"] == 3
	assert users_pd["users", "1", "name"] == "Joe"
	# Non existent but correct paths return None
	assert users_pd["users", "-1", "name"] is None

	assert users_pd[2] is None
	# If value is not a dict, return that value
	assert isinstance(users_pd["follows"], list)
	# If value is a dict, return a PathDict
	assert users_pd["users"] is users_dict["users"]
	# Wrong path accesses, eg. get key on list, raise an exception
	with pytest.raises(KeyError):
		print(users_pd["follows", "not_correct"])
	# Get at list
	assert users_pd[["follows", 0]] == ["Ben", "Sue"]


def test_PDHandle_get_at():
	j = {"1": {"2": 3}}
	pd(j).get_at("1/2") == 3
	pd(j).get_at("1/3/4") is None
	pd(j).get_at("2") is None
	with pytest.raises(KeyError):
		pd(j).get_at("1/2/3")


def test_set_path():
	assert pd(["1", 2]).set([3, "4"]).get() == [3, "4"]

	j = {"u1": "Ben", "u2": "Sue"}
	p = pd(j)

	p.set(None).get() == j

	# Replace entire dict
	p.at().set({"u3": "Joe"})
	assert j == {"u3": "Joe"}

	# Cover specific KeyError
	with pytest.raises(KeyError):
		p.at("u3/meta/age").set(22)

	with pytest.raises(TypeError):
		p.at().set("Not Allowed")



	p = pd({"l1": [1, 2, 3]})
	with pytest.raises(KeyError):
		p.at(["l1", "nonexistent"]).set(4)
	with pytest.raises(KeyError):
		p.at(["l1", "nonexistent", "also_nonexistent"]).set(4)


# TODO: Decide if pop should be part of PathDict
# def test_pop():
# 	pd = PathDict({"u1": "Ben", "u2": "Sue"})
# 	popped = pd.pop("u1")
# 	assert popped == "Ben"
# 	assert pd.dict == {"u2": "Sue"}
# 	pop_not_existent = pd.pop("u3", None)
# 	assert pop_not_existent is None



def test_copy():
	j = {"1": {"2": 3}}

	assert pd(j).copy().get()     == j
	assert pd(j).copy().get() is not j

	assert pd(j).at("1").get() is j["1"]
	assert pd(j).at("1").copy().get() is not j["1"]

	print("💽")
	print(pd(j).at("1").copy())
	assert pd(j).at("1").copy().get()     == j["1"]

	assert pd(j).at("1").copy(from_root=True).get_root() == j

	# Nested
	dc_pd = pd(users).copy()
	assert dc_pd.data is not users
	dc_pd_copy = dc_pd.copy()
	assert dc_pd is not dc_pd_copy



def test_contains():
	users_dict = copy.deepcopy(users)
	users_pd = pd(users_dict)
	assert "total_users" in users_pd
	assert ["premium_users", 1] in users_pd
	assert "premium_users/1" in users_pd
	assert "premium_users", "1" in users_pd
	assert ["premium_users", "44"] not in users_pd
	assert ["users", "1"] in users_pd
	assert ["users", "999999"] not in users_pd
	assert ["users", "1", "name"] in users_pd
	assert ["users", "999999", "name"] not in users_pd
	assert ["users", "1", "name", "joe"] not in users_pd
	assert ["users", "1", "name", "joe", "Doe"] not in users_pd  # too many paths



def test_nested_object_copy():
	# Test copy with object
	class TestObject():
		def __init__(self, data): self.data = data
		def __repr__(self): return f"TestObject({self.data})"

	o = pd({})
	o["test", "test"] = TestObject({"1": "2"})
	assert str(o.get()) == """{'test': {'test': TestObject({'1': '2'})}}"""

	od = o.copy()
	# The copy has the same str representation
	assert str(od.get()) == str(o.get())
	# It is still a TestObject
	assert type(od.at("test", "test").get()) == TestObject
	# But not the same object
	assert od.at("test", "test").get() is not o.at("test", "test").get()


def test_PDHandle_map():
	j = {"1": {"2": 3}}
	assert pd(j).at("1/2").map(lambda x: x + 1).get() == 4
	assert pd(j).at("1/6/7").map(lambda x: (x or 0) + 1).get() == 1
	assert pd(j).at("1/6/7").map(lambda x: (x or 0) + 1).get() == 2
	assert j["1"]["2"] == 4
	assert j["1"]["6"]["7"] == 2
	with pytest.raises(TypeError):
		pd(j).at("1/99/99").map(lambda x: x + 1)


def test_PDHandle_mapped():
	j = {
		"1": {"2": 3},
		"a": {"b": "c"}
	}

	p = pd(j).at("1/2").mapped(lambda x: x + 1).get_root()
	p2 = pd(j).copy().at("1/2").map(lambda x: x + 1).get_root()


	assert j["1"]["2"] == 3
	assert p["1"]["2"] == 4
	assert p2["1"]["2"] == 4

	assert j["a"] == p["a"]
	assert j["a"] is not p["a"]


def test_scenario_1():
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
	o = pd(d)
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

	assert o.get() == {
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


def test_PDMultiHandle_get_all():
	db = {
		"a": {
			"a1": 1,
			"a2": 2,
			"a3": 3,
		},
		"b": {
			"b1": 4,
			"b2": 5,
			"b3": 6,
		},
	}

	p = pd(db)

	assert p.at("nonexistent/*").get_all() == []
	assert p.at("*/nonexistent/*").get_all() == []
	# assert p.at("*/nonexistent").get_all() == []

	# Finds all values, returns as list
	assert p.at("*").get_all() == [
		{
			"a1": 1,
			"a2": 2,
			"a3": 3,
		},
		{
			"b1": 4,
			"b2": 5,
			"b3": 6,
		},
	]

	assert p.at("*", "a1").get_all() == [1, None]
	assert p.at("*", "*").get_all() == [1, 2, 3, 4, 5, 6]

	assert p.at("*", "*").get_all(include_paths=True) == [
		(("a", "a1"), 1),
		(("a", "a2"), 2),
		(("a", "a3"), 3),
		(("b", "b1"), 4),
		(("b", "b2"), 5),
		(("b", "b3"), 6),
	]

	assert p.at("*", "*").get_all(as_type="dict") == {
		("a", "a1"): 1,
		("a", "a2"): 2,
		("a", "a3"): 3,
		("b", "b1"): 4,
		("b", "b2"): 5,
		("b", "b3"): 6,
	}

	with pytest.raises(ValueError):
		p.at("*", "*").get_all(as_type="invalid")





def test_PDMultiHandle_get_all_2():
	p = pd({
		"1": {
			"name": "Joe",
			"age": 22,
			"interests": ["Python", "C++", "C#"],
		},
		"2": {
			"name": "Ben",
			"age": 49,
			"interests": ["Javascript", "C++", "Haskell"],
		},
		"3": {
			"name": "Sue",
			"age": 36,
			"interests": ["Python", "C++", "C#"],
		},
	})

	ages = p.at(["*", "age"]).get_all()
	assert ages == [22, 49, 36]

	ages_sum = sum(p.at("*/age").get_all())
	assert ages_sum == 107

	# ages_over_30 = p.at("*/age").filtered(lambda x: x > 30)
	# print(ages_over_30)
	# assert ages_over_30 == [49, 36]

	# interests = pd["*", "interests"]
	# assert interests == [
	# 	["Python", "C++", "C#"],
	# 	["Javascript", "C++", "Haskell"],
	# 	["Python", "C++", "C#"],
	# ]



def test_PDMultiHandle_get_all_3():
	p = pd({
		"1": [2, 3, 4],
		"2": "3",
	})
	assert p.at("1/*").get_all() == [2, 3, 4]
	with pytest.raises(KeyError):
		p.at("2/*").get_all()


def test_PDHandle_filter():
	users_pd = pd(users)

	users_below_30 = users_pd.copy().at("users").filtered(lambda k, v: v["age"] <= 30)
	assert users_below_30.get() == {
		"1": {
			"age": 22,
			"name": "Joe"
		}
	}

	premium_users = users_pd.copy().at("users").filtered(lambda k, v: int(k) in users_pd["premium_users"])
	assert premium_users.get() == {
		"1": {
			"age": 22,
			"name": "Joe"
		},
		"3": {
			"age": 32,
			"name": "Sue"
		}
	}

	follows_includes_joe = users_pd.at("follows").filtered(lambda e: "Joe" in e)
	assert isinstance(follows_includes_joe.get(), list)
	assert follows_includes_joe.get() == [
		["Joe", "Ben"],
		["Ben", "Joe"],
	]


def test_PDHandle_filter_behavior_spec():
	j = {
		"a": "b",
		"1": {
			"2": "20",
			"3": "30",
			"4": "40",
		}
	}
	p = pd(j)
	p.at("1").filter(lambda k, v: int(k) > 3)

	assert j == {"a": "b", "1": {"4": "40"}}
	assert p.get() == {"4": "40"}
	assert p.get_root() == {"a": "b", "1": {"4": "40"}}

	with pytest.raises(TypeError):
		p.at("a").filter(lambda x: x)


def test_scenario_2():
	tr = pd({
		"1": {
			"date": "2018-01-01",
			"amount": 100,
			"currency": "EUR",
		},
		"2": {
			"date": "2018-01-02",
			"amount": 200,
			"currency": "CHF",
			"related": [5, {"nested": "val"}, 2, 3]
		},
	})

	assert tr["2", "related", 1, "nested"] == "val"

	with pytest.raises(KeyError):
		print(tr["2", "related", 9])
	with pytest.raises(KeyError):
		print(tr["2", "related", 0, "nested", "val"])


def test_star_operations():
	winners_original = pd({
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
	winners = winners_original.copy(from_root=True)
	assert winners.at("*", "podium", "*", "name").get_all() == [
		"Joe", "Ben", "Sue", "Bernd", "Sara", "Jan"
	]

	# Increment age of all users by 1
	winners = winners_original.copy(from_root=True)
	winners.at("*/podium/*/age").map(lambda x: x + 1)
	assert winners["2017", "podium", "17-place-1", "age"] == 23
	assert winners["2017", "podium", "17-place-2", "age"] == 14
	assert winners["2017", "podium", "17-place-3", "age"] == 99
	assert winners["2018", "podium", "18-place-1", "age"] == 51
	assert winners["2018", "podium", "18-place-2", "age"] == 33
	assert winners["2018", "podium", "18-place-3", "age"] == 27

	names_2017 = winners.at("2017", "podium", "*", "name").get_all()
	assert names_2017 == ["Joe", "Ben", "Sue"]



def test_PDHandle_reduce():
	users_pd = pd(users).copy()

	users_ages = users_pd.at("users").reduce(lambda k, v, a: a + v["age"], aggregate=0)
	assert users_ages == 103

	p = pd({"l1": [1, 2, 3]})
	assert p.at("l1").reduce(lambda v, a: a + v, aggregate=10) == 16

	p = pd({"l1": "abc"})
	with pytest.raises(TypeError):
		p.at("l1").reduce(lambda v, a: a + v, aggregate=0)

	p = pd(users).copy()
	assert p.at("users/*/name").reduce(lambda v, a: a + [v], aggregate=[]) == ["Joe", "Ben", "Sue"]
