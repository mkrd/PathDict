import pytest

from path_dict import pd


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
		],
	}
	o = pd(d)
	# Getting attributes
	assert o["total_users"] == 3
	assert o["not_exists"] is None
	assert o["users"] == {
		"1": {"name": "Joe", "age": 22},
		"2": {"name": "Ben", "age": 49},
		"3": {"name": "Sue", "age": 32},
	}
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
	assert o["follows"] == [["Sue", "Ben"], ["Ben", "Joe"], ["Joe", "Ben"]]

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
		"follows": [["Sue", "Ben"], ["Ben", "Joe"], ["Joe", "Ben"]],
	}


def test_scenario_2():
	tr = pd(
		{
			"1": {
				"date": "2018-01-01",
				"amount": 100,
				"currency": "EUR",
			},
			"2": {"date": "2018-01-02", "amount": 200, "currency": "CHF", "related": [5, {"nested": "val"}, 2, 3]},
		}
	)

	assert tr["2", "related", 1, "nested"] == "val"

	with pytest.raises(KeyError):
		print(tr["2", "related", 9])
	with pytest.raises(KeyError):
		print(tr["2", "related", 0, "nested", "val"])


def test_scenario_3():
	u = pd(
		{
			"1": {
				"name": "Joe",
				"currencies": ["EUR", "CHF"],
				"expenses": {
					"1": {"amount": 100, "currency": "EUR"},
					"2": {"amount": 50, "currency": "CHF"},
					"3": {"amount": 200, "currency": "EUR"},
				},
			},
			"2": {
				"name": "Ben",
				"currencies": ["EUR", "USD"],
				"expenses": {
					"1": {"amount": 3, "currency": "EUR"},
					"2": {"amount": 40, "currency": "USD"},
					"3": {"amount": 10, "currency": "USD"},
				},
			},
			"3": {
				"name": "Sue",
				"currencies": ["CHF", "USD"],
				"expenses": {
					"1": {"amount": 500, "currency": "CHF"},
					"2": {"amount": 300, "currency": "CHF"},
					"3": {"amount": 200, "currency": "USD"},
				},
			},
		}
	)

	assert u.at("*", "expenses", "*", "amount").sum() == 1403
	assert u.at("2", "expenses", "*", "amount").sum() == 53
	assert u.at("*", "expenses", "1", "amount").sum() == 603
	# Get sum of all expenses in EUR

	assert (
		u.deepcopy(from_root=True)
		.at("*", "expenses", "*")
		.filter(lambda v: v["currency"] == "EUR")
		.at("*", "amount")
		.sum()
		== 303
	)

	# Get all transactions in CHF except for those of sue
	assert (
		u.at("*")
		.filter(lambda x: x["name"] != "Sue")
		.at("*", "expenses", "*")
		.filter(lambda v: v["currency"] == "CHF")
		.at("*", "amount")
		.sum()
		== 50
	)

	j = pd(
		{
			"a": [1, 2],
			"b": {"c": 1, "d": 2},
			"e": 5,
		}
	)
	assert j.at("a").sum() == 3
	assert j.at("b").sum() == 3
	with pytest.raises(TypeError):
		j.at("e").sum()
