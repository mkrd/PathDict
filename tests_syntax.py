from path_dict import PathDict as pd

users ={
  "user_1": {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "age": 32,
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    },
    "interests": ["reading", "hiking", "traveling"]
  },
  "user_2": {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "age": 28,
    "address": {
      "street": "456 Oak Ave",
      "city": "Somewhere",
      "state": "NY",
      "zip": "67890"
    },
    "interests": ["cooking", "running", "music"],
    "job": {
      "title": "Software Engineer",
      "company": "Example Inc.",
      "salary": 80000
    }
  },
  "user_3": {
    "name": "Bob Johnson",
    "email": "bob.johnson@example.com",
    "age": 40,
    "address": {
      "street": "789 Maple Blvd",
      "city": "Nowhere",
      "state": "TX",
      "zip": "54321"
    },
    "interests": ["gardening", "fishing", "crafts"],
    "job": {
      "title": "Marketing Manager",
      "company": "Acme Corporation",
      "salary": 90000
    }
  },
  "user_4": {
    "name": "Alice Brown",
    "email": "alice.brown@example.com",
    "age": 25,
    "address": {
      "street": "321 Pine St",
      "city": "Anywhere",
      "state": "FL",
      "zip": "13579"
    },
    "interests": ["painting", "yoga", "volunteering"],
    "job": {
      "title": "Graphic Designer",
      "company": "Design Co.",
      "salary": 65000
    }
  }
}

users_pd = pd(users)


users_pd.at("user_4")



print(users_pd.at("user_5").set({"name": "John Smither", "age": 33}))

# print(users_pd.at("*", "age").gather(as_type="list", include_paths=True))
