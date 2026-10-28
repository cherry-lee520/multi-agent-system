class WordCountAgent:
    def execute(self, text: str) -> dict[str, int]:
        return {"word_count": len(text.split())}