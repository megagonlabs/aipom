import networkx as nx

from plan import PlanDAG
from utils import openai_client

class Executor:
    """
    Executes a plan represented as a DAG
    
    Attributes:
        agent_registry (AgentRegistry): Registry containing all available agents
        plan_dag (networkx.DiGraph): The plan represented as a directed acyclic graph
        node_info (dict): Dictionary to store node-specific information
        model (object): The OpenAI client used for LLM interactions
        config (dict): Configuration parameters for model execution
    """
    def __init__(self, agent_registry):
        """Initializes the Executor with the agent registry."""
        self.agent_registry = agent_registry
        self.plan_dag = None 
        self.plan = None
        self.node_info = {}
        self.model = openai_client
        self.config = {"temperature": 0, "response_format": {"type": "json_object"}}
    
    def set_plan(self, plan):
        """Store the planDAG instance for execution."""
        self.plan = PlanDAG(plan.query).initialize_from_dag(plan.dag)
        self.plan_dag = self.plan.dag

    def get_plan(self):
        """Retrieve planDAG used for execution"""
        self.plan.set_plan_dag(self.plan_dag)
        return self.plan
    
    def execute_plan(self) -> dict:
        """Execute the entire planDAG and return final results."""
        # topological sort
        sorted_nodes = list(nx.topological_sort(self.plan_dag)) 
           
        for node in sorted_nodes:
            # execute single node
            self.execute_node(node)
            
        return self.plan_dag.nodes[sorted_nodes[-1]]['exec']

    def is_source_node(self, node_id):
        """Checks if the given node is a source node (has no predecessors)."""
        return len(list(self.plan_dag.predecessors(node_id))) == 0
    
    def can_execute_node(self, node_id):
        """
        Checks if the given node is executable.
        A node is executable if it is a source node or all its predecessors have been executed.
        """
        predecessors = list(self.plan_dag.predecessors(node_id)) 

        if not predecessors:
            return True
        valid_status = ["EXECUTED", "MODIFIED"]
        return all(self.plan_dag.nodes[pred]["exec_status"] in valid_status for pred in predecessors)

    def execute_node(self, node_id):
        """
        Executes a single node in the plan. Stores result within node.

        Args:
            node_id (int): id of the node to execute.

        Raises:
            ValueError: If no agent is found for the specified task.
        """
        task = self.plan_dag.nodes[node_id]['task'] 
        name = self.plan_dag.nodes[node_id]['name']
        params = self.plan_dag.nodes[node_id].get('params', {})
        original_exec = self.plan_dag.nodes[node_id].get('exec', {})

        agent = self.agent_registry.get_agent(name)
        if not agent:
            agent = self.agent_registry.get_agent("fallback")
            # raise ValueError(f"No agent found for task: {task}")

        input_vars = self.plan_dag.nodes[node_id]['input']
        output_vars = self.plan_dag.nodes[node_id]['output']
        input_vals = {}
        try:
            for src_id, _, d in self.plan_dag.in_edges(node_id, data=True):
                input_vals[d['dest_input']] = self.plan_dag.nodes[src_id]['exec'][d['src_output']]
            for pair in input_vars:
                pair[1] = input_vals.get(pair[0], pair[1])
        except Exception as ex:
            raise Exception(f"Error executing node {node_id}: Ensure edges are connected, i/o variables defined.    ")
        
        try:
            self.plan_dag.nodes[node_id]['exec'] = agent.execute(task, input_vars, output_vars, params)
        except Exception as ex:
            raise Exception(f"Error executing node {node_id}: Ensure edges are connected, i/o variables defined.")
        
        try:
            for _, dest_id, k, d in self.plan_dag.out_edges(node_id, data=True, keys=True):
                if original_exec:
                    if not original_exec[k[0]] == self.plan_dag.nodes[node_id]['exec'][k[0]]:
                        d['hasUpdatedValue'] = True
                        d['sameExecVal'] = False
                    else:
                        d['hasUpdatedValue'] = False
                        d['sameExecVal'] = True
                else:
                    d['hasUpdatedValue'] = False
        except Exception as ex:
            raise Exception(ex)
        
        try:
            for _, _, k, d in self.plan_dag.in_edges(node_id, data=True, keys=True):
                d['hasUpdatedValue'] = False
                
        except Exception as ex:
            raise Exception(ex)