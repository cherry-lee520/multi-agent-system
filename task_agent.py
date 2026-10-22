from uuid import uuid4
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel,Field,ConfigDict
from task_executor import execute_text_length
from typing import Literal

class TaskRequest(BaseModel):
	model_config = ConfigDict(extra="forbid")

	task_type: Literal["text_length"]
	text:str = Field(min_length=1,max_length=10000)

router = APIRouter()

tasks = {} #保存所有任务
@router.post("/tasks",status_code=201)
def check_task(task:TaskRequest):
	if len(tasks)>999:
		raise HTTPException(status_code=503,detail="Task storage is full")

	task_id = str(uuid4())
	match task.task_type:
		case "text_length":
			result = execute_text_length(task.text)
			record = {"task_id":task_id,
				  "task_type":task.task_type,
				  "status":"succeeded",
				  "result":result}
			tasks[task_id] = record
			return record
		case _:
			raise HTTPException(
				status_code=422,
				detail="Unsupported task type")
@router.get("/tasks/{task_id}")
def get_task(task_id:str):
	if task_id not in tasks:
		raise HTTPException(status_code=404,detail="Task not found")
	return tasks[task_id]
