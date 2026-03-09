import logging

logger = logging.getLogger('agents_test')

from typing import List
from langchain_core.language_models.chat_models import BaseChatModel
from models.prompt_manager import PromptManager
from langchain.agents import create_agent
from collections.abc import Sequence
from langchain_core.tools import BaseTool
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from typing import Generator, Dict, List, Optional
from langchain_core.messages import AIMessageChunk, ToolMessage
import json 
import ulid
from langfuse import observe
from langfuse.langchain import CallbackHandler
from ..llm_service import LLMService

class AbstractAgent():
    """
    Abstract class for an agent.
    """
    def __init__(self, name: str, llm_service: LLMService, tools: Optional[Sequence[BaseTool]], message_memory: int = 0) -> None:
        self.name = name
        self.llm = llm_service.llm
        self.pm = PromptManager()
        self.system_prompt = self.pm.get_prompt(name, "system_prompt")        
        self.tools = tools
        self.create_time = datetime.now()
        self.message_memory = message_memory
        self.tools = tools or []
        self.agent = create_agent(
            name=name,
            model=self.llm,
            system_prompt=self.system_prompt,
            tools=self.tools
        )    
        self.langfuse_client = llm_service.langfuse_client if llm_service.langfuse_client is not None else None

    def show_system_prompt(self):
        print(self.system_prompt)
        
    def show_tools(self):
        print(self.tools)

    def show_agent(self):
        print(self.agent)
        
    def __repr__(self) -> str:
        return f"AbstractAgent(name={self.name}, llm={self.llm}, tools={self.tools}, message_memory={self.message_memory}. Created at {self.create_time.strftime('%Y-%m-%d %H:%M:%S')})"
  
    def get_response(self, user_query: str,chat_history: List[Dict[str, str]]) -> Generator[Dict[str, str]]:        
        """
        Generate a response to the user query based on the chat history.

        Args:
            user_query (str): The query from the user.
            chat_history (List[Dict[str, str]]): The chat history.

        Yields:
            Generator[Dict[str, str]]: A stream of messages to be sent to the user.
        """
        
        # give the agent only the last n messages
        if self.message_memory > 0:
            history = chat_history[-self.message_memory:]
        else:
            history = chat_history

        messages = self._convert_history(history)
        messages.append(HumanMessage(content=user_query))

        # # agent stream 
        # stream = self.agent.stream(
        #     {"messages": messages},
        #     stream_mode="messages"
        # )

        stream = self.run_llm_call(messages,stream=True)

        content = ""
        for event in stream:
            if isinstance(event, tuple):
                # AIMessageChunk
                message_chunk = self.tuple_safe_get(event, 0, default=None)
                # langchain metadata 
                metadata = self.tuple_safe_get(event, 1, default=None)
            else: 
                raise(ValueError) 
                         
            # handle tool messages
            if isinstance(message_chunk,ToolMessage):
                # logger.info(f"Tool answered with content: {event}")   
                continue

            if not isinstance(message_chunk, AIMessageChunk):
                continue
            
            # check for reasoning chunks
            reasoning_chunk = message_chunk.additional_kwargs.get("reasoning_content")
            if reasoning_chunk:
                yield {
                    "type": "thinking",
                    "content": reasoning_chunk
                }
            
            # normal output content
            if message_chunk.content:
                chunk_content = message_chunk.content
                content += chunk_content
                yield {
                    "type": "content",
                    "content": chunk_content
                }
            
            # Check for tool calls
            if message_chunk.tool_calls:
                for tool_call in message_chunk.tool_calls:
                    args = tool_call.get('args')
                    # convert dict to str
                    args_str = json.dumps(args)  
                    yield {
                        "type":"tool_call",
                        "tool": tool_call.get('name'),
                        "content": args_str
                    }
                    
        yield {
            "type": "end",
            "content": content
        }
        
    def _convert_history(self, history: List[Dict[str, str]]):
        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages        
    
    @staticmethod
    def tuple_safe_get(tuple_input: tuple, index: int, default=None):
        """
        Safely get an element from a tuple by index.

        Args:
            tuple_input (tuple): The tuple to access.
            index (int): Index of the element to retrieve.
            default (any, optional): Value to return if index is out of range. Defaults to None.

        Returns:
            any: The element at the given index, or the default value if index is invalid.
        """
        try:
            return tuple_input[index]
        except (IndexError, TypeError):
            return default

    @staticmethod
    def generate_session_id():
        """Generate a unique session ID using TEAM_NAME and ULID."""
        return f"test-{ulid.ulid()}" 
    
    @observe()
    def run_llm_call(self, messages, stream: bool = False):
        """Run a single LangChain invocation and track it in Langfuse."""
        callbacks = None
        # prepare callback handler for langfuse client
        if self.langfuse_client is not None:
            session_id = self.generate_session_id()
            # Update trace with session_id
            self.langfuse_client.update_current_trace(
                session_id=session_id,
                name=f"{self.name}_agent"
            )
            # Create Langfuse callback handler for automatic generation tracking
            # The handler will attach to the current trace created by @observe()
            langfuse_handler = CallbackHandler()
            callbacks = [langfuse_handler]

        # Invoke LangChain with Langfuse handler to track tokens and costs
        if stream:
            response = self.agent.stream(
                {"messages": messages},
                config={"callbacks": callbacks} if callbacks else None,
                stream_mode="messages",
            )
        else:
            response = self.agent.invoke(
                {"messages": messages}, 
                config={"callbacks": callbacks} if callbacks else None
            )

        return response
