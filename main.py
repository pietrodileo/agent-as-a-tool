# Example: Travel Planning System
from utils.logging import setup_logging

logger = setup_logging()

from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import time
from datetime import datetime

from models.llm_service import LLMService
from models.agents.abstract import AbstractAgent
from models.agents.tools import create_travel_agents, build_agent_tools

from langfuse import Langfuse

def load_environment() -> dict:
    """Load environment variables from .env."""
    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)
    env = dotenv_values(env_file)
    return env


def main() -> None:
    logger.info("Application started")
    env = load_environment()
    
    # Try to initialize Langfuse client
    try:
        langfuse_client = Langfuse(
            public_key=env.get("LANGFUSE_PUBLIC_KEY"),
            secret_key=env.get("LANGFUSE_SECRET_KEY"),
            host=env.get("LANGFUSE_BASE_URL", "https://challenges.reply.com/langfuse")
        )
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse client: {e}")
        langfuse_client = None

    logger.info(f"langfuse_client initialized: {langfuse_client}")

    default_think = "false"
    model: str | None = env.get("LLM_MODEL")
    think: bool = env.get("THINK", default_think).lower() == "true"
    chat_messages_in_memory = int(env.get("MESSAGE_MEMORY", 0))
    
    if not model:
        logger.error("LLM_MODEL environment variable is not set.")
        raise ValueError("LLM_MODEL environment variable is not set.")
    
    service = LLMService(
        model=model,
        base_url=env.get("OLLAMA_URL", "http://localhost:11434"),
        temperature=0.1,
        think=think,
        message_memory=chat_messages_in_memory,
        max_tokens=1024,
        langfuse_client=langfuse_client
    )
    travel_agents = create_travel_agents(service)
    orchestrator_tools = build_agent_tools(travel_agents)
    orchestrator = AbstractAgent(
        "orchestrator",
        service,
        orchestrator_tools,
        service.message_memory
    )

    quit_command = False
    chat_history = []
    while not quit_command:
        print(f"\n{datetime.now().strftime('%H:%M:%S')} - USER ('quit' to exit): ")
        user_input = input()

        if user_input.lower() == "quit":
            quit_command = True
            logger.info("User left the conversation.")
            break
            
        response = orchestrator.get_response(user_query=user_input, chat_history=chat_history)
        
        start_time = time.time()
        chunk = None
        print(f"{datetime.now().strftime('%H:%M:%S')} - AI: ")        
        thinking_label = False
        content = ""
        for chunk in response:
            if chunk["type"] == "thinking":
                if not thinking_label:
                    print("AI is thinking... ", end="", flush=True)
                    thinking_label = True
                content = chunk["content"]
            elif chunk["type"] == "content":
                content = chunk["content"]
            elif chunk["type"] == "tool_call":
                # avoid printing tool calls
                continue
            elif chunk["type"] == "end":
                continue
                # content = chunk["content"]
            else:
                raise ValueError(f"Unknown chunk type: {chunk['type']}")    
            print(content, end="", flush=True)
        
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": content})

        end_time = time.time()

        metadata = {
            "model": model,
            "latency_seconds": round(end_time - start_time, 3),
            "prompt_tokens": getattr(chunk, "prompt_eval_count", None),
            "completion_tokens": getattr(chunk, "eval_count", None),
            "total_tokens": (
                (getattr(chunk, "prompt_eval_count", 0) or 0)
                + (getattr(chunk, "eval_count", 0) or 0)
            )
        }

        # logger.info(f"LLM metadata: {metadata}")

    logger.info("Application stopped")
    
if __name__ == "__main__":
    main()