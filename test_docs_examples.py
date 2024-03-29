from path_dict import pd
from datetime import datetime, timedelta


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


users = pd(users)

# Get all user names
users["*", "name"]  # -> ["Julia", "Ben"]
print(f"{users['*', 'name'] = }")

# Increase age of Julia
users["u1", "age"] = 33
print(f"{users['u1', 'age'] = }")  # -> 33

# Append interest "cooking" to all users
users["*", "interests"] = lambda i: i + ["cooking"]
print(users)

# Remove all interests of Ben which do not start with "a" ("cooking is removed")
users.at("u2", "interests").filter(lambda i: not i.startswith("a"))
print(users)

# Remove users that are younger than 30
users.at().filter(lambda id, user: user["age"] >= 30)
print(users)




crawler_output = {
	"crawl_time": "2021-09-01 12:00:00",
	"posts": [
		{
			"id": 1,
			"title": "Hello World",
			"meta": {
				"deleted": True,
				"author": "u1"
			}
		},
		{
			"id": 2,
			"title": "Hello aswell",
			"meta": {
				"author": "u2"
			}
		}
	]
}

# # Get all deleted Posts:
# deleted_posts = []
# for post in crawler_output["posts"]:
# 	if "meta" in post:
# 		if post["meta"].get("deleted", False):
# 			deleted_posts.append(post)

# # Or
# deleted_posts = [post for post in crawler_output["posts"] if post.get("meta", {}).get("deleted", False)]

# # Remove all deleted posts
# db["posts"] = [post for post in crawler_output["posts"] if not post.get("meta", {}).get("deleted", False)]

# print("Deleted Posts:")
# print(deleted_posts)

# # PD version get deleted posts
# pd = PathDict(crawler_output)
# deleted_posts = pd.filtered("posts", lambda x: x["meta", "deleted"])["posts"]
# print(deleted_posts)
# # Current
# deleted_posts = crawler_output.filtered("posts", lambda x: x["meta", "deleted"])["posts"]
# # New alternative 1
# deleted_posts = pd(crawler_output).filtered("posts", lambda x: x["meta", "deleted"])["posts"]
# # New alternative 2
# deleted_posts = pd.filtered(crawler_output, "posts", lambda x: x["meta", "deleted"])["posts"]



# # PD version remove deleted posts
# pd.filter("posts", f=lambda x: not x["meta", "deleted"])



posts = {
	"p1": {
		"ts": 1663566212,
		"title": "Hello World",
		"meta": {"author": "u1", "deleted": True},
	},
	"p2": {
		"ts": 1666158212,
		"title": "Hello aswell",
		"meta": {"author": "u2"},
	},
	"p3": {
		"ts": 1666331012,
		"title": "Hello again",
	},
}


last_week = datetime.now() - timedelta(weeks=1)
pd(posts).at("*", "ts").map(lambda ts: datetime.fromtimestamp(ts))
pd(posts).filter(lambda id, post: post["ts"] > last_week)
