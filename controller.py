import json
import traceback

from networkx import MultiDiGraph

from agent_registry import AgentRegistry
from custom_types import (Action, ExecuteData, InteractionData, Message,
                          SystemMessage, UserMessage, action_schema)
from executor import Executor
from planner import Planner
from prompts import *
from utils import InteractionType, current_time, openai_client


class Controller:
    """
    The Controller class manages the interaction flow between the user, planner, and executor.
    It handles user messages, UI interactions, and execution requests, maintaining the plan state 
    and generating appropriate responses.

    Attributes:
        interaction_log (list[InteractionData]): Stores user interactions with the UI.
        chat_history (list[Message]): Tracks the conversation history.
        registry (AgentRegistry): Handles agent configurations and retrievals.
        planner (Planner): Manages planning operations.
        executor (Executor): Handles plan execution.
        config (dict): Configuration settings for the LLM.
        client (OpenAI client): The LLM client for generating responses.
    """
    def __init__(self):
        """Initializes the Controller with empty logs, a planner, and an executor."""
        self.interaction_log: list[InteractionData] = []
        self.chat_history: list[Message] = []
        self.registry = AgentRegistry()
        self.planner = Planner(self.registry)
        self.executor = Executor(self.registry)
        self.config = {"model": "gpt-4o-mini", "temperature": 0}
        self.client = openai_client

    def process_user_message(self, user_message: UserMessage) -> tuple[MultiDiGraph | None, SystemMessage | None]:
        """
        Processes a user message, determines the action, and generates a system response.

        Args:
            user_message (UserMessage): The message sent by the user.

        Returns:
            tuple[MultiDiGraph | None, SystemMessage | None]: 
                - The updated plan DAG or None if no plan is generated.
                - The system response message.
        """
        self.chat_history.append(user_message)
        action = self._classify_intent()
        if action["action"] == 1: # plan
            if len(self.chat_history) == 1:
                plan = self.planner.generate_plan(user_message["content"])
            else:
                plan = self.planner.generate_plan(action["user_query"])
            system_message = self._generate_response(
                action, response_to=user_message["id"], plan=plan
            )
            plan_dag = plan.dag
        elif action["action"] == 2: # feedback
            plan = self.planner.refine_plan_nl(action["plan_feedback"])
            system_message = self._generate_response(
                action, response_to=user_message["id"], plan=plan
            )
            plan_dag = plan.dag
        elif action["action"] == 3: # execute
            plan_dag, system_message = self.process_execution(
                action["execute"], response_to=user_message["id"]
            )
        else: # ask for clarification
            plan_dag = None
            system_message = self._generate_response(action, response_to=user_message["id"])

        self.chat_history.append(system_message)
        return plan_dag, system_message

    def process_ui_interaction(self, interaction: InteractionData, response_to: int = -1) -> tuple[MultiDiGraph | None, SystemMessage | None]:
        """
        Processes user interactions from the UI and updates the DAG accordingly.

        Args:
            interaction (InteractionData): The UI interaction data.
            response_to (int): The id of the message being responded to.

        Returns:
            tuple[MultiDiGraph | None, SystemMessage | None]:
                - The updated plan DAG or None if no plan is generated.
                - The system response message.
        
        Raises:
            Exception: If no previous plan exists when modifying the plan.
        """
        self.interaction_log.append(interaction)
        plan = None
        system_response = None
        prev_plan = self.planner.get_latest_plan()

        if not prev_plan:
            return None, self._generate_response(
                    action={'action': 5, 'ex': "No plan to update"},
                    response_to=response_to
                )

        match interaction["interaction"]:
            case InteractionType.ADD_NODE:
                # interaction example = {"interaction": "add_node", "n": <new node id>, "n_attr": <new node attr>, "plan": <resulting plan>}
                plan = self.planner.add_node(
                    prev_plan=prev_plan,
                    node_id=interaction["n"],
                    node_data=interaction["n_attr"],
                )
            case InteractionType.REMOVE_NODE:
                # interaction example = {"interaction": "remove_node", "n": <new node id>, "n_attr": <new node attr>, "plan": <resulting plan>}
                plan = self.planner.remove_node(
                    prev_plan=prev_plan,
                    node_id=interaction["n"],
                )
            case InteractionType.ADD_EDGE:
                # interaction example = {"interaction": "add_edge", "e_s": <added edge source>, "e_t": <added edge target>, "e_attr": <added edge attr>, "plan": <resulting plan>}
                plan = self.planner.add_edge(
                    prev_plan=prev_plan,
                    src=interaction["e_s"],
                    dest=interaction["e_t"],
                    edge_data=interaction["e_attr"]
                )
            case InteractionType.REMOVE_EDGE:
                # interaction example = {"interaction": "remove_edge", "e_s": <removed edge source>, "e_t": <removed edge target>, "e_attr": <added edge attr>, "plan": <resulting plan>}
                plan = self.planner.remove_edge(
                    prev_plan=prev_plan,
                    src=interaction["e_s"],
                    dest=interaction["e_t"],
                    edge_data=interaction["e_attr"]
                )
            case InteractionType.MODIFY_NODE:
                # interaction example = {"interaction": "modify_node", "n": <changed node id>, "n_attr": <modified node attr>, "plan": <resulting plan>}
                plan = self.planner.update_node(
                    prev_plan=prev_plan,
                    node_id=interaction["n"],
                    node_data=interaction["n_attr"],
                )
            case InteractionType.MODIFY_NODE_EDGES:
                # interaction example = {"interaction": "modify_node_edges", "n": <changed node id>, "n_attr": <modified node attr>, "edges": <updated edges>, "plan": <resulting plan>}
                plan = self.planner.update_node_edge(
                    prev_plan=prev_plan,
                    node_id=interaction["n"],
                    node_data=interaction["n_attr"],
                    edges=interaction["edges"]
                )
            case InteractionType.UPDATE_EXEC:
                # interaction example = {"interaction": "update_exec", "n": <changed node id>, "n_exec": <updated execution output>, "plan": <resulting plan>}
                plan = self.planner.update_exec(
                    prev_plan=prev_plan,
                    node_id=interaction["n"],
                    node_exec=interaction["n_exec"],
                    node_attr=interaction["n_exec_attr"],
                    node_attr_value=interaction["n_exec_attr_value"]
                )
            case InteractionType.REPLAN:
                # interaction example = {"interaction": "replan"}
                plan = self.planner.generate_plan(prev_plan.query, is_replan=True)
            case InteractionType.FIX_PLAN:
                # interaction example = {"interaction": "fix_plan", "plan": <resulting plan>}
                plan = self.planner.fix_plan(prev_plan)
            case InteractionType.SPLIT_NODE:
                pass
            case InteractionType.MERGE_NODES:
                pass
        action = {
            "action": 4,
            "interaction": {
                "type": interaction["interaction"], 
            }
        }
        system_response = self._generate_response(
            action, response_to=response_to, plan=plan
        )
        return plan.dag, system_response

    def process_execution(self, exec_request: ExecuteData, response_to: int = -1) -> tuple[MultiDiGraph | None, SystemMessage | None]:
        """
        Executes the plan or a specific node based on the mode.

        Args:
            exec_request (ExecuteData): The execution request details.
            response_to (int): The id of the message being responded to.

        Returns:
            tuple[MultiDiGraph | None, SystemMessage | None]:
                - The updated DAG after execution.
                - The system response message.

        Raises:
            Exception: If dependencies are not met or the node cannot be executed.
        """
        plan = None
        system_response = None
        mode = exec_request.get("mode")
        plan = self.planner.get_latest_plan()
        self.executor.set_plan(plan)

        if mode == "all":
            try:
                self.executor.execute_plan()
            except Exception as ex:
                return self.executor.get_plan().dag, self._generate_response(
                    action={'action': 5, 'ex': f"Error: {ex}"},
                    response_to=response_to
                )
            plan = self.executor.get_plan() # obtain executed plan and results
            plan.set_exec_status("EXECUTED")
            system_response = self._generate_response(
                {"action": 3, "execute": {"mode": "all"}}, response_to=response_to, plan=plan
            )

        elif mode == "single":
            node_id = exec_request.get("node_id")
            if not self.executor.plan_dag and not self.executor.is_source_node(node_id):
                return None, self._generate_response(
                    action={'action': 5, 'ex': "Cannot execute node without executing previous nodes"},
                    response_to=response_to
                )
            
            # check if nodes corresponding to incoming edges have been executed. 
            if not self.executor.can_execute_node(node_id):
                return None, self._generate_response(
                    action={'action': 5, 'ex': "This node cannot be executed yet because one or more of its preceding nodes have not been executed. Please make sure all prerequisite nodes are completed before proceeding."},
                    response_to=response_to
                )
            
            try:
                self.executor.execute_node(node_id)
            except:
                return self.executor.get_plan().dag, self._generate_response(
                    action={'action': 5, 'ex': f"Error executing node {node_id}. Ensure edges are connected, i/o variables defined."},
                    response_to=response_to
                )
            plan = self.executor.get_plan()
            plan.set_node_exec_status(node_id, "EXECUTED")
            system_response = self._generate_response(
                {"action": 3, "execute": {"mode": "single", "node_id": node_id}}, response_to=response_to, plan=plan
            )

        self.planner.append_plan(plan)
        return plan.dag, system_response

    def reset(self) -> tuple[MultiDiGraph | None, SystemMessage | None, list[Message]]:
        """Resets controller state"""
        self.interaction_log.clear()
        self.chat_history.clear()
        self.planner = Planner(self.registry)
        self.executor = Executor(self.registry)
        return None, None, []

    def _classify_intent(self) -> Action:
        """Detect latest user intent based on chat history"""
        messages = [{"role": "system", "content": INTENT_SYSTEM_PROMPT}] + [
            {"role": message["role"], "content": message["content"]}
            for message in self.chat_history
            if message["role"] in ["system", "user", "assistant"]
        ]
        try:
            response = self.client.chat.completions.create(
                messages=messages, **self.config, response_format={"type": "json_schema", "json_schema": action_schema}
            )
            response_obj = json.loads(response.choices[0].message.content)
            next_action = {
                "action": response_obj["action"],
                "user_query": response_obj["user_query"],
                "plan_feedback": response_obj["plan_feedback"],
                "execute": response_obj["execute"]
            }
            print(f"[{current_time()}] -- User Intention:", next_action)
        except Exception as e:
            next_action = {"action": 0}
            print(f"[{current_time()}] -- Error in intent detection:", e, traceback.format_exc())
        return next_action

    def _generate_response(self, action: Action, response_to: int , plan: str = "") -> SystemMessage:
        """
        Generates a system response based on the action and plan.

        Args:
            action (Action): The detected action.
            response_to (int): The message ID being responded to.
            plan (str): The current plan (optional).

        Returns:
            SystemMessage: The system's response message.
        """
        if action["action"] == 0:
            content = "Could you please clarify or provide more details?"
            system_response = {"role": "assistant", "content": content, "timestamp": current_time(), "response_to": response_to}
        else:
            if action["action"] == 1:
                # plan
                prompt = RESPONSE_MESSAGE_PLAN.format(query=action["user_query"], plan=plan)
            elif action["action"] == 2:
                # feedback
                prompt = RESPONSE_MESSAGE_PLAN.format(query=action["plan_feedback"], plan=plan)
            elif action["action"] == 3:
                # execute
                if action["execute"]["mode"] == "all":
                    query = "Execute all steps"
                elif action["execute"]["mode"] == "single":
                    query = f"Execute node {action['execute']['node_id']}"
                prompt = RESPONSE_MESSAGE_EXECUTE.format(query=query, plan=plan)
            elif action["action"] == 4:
                # interact
                prompt = RESPONSE_MESSAGE_INTERACT.format(
                    interaction=action['interaction']['type'], plan=plan
                )
            elif action["action"] == 5:
                # error message
                return {
                    "role": "assistant",
                    "content": f"An error has occured: {action['ex']}\nPlease try again",
                    "timestamp": current_time(),
                    "response_to": response_to
                }

            messages = [
                {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                {"role": "user","content": prompt},
            ]
            try:
                response = self.client.chat.completions.create(messages=messages, **self.config)
                system_response = {
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                    "timestamp": response.created,
                    "response_to": response_to
                }
            except Exception as e:
                print(f"[{current_time()}] -- Error in response generation:", e, traceback.format_exc())
                content = "The results are updated."
                system_response = {"role": "assistant", "content": content, "timestamp": current_time(), "response_to": response_to}
        return system_response