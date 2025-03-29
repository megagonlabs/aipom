import json
from textwrap import dedent

from custom_types import NodeInputVars
from utils import openai_client

from .base_agent import BaseAgent


LLM_AGENT_REGISTRY = {
    "add": {
        "description": "add operands",
        "input": "list of operand name and value pair",
        "output": "one summed value",
        "output_format": "number",
    },
    "subtract": {
        "description": "subtract operands",
        "input": "list of operands name and value pair",
        "output": "one subtracted value",
        "output_format": "number",
    },
    "multiply": {
        "description": "multiply operands",
        "input": "list of operands name and value pair",
        "output": "one multiplied value",
        "output_format": "number",
    },
    "divide": {
        "description": "divide operands",
        "input": "list of operands name and value pair",
        "output": "one divided value",
        "output_format": "number",
    },
    "summarize": {
        "description": "summarize long input into short paragraph",
        "input": "long document",
        "output": "a paragraph",
        "output_format": "text",
    },
    "compare": {
        "description": "compare two or more items",
        "input": "a list of text query",
        "output": "one text entity of comparison result",
        "output_format": "text",
    },
    "extract": {
        "description": "extract smaller unit of text from given text",
        "input": "text",
        "output": "text entities",
        "output_format": "list",
    },
    # "identify_operands": {
    #     "description": "identify operands with text description of each operands",
    #     "input": "question",
    #     "output": "list of operand names with their numerical values",
    #     "output_format": "{<name>: number, ...}",
    # },
    # "arithmetic_operation": {
    #     "description": "perform arithmetic operations on numbers or dates",
    #     "input": "list of operands, operator",
    #     "output": "one calculated value",
    #     "output_format": "number or date",
    # },
    # "convert_format": {
    #     "description": "convert input from one format to another",
    #     "input": "text, format",
    #     "output": "formatted text",
    #     "output_format": "text",
    # },
    # "db_execution": {
    #     "description": "execute SQL queries on a database",
    #     "input": "SQL query",
    #     "output": "records in json format",
    #     "output_format": "list of dictionaries",
    # },
    # "fact_check": {
    #     "description": "check the validity of a statement",
    #     "input": "statement",
    #     "output": "True or False",
    #     "output_format": "boolean",
    # },
    # "nl2query": {
    #     "description": "convert natural language to SQL query",
    #     "input": "natural language question",
    #     "output": "SQL query",
    #     "output_format": "SQlite query that could be directly executed",
    # },
    # "web_search": {
    #     "description": "search the web for information",
    #     "input": "search query",
    #     "output": "list of search results",
    #     "output_format": "list of evidences in plain text",
    # },
    # "data_format_conversion": {
    #     "description": "convert data format from one to another. used as a utility agent to convert data format between two agents",
    #     "input": "any format",
    #     "output": "desired format",
    #     "input_format": "any, from the previous agent output",
    #     "output_format": "any, depends on the desired format of next agent",
    # },
    "fallback": {
        "description": "handles queries that do not match any specific mathematical operation, providing general assistance",
        "input": "any question or task description",
        "output": "answer",
        "output_format": "any",
    },
}


class LLMAgent(BaseAgent):
    def __init__(
        self,
        agent: str,
        config: dict = {"model": "gpt-4o", "temperature": 0},
    ):
        self.agent_name = agent
        self.config = config
        self.client = openai_client
        self.set_system_prompt()

    def set_system_prompt(self):
        """
        Sets the system prompt for the specific LLM agent based on the agent's description.
        """
        agent = LLM_AGENT_REGISTRY[self.agent_name]
        self.system_prompt = dedent(
            f"""
            You are a helpful assistant for '{self.agent_name}' task. Your job is to {agent['description']}.
            Your input will be '{agent['input']}' and your output should be '{agent['output']}'. Keep your answer concise and short. Do not explain.
            Your answer should be in JSON, with given output keys and output values in {agent['output_format']}."""
        )

    def execute(
        self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict
    ) -> dict:
        """
        Executes the LLM agent using the OpenAI API.
        """
        prompt = "Task: {task}\n\nInput: {input_vars}\n\nOutput keys: {output_vars}"
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": prompt.format(
                    task=task, input_vars=input_vars, output_vars=output_vars
                ),
            },
        ]
        config = self.config.copy()
        config.update(params)
        response = self.client.chat.completions.create(
            messages=messages, **config, response_format={"type": "json_object"}
        )
        response_obj = json.loads(response.choices[0].message.content)
        return response_obj


class IdentifyOperandsAgent:
    def __init__(self):
        self.config = {"model": "gpt-4o", "temperature": 0}
    def execute(
        self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict
    ) -> dict:
        """Extracts numeric operands from a given expression."""
        GSM_PROMPT_ID = """
            From a given mathematical task extract the required expressions and their value from the text. 
            Only extract those expressions which has been mentioned in the task. Use the query to obtain values.

            Your output should be a dictionary with variable names as keys eg. "number_of_chocolates" and corresponding value eg \"number_of_chocolates\": 10
            Your response should be in JSON strictly with the following output keys {output_vars}
            Task = {task}
            Input:
            {input_vars}
        """
        messages = [
            # {"role": "system", "content": "Your response should be in JSON with the following output keys {output_vars}"},
            {
                "role": "user",
                "content": GSM_PROMPT_ID.format(
                    task=task, input_vars=input_vars, output_vars=output_vars
                ),
            },
        ]
        config = self.config.copy()
        config.update(params)
        response = openai_client.beta.chat.completions.parse(
            messages=messages, **config, response_format={"type": "json_object"}
        )
        response_obj = json.loads(response.choices[0].message.content)
        return response_obj
