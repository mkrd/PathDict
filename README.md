
![Logo](https://github.com/mkrd/PathDict/blob/main/assets/logo.png?raw=true)

[![Total Downloads](https://pepy.tech/badge/path-dict)](https://pepy.tech/project/path-dict)
![Tests](https://github.com/mkrd/PathDict/actions/workflows/test.yml/badge.svg)
![Coverage](https://github.com/mkrd/PathDict/blob/main/assets/coverage.svg?raw=1)


Why do I need this?
================================================================================

Do you work with dicts a lot, but you also whish that they could do more?
Then PathDict is for you!

Lets look at this dict:

```python
users = {
    "u1": {
        "name": "Julia",
        "age": 32,
        "interests": ["soccer", "basketball"],
    },
    "u2": {
        "name": "Ben",
        "age": 26,
        "interests": ["airplanes", "alternative music"],
    }
}
```

With PathDict, you can do things like:

```python
users = PathDict(users)

# Get all user names
users["*", "name"]  # -> ["Julia", "Ben"]

# Add new post to the current_user's posts
new_post = {"title": ...}
users[current_user.id, "posts"] = lambda x: (x or []) + [new_post]  # Key "posts" is automatically created!


# Increase age of Julia
users["u1", "age"] = 33

# Append interest "cooking" to all users
users["*", "interests"] = lambda interests: interests + ["cooking"]


# Remove all interests of Ben which do not start with "a" ("cooking is removed")
users.filter("u2", "interests", f=lambda interest: not interest.startswith("a"))

# Remove users that are younger than 30
users.filter(f=lambda id, user: user["age"] >= 30)
```

**Pretty neat, right?**



Second Example
--------------------------------------------------------------------------------

Consider the following dict filled with users. Notice how Bob has
provided sports interests only, and Julia has provided music interests only.
```python
db = {
    "bob": {
        "interests": {
            "sports": ["soccer", "basketball"]
        }
    },
    "julia": {
        "interests": {
            "music": ["pop", "alternative"]
        }
    }
}
```

Lets print the music interests of each user using normal dicts:

```python
for user_name in db:
    user_music = None
    if user_name in db:
        if "interests" in db[user_name]:
            if "music" in db[user_name]["interests"]:
                user_music = db[user_name]["interests"]["music"]
    print(user_music)

# ---> None
# ---> ["pop", "alternative"]
```

**Annoying, right?** This is how we do it with a PathDict:

```python
db = PathDict(db)
for user_name in db:
    print(db[user_name, "interests", "music"])

# ---> None
# ---> ["pop", "alternative"]

```

**Much better!** If any of the keys do not exist, it will not throw and error,
but return `None`.

If we tried this with a normal dict, we would have gotten a `KeyError`.

The same also works for setting values, if the path does not exist, it will be
created.

Installation
================================================================================

`pip3 install path-dict`

```python
from path_dict import PathDict
```

Usage
================================================================================

PathDict subclasses [collections.UserDict](https://docs.python.org/3/library/collections.html#collections.UserDict),
so it behaves almist like a normal python dict, but comes with some handy extras.

## Initialize

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
joe = PathDict(user, copy=True)
> joe == user
---> True
> joe.dict is user
---> False
```

## Getting and setting values with paths

You can use paths of keys to access values:

```python
joe = PathDict(user, copy=True)

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
joe = PathDict(user, copy=True)

# Get invalid path (joe["hobbies"] is a list)
> joe["hobbies", "not_existent"]
---> Error!
```



## Most dict methods are supported

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

## Apply a function at a path

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

# Using a PathDict:
stats_pd["views", "total"] = lambda x: (x or 0) + 1
```

## Filtering

PathDicts offer a filter function, which can filter a list or a PathDict at a given path in-place.

To filter a list, pass a function that takes one argument (eg. `lambda ele: return ele > 10`) and returns True if the value should be kept, else False.
To filter a PathDict, pass a function that takes two arguments (eg. `lambda key, value: key != "1"`) and returns True if the key-value pair should be kept, else False.

You can filter the PathDict filter is called on, or you can also pass a path into the filter to apply the filter at a given path.

A filtered function is also offered, which does the same, but returns a filtered copy instead of filtering in-place.


```python
joe = PathDict(user, copy=True)

# Remove all friends that are older than 33.
joe.filter("friends", f=lambda k, v: v["age"] <= 33)

> joe["friends"]
---> PathDict({
    "Sue": {"age": 30}
})
```

## Aggregating

The aggregate function can combine a PathDict to a single aggregated value.
It takes an init parameter, and a function with takes three arguments (eg. `lambda key, val, agg`)

```python
joe = PathDict(user, copy=True)

# Sum of ages of all friends of joe
friend_ages = joe.aggregate("friends", init=0, f=lambda k, v, a: a + v["age"])

> friend_ages
---> 65
```

## Serialize to JSON

To serialize a PathDict to JSON, call `json.dumps(<PathDict>.dict)`.
If you try to serialize a PathDict object itself, the operation will fail.



# Reference


### pd(data: dict | list, raw=False) -> PathDict

Creates and returns a handle on the given data.

 Args:
- `data` - Must be a list or dict.
- `raw` - If `True`, do not interpret paths. So wildcards (`*`) are interpreted as a usual key, and tuples will be interpreted as keys  as well.

Returns:
- A handle that references the root of the given data dict or list.


## PathDict

### copy(self, from_root=False) -> PathDict

Return a deep copy of the data at the current path or from the root.

Args:
- `from_root` - If `True`, the copy will not be made at the root data, and not where the current path is. The path handle will be at the same location as it was in the original. If `False`, only the part of the data where the current path handle is at will be copied.

Returns:
- A handle on the newly created copy

The current path handle will stay the same.
