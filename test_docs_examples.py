from pathdict import PathDict

users = {
	"u1": {
		"name": "Julia",
		"age": 32,
		"interests": ["soccer", "basketball"],
	},
	"u2": {
		"name": "Ben",
		"age": 26,
		"interests": ["airplanes", "alternative music"]
	}
}


users = PathDict(users)

# Get all user names
users["*", "name"]  # -> ["Julia", "Ben"]
print(f"{users['*', 'name'] = }")

# Increase age of Julia
users["u1", "age"] = 33
print(f"{users['u1', 'age'] = }")  # -> 33

# Append interest "cooking" to all users
users["*", "interests"] = lambda interests: interests + ["cooking"]
print(users)

# Remove all interests of Ben which do not start with "a" ("cooking is removed")
users.filter("u2", "interests", f=lambda interest: not interest.startswith("a"))
print(users)

# Remove users that are younger than 30
users.filter(f=lambda id, user: user["age"] >= 30)
print(users)
