# PathDict

[![Downloads](https://pepy.tech/badge/path-dict)](https://pepy.tech/project/path-dict)
[![Downloads](https://pepy.tech/badge/path-dict/month)](https://pepy.tech/project/path-dict)
[![Downloads](https://pepy.tech/badge/path-dict/week)](https://pepy.tech/project/path-dict)


The versatile dict for Python!


## Installation
`pip3 install path-dict`

Import:

```python
from path_dict import PathDict
```



## Usage
PathDict is like a normal python dict, but comes with some handy extras.



### Initialize

```python
# Empty PathDict
pd = PathDict()

> pd
---> PathDict({})

```

A PathDict keeps a reference to the original initializing dict:

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
> joe == user
---> True
> joe.dict is user
---> True
```

You can also get a deep copy:

```python
joe = PathDict(user, deepcopy=True)
> joe == user
---> True
> joe.dict is user
---> False
```



### Getting and setting values with paths

You can use paths of keys to access values:

```python
joe = PathDict(user, deepcopy=True)

# Get existing path
> joe["friends", "Sue", "age"]
---> 30

# Get non-existent, but valid path
> joe["friends", "Josef", "age"]
---> None

# Set non-existent, but valid path, creates keys
joe["authentification", "password"] = "abc123"
> joe["authentification"]
---> PathDict({"password": "abc123"})
```

Using invalid paths to get or set a value will result in an error. An invalid path is a path that tries to access a key of an int or list, for example. So, only use paths to access hierarchies of PathDicts.


```python
joe = PathDict(user, deepcopy=True)

# Get invalid path (joe["hobbies"] is a list)
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


### Apply a function at a path

When setting a value, you can use a lambda function to modify the value at a given path.
The function should take one argument and return the modified value.


```python
stats_dict = {}
stats_pd = PathDict({})

# Using a standard dict:
if "views" not in stats_dict:
	stats_dict["views"] = {}
if "total" not in stats_dict["views"]:
	 stats_dict["views"]["total"] = 0
stats_dict["views"]["total"] += 1

# You can achieve the same using a PathDict:
stats_pd["views", "total"] = lambda x: (x or 0) + 1
```



### Filtering

PathDicts offer a filter function, which can filter a list or a PathDict at a given path in-place.

To filter a list, pass a function that takes one argument (eg. `lambda ele: return ele > 10`) and returns True if the value should be kept, else False.
To filter a PathDict, pass a function that takes two arguments (eg. `lambda key, value: key != "1"`) and returns True if the key-value pair should be kept, else False.

You can filter the PathDict filter is called on, or you can also pass a path into the filter to apply the filter at a given path.

A filtered function is also offered, which does the same, but returns a filtered deepcopy instead of filtering in-place.


```python
joe = PathDict(user, deepcopy=True)

# Remove all friends that are older than 33.
joe.filter("friends", f=lambda k, v: v["age"] < 33)

> joe["friends"]
---> PathDict({
	"Sue": {"age": 30}
})
```


### Aggregating

The aggregate function can combine a PathDict to a single aggregated value.
It takes an init parameter, and a function with takes three arguments (eg. `lambda key, val, agg`)

```python
joe = PathDict(user, deepcopy=True)

# Sum of ages of all friends of joe
friend_ages = joe.aggregate("friends", init=0, f=lambda k, v, a: a + v["age"])

> friend_ages
---> 65
```

### Serialize to JSON

To serialize a PathDict to JSON, call `json.dumps(path_dict.dict)`.
If you try to serialize a PathDict object itself, the operation will fail.
