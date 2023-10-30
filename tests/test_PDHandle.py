import pytest

from path_dict import pd
from tests import dummy_data


def test_initialization():
	# Empty
	assert pd({}).get() == {}

	# Wrong inits
	for wrong in ["", 1, 1.0, True, None, (), set()]:
		with pytest.raises(TypeError):
			pd(wrong)

	# Check data
	init_dict = dummy_data.get_users()
	p = pd(init_dict)
	assert p.data is init_dict
	assert p is not init_dict
	assert p.get() == init_dict
	assert p["users"] is init_dict["users"]
	assert isinstance(p["premium_users"], list)
	assert p["premium_users"] is init_dict["premium_users"]


def test_at():
	db = dummy_data.get_db()
	assert pd(db).at().path_handle.path == []
	assert pd(db).at("").path_handle.path == []
	assert pd(db).at([]).path_handle.path == []
	assert pd(db).at("users").path_handle.path == ["users"]
	assert pd(db).at(["users"]).path_handle.path == ["users"]
	assert pd(db).at("users", "1").path_handle.path == ["users", "1"]
	assert pd(db).at("users", "1", "friends").path_handle.path == ["users", "1", "friends"]
	assert pd(db).at(["users", "1", "friends"]).path_handle.path == ["users", "1", "friends"]


def test_at_parent():
	assert pd(dummy_data.get_db()).at("users", "1").at_parent().path_handle.path == ["users"]
	pd(dummy_data.get_db()).at_parent().get() is None


def test_at_children():
	db = dummy_data.get_db()
	assert pd(db).at("users").at_children().gather() == list(db["users"].values())


def test_simple_get():
	db = dummy_data.get_db()
	assert pd(db).get() == db
	assert pd(db).at("").get() == db
	assert pd(db).at().get() == db
	assert pd(db).at("users", "1", "name").get() == "John"
	assert pd(db).at("users", "9", "name").get() is None
	assert pd(db).at(2).get() is None
	assert pd(db).at("users", "9", "name").get("default") == "default"


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
	copy = pd(shared_dict).deepcopy()
	assert copy.get() is not p1_shared_dict.get()


def test__repr__():
	j = {"1": 2}
	assert str(pd(j)) == "PathDict(self.data = {'1': 2}, self.path_handle = Path(path=[], raw=False))"


def test_reset_at_after_in():
	j = {"1": {"2": 3}}
	p = pd(j)
	assert "1" in p
	assert p.get() == j


def test_deepcopy():
	j = {"1": {"2": 3}}
	assert pd(j).at("1").get() is j["1"]

	# deepcopy at root
	assert pd(j).deepcopy().get() == j
	assert pd(j).deepcopy().get() is not j

	# deepcopy at path
	assert pd(j).at("1").deepcopy().get() is not j["1"]
	assert pd(j).at("1").deepcopy().get() == j["1"]
	assert pd(j).deepcopy().at("1").get() is not j["1"]

	# deepcopy from root at path
	assert pd(j).at("1").deepcopy(from_root=True).at().get() == j
	assert pd(j).at("1").deepcopy(from_root=True).at().get() is not j
	assert pd(j).at("1").deepcopy(from_root=True).get() == j

	# Nested
	users = dummy_data.get_users()
	dc_pd = pd(users).deepcopy()
	assert dc_pd.data is not users
	dc_pd_copy = dc_pd.deepcopy()
	assert dc_pd is not dc_pd_copy


def test_copy():
	j = {"1": {"2": 3}}
	assert pd(j).at("1").get() is j["1"]

	assert pd(j).copy().get() == j
	assert pd(j).copy().get() is not j

	assert pd(j).at("1").copy().get() is not j["1"]
	assert pd(j).at("1").copy().get() == j["1"]
	assert pd(j).copy().at("1").get() is j["1"]

	assert pd(j).at("1").copy(from_root=True).at().get() == j

	# Nested
	users = dummy_data.get_users()
	dc_pd = pd(users).copy()
	assert dc_pd.data is not users
	dc_pd_copy = dc_pd.copy()
	assert dc_pd is not dc_pd_copy


def test_contains():
	users_dict = dummy_data.get_users()
	users_pd = pd(users_dict)
	assert "total_users" in users_pd
	assert ["premium_users", 1] in users_pd
	assert "premium_users", "1" in users_pd
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
	class TestObject:
		def __init__(self, data):
			self.data = data

		def __repr__(self):
			return f"TestObject({self.data})"

	o = pd({})
	o["test", "test"] = TestObject({"1": "2"})
	assert str(o.get()) == """{'test': {'test': TestObject({'1': '2'})}}"""

	# True deepcopy
	tdc = o.deepcopy(true_deepcopy=True)
	# The copy has the same str representation
	assert str(tdc.get()) == str(o.get())
	# It is still a TestObject
	assert type(tdc.at("test", "test").get()) == TestObject
	# But not the same object
	assert tdc.at("test").get() is not o.at("test").get()
	assert tdc.at("test", "test").get() is not o.at("test", "test").get()

	# Fast deepcopy
	fdc = o.at().deepcopy()
	# The copy has the same str representation
	assert str(fdc.get()) == str(o.get())
	# It is still a TestObject
	assert type(fdc.at("test", "test").get()) == TestObject
	# But not the same object
	assert fdc.at("test").get() is not o.at("test").get()
	assert fdc.at("test", "test").get() is o.at("test", "test").get()


def test_get_path():
	users_dict = dummy_data.get_users()
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

	assert users_pd["users", "1", "*"] == ["Joe", 22]


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
		p.at("u3", "meta", "age").set(22)

	with pytest.raises(TypeError):
		p.at().set("Not Allowed")

	p = pd({"l1": [1, 2, 3]})
	with pytest.raises(KeyError):
		p.at(["l1", "nonexistent"]).set(4)
	with pytest.raises(KeyError):
		p.at(["l1", "nonexistent", "also_nonexistent"]).set(4)


def test_map():
	j = {"1": {"2": 3}}
	assert pd(j).at("1", "2").map(lambda x: x + 1).get() == 4
	assert pd(j).at("1", "6", "7").map(lambda x: (x or 0) + 1).get() == 1
	assert pd(j).at("1", "6", "7").map(lambda x: (x or 0) + 1).get() == 2
	assert j["1"]["2"] == 4
	assert j["1"]["6"]["7"] == 2
	with pytest.raises(TypeError):
		pd(j).at("1", "99", "99").map(lambda x: x + 1)


def test_mapped():
	j = {"1": {"2": 3}, "a": {"b": "c"}}

	p = pd(j).at("1", "2").mapped(lambda x: x + 1).at().get()
	p2 = pd(j).deepcopy().at("1", "2").map(lambda x: x + 1).at().get()

	assert j["1"]["2"] == 3
	assert p["1"]["2"] == 4
	assert p2["1"]["2"] == 4

	assert j["a"] == p["a"]
	assert j["a"] is not p["a"]


def test_append():
	p = pd({})
	p.at("1", "2").append(3)
	assert p.at().get() == {"1": {"2": [3]}}
	with pytest.raises(TypeError):
		p.at("1").append(2)


def test_update():
	p = pd({"a": 1})
	p.update({"b": 2, "a": 2})
	assert p.get() == {"a": 2, "b": 2}


def test_filter_behavior_spec():
	j = {
		"a": "b",
		"1": {
			"2": "20",
			"3": "30",
			"4": "40",
		},
	}
	p = pd(j)
	p.at("1").filter(lambda k, v: int(k) > 3)

	assert j == {"a": "b", "1": {"4": "40"}}
	assert p.get() == {"4": "40"}
	assert p.at().get() == {"a": "b", "1": {"4": "40"}}

	with pytest.raises(TypeError):
		p.at("a").filter(lambda x: x)


def test_filter():
	users_pd = pd(dummy_data.get_users())

	users_below_30 = users_pd.deepcopy().at("users").filtered(lambda k, v: v["age"] <= 30)
	assert users_below_30.get() == {"1": {"age": 22, "name": "Joe"}}

	premium_users = users_pd.deepcopy().at("users").filtered(lambda k, v: int(k) in users_pd["premium_users"])
	assert premium_users.get() == {"1": {"age": 22, "name": "Joe"}, "3": {"age": 32, "name": "Sue"}}

	follows_includes_joe = users_pd.at("follows").filtered(lambda e: "Joe" in e)
	assert isinstance(follows_includes_joe.get(), list)
	assert follows_includes_joe.get() == [
		["Joe", "Ben"],
		["Ben", "Joe"],
	]


def test_reduce():
	users_pd = pd(dummy_data.get_users())

	users_ages = users_pd.at("users").reduce(lambda k, v, a: a + v["age"], aggregate=0)
	assert users_ages == 103

	p = pd({"l1": [1, 2, 3]})
	assert p.at("l1").reduce(lambda v, a: a + v, aggregate=10) == 16

	p = pd({"l1": "abc"})
	with pytest.raises(TypeError):
		p.at("l1").reduce(lambda v, a: a + v, aggregate=0)

	p = pd(dummy_data.get_users())
	assert p.at("users", "*", "name").reduce(lambda v, a: a + [v], aggregate=[]) == ["Joe", "Ben", "Sue"]


def test_keys():
	p = pd({"1": {"2": [3]}})
	assert p.keys() == ["1"]
	assert p.at("1").keys() == ["2"]
	with pytest.raises(AttributeError):
		p.at("1", "2").keys()


def test_values():
	p = pd({"1": {"2": [3]}})
	assert p.values() == [{"2": [3]}]
	assert p.at("1").values() == [[3]]
	with pytest.raises(AttributeError):
		p.at("1", "2").values()


def test_items():
	p = pd({"1": {"2": [3]}})
	assert list(p.items()) == [("1", {"2": [3]})]
	assert list(p.at("1").items()) == [("2", [3])]
	with pytest.raises(AttributeError):
		p.at("1", "2").items()


def test__len__():
	p = pd({"1": {"2": [3, 1]}})
	assert len(p) == 1
	assert len(p.at("1")) == 1
	assert len(p.at("1", "2")) == 2


def test_pop():
	p = pd({"1": {"2": [3, 1]}, "4": 4})
	assert p.pop("1") == {"2": [3, 1]}
	assert p.get() == {"4": 4}
	assert p.pop("1") is None
	assert p.pop("1", 2) == 2


def test_iter():
	p = pd({"a": 1, "b": 2, "c": 3})

	keys = []
	for k in p:
		keys.append(k)
	assert keys == ["a", "b", "c"]
