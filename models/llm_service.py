import logging

logger = logging.getLogger('agents_test')

from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from typing import Optional,List,Dict,Generator
from langfuse import Langfuse

class LLMService:
    """
        Wrapper for llm BaseChatModel
    """
    def __init__(self, 
                 llm_type:str, 
                 model:str, base_url:str, 
                 temperature:float, 
                 think:bool=False, 
                 message_memory: int = 0, 
                 max_tokens: Optional[int] = 512, 
                 api_key: Optional[str] = None,
                 langfuse_client: Optional[Langfuse] = None):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.message_memory = message_memory
        self.max_tokens = max_tokens
        self.think = think        
        self.api_key = api_key
        self.langfuse_client = langfuse_client

        if llm_type == "ollama":        
            self.llm: BaseChatModel = ChatOllama(model=self.model, 
                            temperature=self.temperature, 
                            reasoning=self.think, 
                            num_predict=self.max_tokens,
                            base_url=self.base_url,
                            )
        elif llm_type == "mistral":        
            self.llm: BaseChatModel = ChatMistralAI(
                model_name=self.model,
                temperature=self.temperature, 
                api_key=self.api_key
            )
                
    def _convert_history(self, history: List[Dict[str, str]]):
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages        
        
    def get_response(self, user_query: str, chat_history: List[Dict[str, str]]) -> Generator[Dict[str, str], None, None]:
        # memory trimming
        if self.message_memory > 0:
            history = chat_history[-self.message_memory:]
        else:
            history = chat_history

        messages = self._convert_history(history)
        messages.append(HumanMessage(content=user_query))

        stream = self.llm.stream(messages)

        content = ""
        for chunk in stream:
            if chunk.content:
                if isinstance(chunk.content, str):
                    chunk_content = chunk.content
                else:
                    raise ValueError("Chunk content is not a string")
                content += chunk_content
                yield {
                    "type": "content",
                    "content": chunk_content
                }

        yield {
            "type": "end",
            "content": content
        }
        
    def __repr__(self) -> str:
        return f"""
            LLMService(
                model_name={self.model}, 
                temperature={self.temperature}, 
                think={self.think}, 
                message_memory={self.message_memory}, 
                max_tokens={self.max_tokens},
                base_url={self.base_url},
                api_key={self.api_key}
            )
        """ 