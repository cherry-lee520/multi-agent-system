class LengthAgent:
    def execute(self, text:str) -> dict[str, int]:
        return {"character_count":len(text)}