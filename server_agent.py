from fastapi import FastAPI

app = FastAPI()

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
