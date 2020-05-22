# PathDict
The versatile dict for Python!


## Installation
`pip3 install pathdict`

Import:

```python
from pathdict import PathDict
```



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
joe = PathDict(user)
> joe == user # True
> joe.dict is user # True
```

You can also get a deep copy:


```python
joe = PathDict(user, deep_copy=True)
> joe == user # True
> joe.dict is user # False
```



### Getting and setting values with paths

You can use paths of keys to access values:

```python
joe = PathDict(user, deep_copy=True)

# Get

> joe["friends", "Sue", "age"]
---> 30

> joe["friends", "Josef", "age"]
---> None

# Set

joe["authentification", "password"] = "abc123"
> joe["authentification"]
---> PathDict({"password": "abc123"})
```

Using invalid paths to get or set a value will result in an error. An invalid path is a path that tries to access a key of an int or list, for example. So, only use paths to access hierarchies of PathDicts.


```python
joe = PathDict(user, deep_copy=True)


> joe["hobbies", "not_existent"]
---> Error!

```



### Most dict methods are supported

Many of the usual dict methods work with PathDict:

```python
pathdict = ...

for key, value in pathdict.items():
	...

for key in pathdict:
	...

for key in pathdict.keys():
	...

for value in pathdict.values():
	...

```



### Filtering

### Aggregating

### Serialize to JSON
