
from ssl import OP_ENABLE_MIDDLEBOX_COMPAT
from path_dict_alt import pd
import pytest


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


def test_at():

	assert pd(db).at().path_from_root.path == []
	assert pd(db).at([]).path_from_root.path == []
	assert pd(db).at("users").path_from_root.path == ["users"]
	assert pd(db).at(["users"]).path_from_root.path == ["users"]
	assert pd(db).at("users", "1").path_from_root.path == ["users", "1"]
	assert pd(db).at("users/1", "friends").path_from_root.path == ["users", "1", "friends"]
	assert pd(db, str_sep="-").at("users-1", "friends").path_from_root.path == ["users", "1", "friends"]
	assert pd(db).at(["users/1", "friends"]).path_from_root.path == ["users", "1", "friends"]



def test_simple_get():
	assert pd(db).get() == db
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
	deepcopy = pd(shared_dict).deepcopy()
	assert deepcopy.get() is not p1_shared_dict.get()




def test_nested_object_deepcopy():
	# Test deepcopy with object
	class TestObject():
		def __init__(self, data): self.data = data
		def __repr__(self): return f"TestObject({self.data})"

	o = pd({})
	o["test", "test"] = TestObject({"1": "2"})
	assert str(o.get()) == """{'test': {'test': TestObject({'1': '2'})}}"""

	od = o.deepcopy()
	# The deepcopy has the same str representation
	assert str(od.get()) == str(o.get())
	# It is still a TestObject
	assert type(od.at("test", "test").get()) == TestObject
	# But not the same object
	assert od.at("test", "test").get() is not o.at("test", "test").get()


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
