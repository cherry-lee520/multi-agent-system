from agents.length_agent import LengthAgent
from agents.word_count_agent import WordCountAgent


AGENTS = {
    "text_length": LengthAgent(),
    "word_count": WordCountAgent(),
}


def dispatch_task(task_type: str, text: str) -> dict[str, int]:
    agent = AGENTS.get(task_type)

    if agent is None:
        raise ValueError(f"Unsupported task type: {task_type}")

    return agent.execute(text)