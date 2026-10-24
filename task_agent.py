from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, APIRouter
from database import create_task, get_task as get_task_from_db, count_tasks
from pydantic import BaseModel,Field,ConfigDict
from task_executor import execute_text_length
from typing import Literal

class TaskRequest(BaseModel):
	model_config = ConfigDict(extra="forbid")

	task_type: Literal["text_length"]
	text:str = Field(min_length=1,max_length=10000)

router = APIRouter()

@router.post("/tasks",status_code=201)
def check_task(task:TaskRequest):
	if count_tasks() >= 1000:
		raise HTTPException(status_code=503,detail="Task storage is full")

	task_id = str(uuid4())
	match task.task_type:
		case "text_length":
			result = execute_text_length(task.text)
			record = {"task_id":task_id,
				  "task_type":task.task_type,
				  "status":"succeeded",
				  "result":result}
			create_task({
				**record,
				"created_at": datetime.now(timezone.utc).isoformat(),
			})
			return record
		case _:
			raise HTTPException(
				status_code=422,
				detail="Unsupported task type")
@router.get("/tasks/{task_id}")
def get_task(task_id:str):
	record = get_task_from_db(task_id)
	if record is None:
		raise HTTPException(status_code=404,detail="Task not found")
	# created_at 仅用于数据库存储，保持现有 API 响应字段。
	return {key: record[key] for key in ("task_id", "task_type", "status", "result")}
