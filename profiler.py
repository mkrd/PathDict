from path_dict import pd
import json
from pyinstrument.profiler import Profiler

from path_dict.pd_handle import PathDict

db_directory = "./test_data/production_database"


class TestObject(object):
	def __init__(self, data):
		self.data = data

	def get_path(self, path):
		print(path)


users = pd(json.loads(open(f"{db_directory}/users.json", "r").read()))
tasks = pd(json.loads(open(f"{db_directory}/tasks.json", "r").read()))


users.filter(f=lambda k, v: v.get("status") != "archived")
sorted_users_list = sorted(users.values(), key=lambda x: x["first_name"])

print(f"{len(users)} users, {len(tasks)} tasks")
tasks["test", "test"] = TestObject({"test": "test"})


def agg(tasks: PathDict, sorted_users_list):
	# Get active users
	for user in sorted_users_list:
		user_active_tasks = tasks.filtered(lambda k, v: v.get("annotator_id") == user["id"] and v["status"] == "assigned_accepted")
		s = len(user_active_tasks)
		user["active_tasks_sum"] = s
		user_pending_tasks = tasks.filtered(lambda k, v: v.get("annotator_id") == user["id"] and v["status"] == "assigned_pending")
		s = len(user_pending_tasks)
		user["pending_tasks_sum"] = s
		print(user["last_name"], user["active_tasks_sum"], user["pending_tasks_sum"])


profiler = Profiler(interval=0.0001)
profiler.start()
agg(tasks, sorted_users_list)
profiler.stop()
profiler.open_in_browser(timeline=True)
