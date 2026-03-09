from langchain.tools import tool
from langchain_core.messages import HumanMessage

from models.agents.abstract import AbstractAgent
from models.llm_service import LLMService

def create_travel_agents(service: LLMService):

    logistics_agent = AbstractAgent(
        "logistic",
        service,
        None,
        service.message_memory
    )

    recommendations_agent = AbstractAgent(
        "recommendation",
        service,
        None,
        service.message_memory
    )

    return {
        "logistic": logistics_agent,
        "recommendation": recommendations_agent
    }

def build_agent_tools(agents):
    """
    Build tools for travel agents using the Agents as a Tool Pattern.

    Parameters:
    agents (dict): A dictionary of travel agents.

    Returns:
    list: A list of tools.

    """

    logistic_agent = agents["logistic"]
    recommendation_agent = agents["recommendation"]

    @tool
    def plan_logistics_agent(trip_request: str) -> str:
        """Plan travel logistics including routes, times and costs."""
        messages = [HumanMessage(content=trip_request)]
        response = logistic_agent.run_llm_call(messages)
        tool_response = response["messages"][-1].content
        return tool_response

    @tool
    def get_recommendations_agent(trip_details: str) -> str:
        """Provide travel recommendations."""
        messages = [HumanMessage(content=trip_details)]
        response = recommendation_agent.run_llm_call(messages)
        tool_response = response["messages"][-1].content
        return tool_response

    return [
        plan_logistics_agent,
        get_recommendations_agent
    ]