from contextlib import asynccontextmanager

from fastapi import FastAPI
from database import init_db
from task_agent import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/health")
def health():
	return {
		"status":"ok",
		"agent_id":"server-agent-01",
		"version":"0.1.0",
	}

@app.get("/hello")
def hello():
	return {
		"message":"Hello from my Multi-Agent System!",
		"server":"Ubuntu",
		"language":"Python",
	}
