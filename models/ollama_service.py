from ollama import chat
from typing import Generator, Dict, List
from logging import Logger

logger = Logger(__name__)

class OllamaService:
    def __init__(self, model:str, think:bool=False, message_memory:int=0, max_tokens:int=512):
        self.model = model
        self.think = think
        self.message_memory=message_memory
        self.max_tokens=max_tokens

    def get_response(self, user_query: str, chat_history: List[Dict[str, str]]) -> Generator[Dict[str,str]]:
        """
        Generate a response to the user query based on the chat history.

        Args:
            user_query (str): The query from the user.
            chat_history (List[Dict[str, str]]): The chat history.

        Yields:
            Generator[Dict[str,str]]: A stream of messages to be sent to the user.
        """

        # keep only the last N messages in the context
        if self.message_memory > 0:
            history = chat_history[-self.message_memory:]
        else:
            history = chat_history

        messages = history + [{"role": "user", "content": user_query}]

        stream = chat(
            model=self.model,
            messages=messages,
            options={
                "num_ctx": self.max_tokens,
            },
            stream=True,
            think=self.think,
        )

        content = ""
        chunk = None
        for chunk in stream:
            if chunk.message.thinking:
                yield {
                    "type": "thinking",
                    "content": chunk.message.thinking
                }
            if chunk.message.content:
                content += chunk.message.content
                yield {
                    "type": "content",
                    "content": chunk.message.content
                }