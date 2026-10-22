import urllib.request
import json
import urllib.error

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

#测试200
def test_health():
	health_url = f"{BASE_URL}/health"
	with urllib.request.urlopen(health_url,timeout=TIMEOUT) as resp:
		assert resp.status == 200
	print("[PASS] GET /health - 200")
#测试201任务Creat
def test_post_task():
	post_url = f"{BASE_URL}/tasks"
	payload = {"task_type":"text_length","text":"Hello Multi-Agent"}
	data = json.dumps(payload).encode("utf-8")
	request = urllib.request.Request(
		post_url,
		data=data,
		headers={"Content-Type":"application/json"},
		method="POST"
	)
	with urllib.request.urlopen(request,timeout=TIMEOUT) as response:
		assert response.status == 201
		result = json.loads(response.read().decode("utf-8"))
		task_id = result["task_id"]
	print("[PASS] POST /tasks - 201")
	return task_id
#测试get
def test_get_task(task_id):
	get_url = f"{BASE_URL}/tasks/{task_id}"
	with urllib.request.urlopen(get_url,timeout=TIMEOUT) as get_response:
		assert get_response.status == 200
		get_result = json.loads(get_response.read().decode("utf-8"))
		assert get_result["task_id"] == task_id
	print("[PASS] GET /tasks/{task_id} - 200")
#测试404Notfound
def test_not_found():
	not_found_url = f"{BASE_URL}/tasks/not-exit"
	try:
		with urllib.request.urlopen(not_found_url,timeout=TIMEOUT) as resp:
			raise AssertionError(f"预期404，实际返回{resp.status}")
	except urllib.error.HTTPError as e:
		assert e.code==404
	print("[PASS] GET nonexistent task -404")
#测试422未通过数据校验
def test_invalid_type():
	post_url = f"{BASE_URL}/tasks"
	payload = {"task_type":"invalid_type","text":"this is 422 test"}
	data = json.dumps(payload).encode("utf-8")
	resp=urllib.request.Request(
		post_url,
		data=data,
		headers={"Content-Type":"application/json"},
		method="POST"
	)
	try:
		with urllib.request.urlopen(resp,timeout=TIMEOUT) as resp:
			raise AssertionError(f"预期422，实际{resp.status}")
	except urllib.error.HTTPError as e:
		assert e.status == 422
		error_result = json.loads(e.read().decode("utf-8"))
		error_type = error_result["detail"][0]["type"]
		assert error_type == "literal_error"
	print("[PASS] POST invalid payload - 422")
test_health()
task_id = test_post_task()
test_get_task(task_id)
test_not_found()
test_invalid_type()
