from path_dict import pd
import pytest
from tests import dummy_data



def test_get_all():
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

	assert p.at("nonexistent/*").gather() == []
	assert p.at("*/nonexistent/*").gather() == []
	# assert p.at("*/nonexistent").gather() == []

	# Finds all values, returns as list
	assert p.at("*").gather() == [
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

	assert p.at("*", "a1").gather() == [1, None]
	assert p.at("*", "*").gather() == [1, 2, 3, 4, 5, 6]

	assert p.at("*", "*").gather(include_paths=True) == [
		(("a", "a1"), 1),
		(("a", "a2"), 2),
		(("a", "a3"), 3),
		(("b", "b1"), 4),
		(("b", "b2"), 5),
		(("b", "b3"), 6),
	]

	assert p.at("*", "*").gather(as_type="dict") == {
		("a", "a1"): 1,
		("a", "a2"): 2,
		("a", "a3"): 3,
		("b", "b1"): 4,
		("b", "b2"): 5,
		("b", "b3"): 6,
	}

	with pytest.raises(ValueError):
		p.at("*", "*").gather(as_type="invalid")





def test_get_all_2():
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

	ages = p.at(["*", "age"]).gather()
	assert ages == [22, 49, 36]

	ages_sum = sum(p.at("*/age").gather())
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



def test_get_all_3():
	p = pd({
		"1": [2, 3, 4],
		"2": "3",
	})
	assert p.at("1/*").gather() == [2, 3, 4]
	with pytest.raises(KeyError):
		p.at("2/*").gather()





def test_gather():
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
	winners = winners_original.deepcopy(from_root=True)
	assert winners.at("*", "podium", "*", "name").gather() == [
		"Joe", "Ben", "Sue", "Bernd", "Sara", "Jan"
	]

	# Increment age of all users by 1
	winners = winners_original.deepcopy(from_root=True)
	winners.at("*/podium/*/age").map(lambda x: x + 1)
	assert winners["2017", "podium", "17-place-1", "age"] == 23
	assert winners["2017", "podium", "17-place-2", "age"] == 14
	assert winners["2017", "podium", "17-place-3", "age"] == 99
	assert winners["2018", "podium", "18-place-1", "age"] == 51
	assert winners["2018", "podium", "18-place-2", "age"] == 33
	assert winners["2018", "podium", "18-place-3", "age"] == 27

	names_2017 = winners.at("2017", "podium", "*", "name").gather()
	assert names_2017 == ["Joe", "Ben", "Sue"]



def test_sum():
	p = pd({
		"1": {"a": 1, "b": [1]},
		"2": {"a": 3, "b": [1]},
	})
	assert p.at("*/a").sum() == 4
	with pytest.raises(TypeError):
		p.at("*/b").sum()


def test__repr__():
	p = pd({})
	assert str(p.at("*")) == "MultiPathDict(self.root_data = {}, self.path_handle = Path(path=['*'], str_sep=/, raw=False))"


def test_set():
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
	p = pd(db).deepcopy()
	p.at("users/*/friends").set([])
	p["users/*/blip"] = "blap"
	assert p["users", "1", "friends"] == []
	assert p["users", "2", "friends"] == []
	assert p["users", "3", "friends"] == []
	assert p["users", "1", "blip"] == "blap"
	assert p["users", "2", "blip"] == "blap"
	assert p["users", "3", "blip"] == "blap"
