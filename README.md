# PathDict
The versatile dict for Python!

## Usage
PathDict is like a normal python dict, but comes with some handy extras.

### Initialize

```python
# Empty PathDict
pd = PathDict({})
```

A PathDict keeps a reference to the original initializing dict

```python
user = {
	"name": "Joe",
	"age": 22,
	"hobbies": ["Playing football", "Podcasts"]
	"friends": {
		"Sue": {"age": 30},
		"Ben": {"age": 35},
	}
}
pd = PathDict(user)
> pd == user # True
> pd.dict is user # True
```

You can also get a deep copy:


```python
pd = PathDict(user, deep_copy=True)
> pd == user # True
> pd.dict is user # False
```

### Getting and setting values

You can use paths of keys to access values:

```python
joe = PathDict(user, deep_copy=True)

> joe["friends", "Sue", "age"]
---> 30

> joe["friends", "Josef", "age"]
---> None

joe["authentification", "password"] = "abc123"
> joe["authentification"]
---> PathDict({"password": "abc123"})




```


### Most dict methods are supported

### Filtering

### Aggregating

### Serialize to JSON
