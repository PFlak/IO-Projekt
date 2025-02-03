from openai import OpenAI

class NoteTaker:
    def __init__(self, api_key):
        self._client = OpenAI(api_key=api_key)
        pass

    def update_api_key(self, api_key):
        self._client = OpenAI(api_key=api_key)
        pass
