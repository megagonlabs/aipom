import json

from custom_types import LLMPlan
from plan import PlanConverter, PlanDAG
from prompts import PLAN_REFINE_PROMPT, PLAN_SYSTEM_PROMPT, PLAN_FIX_PROMPT
from utils import openai_client


class Planner:
    """
    Handles the management, generation, refinement and replanning of plans.

    Attributes:
        plan_history (list[PlanDAG]): Stores different versions of the plan.
        system_prompt (str): System prompt template for LLM interaction.
        refine_prompt (str): Template for refining plans.
        fix_plan_prompt (str): Template for fixing incomplete or incorrect plans.
        client (object): OpenAI client used for LLM interactions.
        config (dict): Configuration parameters for the model execution.
        agent_registry (AgentRegistry): Registry containing all available agents.
    """
    def __init__(self, agent_registry):
        """Initializes planner with agent registry, and required prompts and configurations"""
        self.plan_history: list[PlanDAG] = [] # Stores different versions of the plan, list[PlanDAG]
        self.system_prompt = PLAN_SYSTEM_PROMPT.format(
            agent_registry=agent_registry.get_agents_description()
        )
        self.refine_prompt = PLAN_REFINE_PROMPT
        self.fix_plan_prompt = PLAN_FIX_PROMPT
        self.client = openai_client
        self.config = {"model": "gpt-4o", "temperature": 0, "response_format": LLMPlan}
        self.agent_registry = agent_registry
        self.agent_names = agent_registry.get_agents_names()

    def modify_config(self, params):
        """Modifies the LLM configuration."""
        self.config.update(params)

    def append_plan(self, plan):
        """Appends a new plan to the history."""
        self.plan_history.append(plan)

    def generate_plan(self, query: str, is_replan: bool = False) -> PlanDAG:
        """
        Generates a new plan based on the user query.

        Args:
            query (str): The user's query or task description.
            is_replan (bool): Indicates if it is a replan (default: False).

        Returns:
            PlanDAG: The generated plan in DAG format.
        """
        llm_plan = self._llm_planner(query)
        plan = PlanDAG().initialize_from_LLMPlan(query, llm_plan, self.agent_names)
        if not is_replan:
            plan.initialize_plan_status()
            plan.intitialize_exec_status()
        else:
            plan.set_plan_status("MODIFIED")
        plan.initialize_params(agent_registry=self.agent_registry)
        self.plan_history.append(plan)
        return plan

    def refine_plan(self, query):
        """Refine plan using query and dag manipulation"""
        pass

    def fix_plan(self, plan):
        """
        Fixes a given plan using LLM correction.

        Args:
            plan (dict): The plan to fix.

        Returns:
            PlanDAG: The corrected plan.
        """
        query = plan.query
        plan = PlanConverter.dag_to_LLMPlan(plan.dag)
        llm_plan = self._llm_fixer(query, plan)
        plan = PlanDAG().initialize_from_LLMPlan(query, llm_plan, self.agent_names)
        plan.initialize_plan_status()
        plan.intitialize_exec_status()
        plan.initialize_params(agent_registry=self.agent_registry)
        self.plan_history.append(plan)
        return plan 

    def add_node(self, prev_plan, node_id, node_data):
        """
        Adds a new node to the plan.

        Args:
            prev_plan (PlanDAG): The previous plan.
            node_id (int): id of the node to add.
            node_data (dict): Data associated with the new node.

        Returns:
            PlanDAG: The updated plan.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.add_node(node_id, node_data)
        plan.set_node_plan_status(node_id, "MODIFIED")
        self.plan_history.append(plan)
        return plan

    def remove_node(self, prev_plan, node_id):
        """
        Removes a node from the plan.

        Args:
            prev_plan (PlanDAG): The previous plan.
            node_id (int): id of the node to remove.

        Returns:
            PlanDAG: The updated plan.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.remove_node(node_id)
        self.plan_history.append(plan)
        return plan

    def update_node(self, prev_plan, node_id, node_data):
        """
        Updates a node's attributes in the plan.

        Args:
            prev_plan (PlanDAG): The previous plan.
            node_id (int): id of the node to update.
            node_data (dict): Updated node attributes.

        Returns:
            PlanDAG: The updated plan.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.update_node(node_id, node_data)
        plan.set_node_plan_status(node_id, "MODIFIED")
        self.plan_history.append(plan)
        return plan
    
    def update_node_edge(self, prev_plan, node_id, node_data, edges):
        """
        Updates a node and its corresponding edges.

        Args:
            prev_plan (PlanDAG): The previous plan.
            node_id (int): id of the node to update.
            node_data (dict): Updated node attributes.
            edges (list[dict]): List of edges to update.

        Returns:
            PlanDAG: The updated plan.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.update_node_edge(node_id, node_data, edges)
        plan.set_node_plan_status(node_id, "MODIFIED")
        self.plan_history.append(plan)
        return plan

    def add_edge(self, prev_plan, src, dest, edge_data):
        """
        Adds an edge between two nodes.

        Args:
            prev_plan (PlanDAG): The previous plan.
            src (int): Source node id.
            dest (int): Destination node id.
            edge_data (dict): Edge attributes.

        Returns:
            PlanDAG: The updated plan.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.add_edge(src, dest, edge_data)
        plan.set_edge_plan_status(src, dest, "MODIFIED", key=(edge_data["src_output"], edge_data["dest_input"]))
        self.plan_history.append(plan)
        return plan

    def remove_edge(self, prev_plan, src, dest, edge_data):
        """
        Removes an edge from the plan.

        Args:
            prev_plan (PlanDAG): The previous plan.
            src (int): Source node id.
            dest (int): Destination node id.
            edge_data (dict): Edge attributes.

        Returns:
            PlanDAG: The updated plan.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.remove_edge(src, dest, edge_data)
        self.plan_history.append(plan)
        return plan
    
    def update_exec(self, prev_plan, node_id, node_exec, node_attr, node_attr_value):
        """
        Updates the execution results and status of a node in the plan.

        Args:
            prev_plan (PlanDAG): The previous plan.
            node_id (int): id of the node to update.
            node_exec (dict): Execution data to be updated.

        Returns:
            PlanDAG: The updated plan with modified execution results and status.
        """
        plan = PlanDAG().initialize_from_dag(prev_plan.copy())
        plan.update_exec(node_id, node_exec, node_attr, node_attr_value)
        plan.set_node_exec_status(node_id, "MODIFIED")
        self.plan_history.append(plan)
        return plan

    def refine_plan_nl(self, feedback: str) -> PlanDAG:
        """
        Refines the existing plan using natural language feedback.

        Args:
            feedback (str): User-provided feedback in natural language.

        Returns:
            PlanDAG: The refined plan with modifications applied.
        """
        prev_plan = self.get_latest_plan()
        prev_llm_plan = PlanConverter.dag_to_LLMPlan(prev_plan.dag)
        llm_plan = self._llm_refiner(prev_plan=prev_llm_plan, feedback=feedback)
        plan = PlanDAG().initialize_from_LLMPlan(prev_plan.query, llm_plan, self.agent_names)
        plan.set_plan_status("MODIFIED")
        plan.initialize_params(agent_registry=self.agent_registry)
        self.plan_history.append(plan)
        return plan

    def refine_plan_dm(self, refined_plan) -> PlanDAG:
        """
        Refines the existing plan using direct manipulation.

        Args:
            refined_plan (PlanDAG): The refined plan after direct manipulation.

        Returns:
            PlanDAG: The updated plan with modifications.
        """
        self.plan_history.append(refined_plan)
        pass

    def get_latest_plan(self) -> PlanDAG:
        """Retrieves the most recent plan if available."""
        return self.plan_history[-1] if self.plan_history else None

    def clear(self) -> None:
        """
        Clears the plan history.
        """
        self.plan_history = []


    def _llm_planner(self, query: str) -> LLMPlan:
        """
        Uses LLM to generate a plan based on the user query.

        Args:
            query (str): The user query to generate the plan.

        Returns:
            LLMPlan: The generated plan in LLM format.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]
        response = self.client.beta.chat.completions.parse(
            messages=messages, **self.config
        )
        response_obj = json.loads(response.choices[0].message.content)
        return response_obj

    def _llm_refiner(self, prev_plan, feedback):
        """
        Refines the existing plan using LLM based on user feedback.

        Args:
            prev_plan (LLMPlan): The previous plan to refine.
            feedback (str): User-provided feedback in natural language.

        Returns:
            LLMPlan: The refined plan in LLM format.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": self.refine_prompt.format(
                    prev_plan=prev_plan, feedback=feedback
                ),
            },
        ]
        response = self.client.beta.chat.completions.parse(
            messages=messages, **self.config
        )
        response_obj = json.loads(response.choices[0].message.content)
        return response_obj
    
    def _llm_fixer(self, query, plan):
        """
        Fixes an initial or incomplete plan using LLM.

        Args:
            query (str): The initial user query.
            plan (dict): The incomplete or incorrect plan.

        Returns:
            LLMPlan: The corrected plan in LLM format.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": self.fix_plan_prompt.format(
                    query=query, plan=plan
                ),
            },
        ]
        response = self.client.beta.chat.completions.parse(
            messages=messages, **self.config
        )
        response_obj = json.loads(response.choices[0].message.content)
        return response_obj