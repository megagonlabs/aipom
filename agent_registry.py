from agents import *

class AgentRegistry:
    """
    Registry class manage different agents, their configurations, and descriptions.
    Attributes:
        agents (dict): A dictionary mapping agent names to their corresponding instances, descriptions, and configurations.
    """
    def __init__(self):
        """
        Initializes the AgentRegistry, with instances of agents and their descriptions and configuration
        """
        identify_operands_agent = IdentifyOperandsAgent()
        add_agent = AddAgent()
        multiply_agent = MultiplyAgent()
        subtract_agent = SubtractAgent()
        divide_agent = DivideAgent()
        add_llm_agent = LLMAgent(agent="add")
        multiply_llm_agent = LLMAgent(agent="multiply")
        subtract_llm_agent = LLMAgent(agent="subtract")
        divide_llm_agent = LLMAgent(agent="divide")
        fallback_agent = LLMAgent(agent="fallback")
        # web_search_agent = WebSearchAgent()
        # extract_agent = LLMAgent(agent="extract")
        # summarize_agent = LLMAgent(agent="summarize")
        # compare_agent = LLMAgent(agent="compare")

        self.agents = {
            "identify_operands": {
                "class": identify_operands_agent,
                "description": "Identifies and extracts operands from query.",
                "default_config": identify_operands_agent.config
            },
            "add": {
                "class": add_agent,
                "description": "Add given operands.",
                "default_config": add_agent.config
            },
            "multiply": {
                "class": multiply_agent,
                "description": "Multiply given operands.",
                "default_config": multiply_agent.config
            },
            "subtract": {
                "class": subtract_agent,
                "description": "Subtract given operands.",
                "default_config": subtract_agent.config
            },
            "divide": {
                "class": divide_agent,
                "description": "Divide given operands.",
                "default_config": divide_agent.config
            },
            "add-llm": {
                "class": add_llm_agent,
                "description": "Add given operands using LLM.",
                "default_config": add_llm_agent.config
            },
            "multiply-llm": {
                "class": multiply_llm_agent,
                "description": "Multiply given operands using LLM.",
                "default_config": multiply_llm_agent.config
            },
            "subtract-llm": {
                "class": subtract_llm_agent,
                "description": "Subtract given operands using LLM.",
                "default_config": subtract_llm_agent.config
            },
            "divide-llm": {
                "class": divide_llm_agent,
                "description": "Divide given operands using LLM.",
                "default_config": divide_llm_agent.config
            },
            # "web_search": {
            #     "class": web_search_agent,
            #     "description": "Search the web for information on input query.",
            #     "default_config": web_search_agent.config
            # },
            # "extract": {
            #     "class": extract_agent,
            #     "description": "Extract entities from text",
            #     "default_config": extract_agent.config
            # },
            # "summarize": {
            #     "class": summarize_agent,
            #     "description": "Summarize long input into short paragraph",
            #     "default_config": summarize_agent.config
            # },
            # "compare": {
            #     "class": compare_agent,
            #     "description": "Compare two or more items",
            #     "default_config": compare_agent.config
            # },
            "fallback": {
                "class": fallback_agent,
                "description": "Handles queries that do not match any specific mathematical operation, providing general assistance.",
                "default_config": fallback_agent.config
            },
        }

    def get_agent(self, agent_name):
        """
        Retrieves the agent instance by its name.

        Args:
            agent_name (str): The name of the agent to retrieve.

        Returns:
            object: The agent instance if found, otherwise None.
        """
        agent_info = self.agents.get(agent_name, None)
        return agent_info["class"] if agent_info else None
    
    def get_agent_default_config(self, agent_name):
        """
        Retrieves the default configuration of the specified agent.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            dict: The default configuration of the agent, or None if not found.
        """
        agent_info = self.agents.get(agent_name, None)
        return agent_info["default_config"] if agent_info else None

    def get_agents_names(self):
        """
        Retrieves a list of all agent names.

        Returns:
            A list of strings
        """
        agents = []
        for agent_name, val in self.agents.items():
            agents.append(agent_name)
        return agents

    def get_agents_list(self):
        """
        Retrieves a list of all agents with their names and default configurations.

        Returns:
            A list of dictionaries containing agent names and their default configurations.
        """
        agents = []
        for agent_name, val in self.agents.items():
            agents.append({
                "agent_name": agent_name,
                "default_config": val["default_config"]
            })
        return agents

    def get_agents_description(self):
        """
        Retrieves a formatted string with the descriptions of all agents.

        Returns:
            str: A string containing the name and description of each agent.
        """
        agents = ""
        for agent_name, agent_info in self.agents.items():
            agents += f"{agent_name}: {agent_info['description']}\n"
        return agents
