
def get_users():
	return {
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


def get_db():
	return {
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
