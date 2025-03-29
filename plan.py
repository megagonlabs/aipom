import json
from copy import deepcopy

from networkx import MultiDiGraph

from custom_types import LLMPlan, UIPlan
from structural_validity import validate_dag
from utils import create_uuid, current_time


class PlanDAG:
    """"""

    def __init__(self, query: str = ""):
        """Initializes a PlanDAG instance."""
        self.dag = MultiDiGraph(id=create_uuid(), query=query, timestamp=current_time())
        self.query = query

    def initialize_from_dag(self, dag: MultiDiGraph) -> "PlanDAG":
        """Initializes the DAG from an existing MultiDiGraph."""
        self.dag = dag
        self.query = dag.graph.get("query", "")
        return self

    def initialize_from_LLMPlan(
        self, query: str, plan: LLMPlan, agent_names: list[str]
    ) -> "PlanDAG":
        """Initializes the DAG from an LLM-generated plan."""
        self.dag = PlanConverter.dag_from_LLMPlan(query, plan, agent_names)
        self.query = query
        return self

    def initialize_from_UIPlan(self, plan: UIPlan) -> "PlanDAG":
        """Initializes the DAG from a UI plan."""
        self.dag = PlanConverter.dag_from_UIPlan(plan)
        self.query = plan["query"]
        return self

    def get_plan_dag(self):
        """Retrieve planDAG"""
        return self.dag

    def set_plan_dag(self, dag):
        """Set planDAG"""
        self.dag = dag

    def get_nodes(self, data=True):
        """Retrieve nodes and corresponding data"""
        return self.dag.nodes(data=True)

    def get_edges(self, data=True):
        """Retrieve edges and corresponding data, keys"""
        return self.dag.edges(data=True, keys=True)

    def copy(self) -> MultiDiGraph:
        """Creates a deep copy of the current DAG."""
        dag_copy = MultiDiGraph(
            id=self.dag.graph["id"],
            query=self.dag.graph["query"],
            timestamp=self.dag.graph["timestamp"],
        )
        dag_copy.add_nodes_from([deepcopy(n) for n in self.dag.nodes(data=True)])
        dag_copy.add_edges_from(self.dag.edges(data=True, keys=True))
        return dag_copy

    def initialize_plan_status(self):
        """Initializes the plan status of all nodes and edges"""
        for node_id in self.dag.nodes():
            self.dag.nodes[node_id]["plan_status"] = "UNMODIFIED"

        for src, dest, key in self.dag.edges(keys=True):
            self.dag.edges[src, dest, key]["plan_status"] = "UNMODIFIED"

    def intitialize_exec_status(self):
        """Initializes the execution status of all nodes"""
        for node_id in self.dag.nodes:
            self.dag.nodes[node_id]["exec_status"] = "NONE"

    def set_plan_status(self, val):
        """Set plan status for nodes and edges"""
        for node_id in self.dag.nodes():
            self.set_node_plan_status(node_id, val)
        for src, dest, key in self.dag.edges:
            self.set_edge_plan_status(src, dest, val, key)

    def set_node_plan_status(self, node_id, val):
        """Set plan status for given node"""
        self.dag.nodes[node_id]["plan_status"] = val

    def set_edge_plan_status(self, src, dest, val, key=None):
        """Set plan status for given edge"""
        edges = list(self.dag.get_edge_data(src, dest).items())
        if key:
            self.dag.edges[src, dest, key]["plan_status"] = val
        else:
            for s, t, k in self.dag.edges:
                if s == src and t == dest:
                    self.dag.edges[s, t, k]["plan_status"] = val

    def set_exec_status(self, val):
        """Set execution status for all nodes"""
        for node_id in self.dag.nodes():
            self.set_node_exec_status(node_id, val)

    def set_node_exec_status(self, node_id, val):
        """Set execution status for given node"""
        self.dag.nodes[node_id]["exec_status"] = val

    def validate_plan(self):  # TODO: update func in accordance with new o->i format
        """Validates a given plan for correctness."""
        if not validate_dag(self.dag.edges()):
            print("Error: Plan is an invalid DAG")

        sink = 0
        for id, node in self.dag.nodes(data=True):
            input = node.get("input", {})
            output = node.get("output", {})
            if not input:
                input = {}
            if not output:
                output = {}
            input_edges = self.dag.in_edges(id, data=True)
            output_edges = self.dag.out_edges(id, data=True)
            if len(input) != len(input_edges):
                print(
                    f"Error: Node {id} has mismtach of input edges and required inputs"
                )
            if len(output) != len(output_edges):
                sink += 1
        if sink != 1:
            print(f"Error: Node {id} has mismtach of output edges and required outputs")

    def add_node(self, node_id, node_data):
        """Adds a new node to the DAG."""
        if node_id in self.dag:
            raise ValueError(f"Node '{node_id}' already exists.")
        self.dag.add_node(node_id, **node_data)

    def remove_node(self, node_id):
        """Removes a node from the DAG."""
        if node_id not in self.dag:
            raise KeyError(f"Node '{node_id}' does not exist.")
        self.dag.remove_node(node_id)

    def add_edge(self, src, dest, edge_data):
        """Adds an edge to the DAG."""
        if src not in self.dag:
            raise KeyError(f"Source node '{src}' does not exist.")
        if dest not in self.dag:
            raise KeyError(f"Destination node '{dest}' does not exist.")
        key = (edge_data["src_output"], edge_data["dest_input"])
        self.dag.add_edge(src, dest, key, **edge_data)

    def remove_edge(self, src, dest, edge_data):
        """Removes an edge from the DAG."""
        key = (edge_data["src_output"], edge_data["dest_input"])
        self.dag.remove_edge(src, dest, key)

    def update_node(self, node_id, node_data):
        """Updates the data of an existing node."""
        if node_id not in self.dag:
            raise KeyError(f"Node '{node_id}' does not exist.")
        
        model = node_data['params'].get('model', None)
        if model and model not in ["gpt-4o", "gpt-4o-mini"]:
            node_data['params']['model'] = "gpt-4o"
        self.dag.nodes[node_id].update(node_data)

    def update_node_edge(self, node_id, node_data, edges):
        """Update node info and corresponding edges"""
        if node_id not in self.dag:
            raise KeyError(f"Node '{node_id}' does not exist.")
        self.dag.nodes[node_id].update(node_data)

        all_edges = list(self.dag.in_edges(node_id, keys=True)) + list(
            self.dag.out_edges(node_id, keys=True)
        )
        self.dag.remove_edges_from(all_edges)

        new_edges = []
        for edge in edges:
            src = int(edge["source"])
            dest = int(edge["target"])
            key = (edge["data"]["src_output"], edge["data"]["dest_input"])
            new_edges.append((src, dest, key, edge["data"]))
        self.dag.add_edges_from(new_edges)

    def update_exec(self, node_id, node_exec, node_attr, node_attr_value):
        """Updates the execution result of an existing node"""
        if node_id not in self.dag:
            raise KeyError(f"Node '{node_id}' does not exist.")
        node_data = self.dag.nodes[node_id]
        
        try:
            for _, _, k, d in self.dag.out_edges(node_id, data=True, keys=True):
                if k[0] == node_attr:
                    if not node_data['exec'][k[0]]==node_attr_value:
                        d['hasUpdatedValue'] = True
                        d['sameExecVal'] = False
                    else:
                        d['sameExecVal'] = True
                
        except Exception as ex:
            raise Exception(ex)
        node_data["exec"] = node_exec
        self.dag.nodes[node_id].update(node_data)

        # for _, dest_id, key, edge_data in self.dag.out_edges(
        #     node_id, data=True, keys=True
        # ):
        #     if self.dag.nodes[dest_id]["exec_status"] == "NONE":
        #         continue
        #     src_output, dest_input = key
        #     if src_output in node_exec:
        #         dest_node = self.dag.nodes[dest_id]
        #         input = dest_node["input"]
        #         for inp in input:
        #             if inp[0] == dest_input:
        #                 inp[1] = node_exec[src_output]
        #         dest_node["input"] = input
        #         self.dag.nodes[dest_id].update(dest_node)

    def initialize_params(self, agent_registry):
        """Initializes parameters for each node to default config"""
        for node_id in self.dag.nodes():
            name = self.dag.nodes[node_id]["name"]
            default_config = agent_registry.get_agent_default_config(name)
            self.dag.nodes[node_id]["params"] = default_config

    def get_node_attr(self, node_id, attr_name):
        """Get an attribute of a node."""
        return self.dag.nodes[node_id].get(attr_name)

    def set_node_attr(self, node_id, attr_name, value):
        """Set an attribute for a node."""
        self.dag.nodes[node_id][attr_name] = value

    def get_edge_attr(self, src, dest, key, attr_name):
        """Get an edge attribute."""
        return self.dag.get_edge_data(src, dest, key).get(attr_name)

    def set_edge_attr(self, src, dest, key, attr_name, value):
        """Set an edge attribute."""
        self.dag[src][dest][key][attr_name] = value

    def __str__(self):
        return f"query: {self.query}\nplan: {json.dumps(self.dag.graph, indent=2)}\nnodes:{json.dumps(dict(self.dag.nodes(data=True)), indent=2)}\nedges:{self.dag.edges(data=True, keys=True)}"


class PlanConverter:
    @classmethod
    def dag_from_LLMPlan(
        cls, query: str, plan: LLMPlan, agent_names: list[str]
    ) -> MultiDiGraph:
        """Converts an LLM-generated plan into a MultiDiGraph DAG."""
        dag = MultiDiGraph(
            id=plan["id"] if "id" in plan else create_uuid(),
            query=query,
            timestamp=plan["timestamp"] if "timestamp" in plan else current_time(),
        )
        nodes_with_valid_agents = [
            n if n["name"] in agent_names else {**n, "name": "fallback"}
            for n in plan["nodes"]
        ]
        dag.add_nodes_from([(n["id"], n) for n in nodes_with_valid_agents])
        dag.add_edges_from(
            [
                (e["src_node"], e["dest_node"], (e["src_output"], e["dest_input"]), e)
                for e in plan["edges"]
            ]
        )
        return dag

    @classmethod
    def dag_to_LLMPlan(cls, dag: MultiDiGraph) -> LLMPlan:
        """Convert dag back to LLM plan format"""
        nodes = []
        for node_id, node_data in dag.nodes(data=True):
            node = {
                "id": node_id,
                "name": node_data.get("name", ""),
                "task": node_data.get("task", ""),
                "input": list(node_data.get("input", [])),
                "output": list(node_data.get("output", [])),
            }
            nodes.append(node)
        edges = []
        for src, dest, edge_data in dag.edges(data=True):
            edge = {
                "src_node": src,
                "dest_node": dest,
                "src_output": edge_data.get("src_output", ""),
                "dest_input": edge_data.get("dest_input", ""),
            }
            edges.append(edge)
        return {"nodes": nodes, "edges": edges}

    @classmethod
    def dag_from_UIPlan(cls, plan: UIPlan, agent_names: list[str]) -> MultiDiGraph:
        """Converts a UIPlan into a MultiDiGraph DAG."""
        dag = MultiDiGraph(
            id=plan["id"], query=plan["query"], timestamp=plan["timestamp"]
        )
        dag.add_nodes_from(
            [
                (int(n["id"]), n["data"])
                for n in nodes_with_valid_agents
                if n["type"] == "_task"
            ]
        )
        dag.add_edges_from(
            [
                (
                    int(e["source"]),
                    int(e["target"]),
                    (e["data"]["src_output"], e["data"]["dest_input"]),
                    e["data"],
                )
                for e in plan["edges"]
            ]
        )
        return dag

    @classmethod
    def dag_to_UIPlan(cls, dag: MultiDiGraph) -> UIPlan:
        """Converts a MultiDiGraph DAG into a UIPlan format."""
        # task nodes and edges
        nodes = [
            {
                "id": str(n["id"]),
                "type": "_task",
                "dragHandle": ".bp5-section-header",
                "data": {
                    **n,
                    # "id": str(n["id"]),
                },
            }
            for n_id, n in dag.nodes(data=True)
        ]
        edges = [
            {
                "id": f"e_{s}-{t}_{k}",
                "source": str(s),
                "sourceHandle": e["src_output"],
                "target": str(t),
                "targetHandle": e["dest_input"],
                "data": {
                    **e,
                },
            }
            for s, t, k, e in dag.edges(data=True, keys=True)
        ]

        plan = {
            "id": dag.graph["id"],
            "query": dag.graph["query"],
            "timestamp": dag.graph["timestamp"],
            "nodes": nodes,
            "edges": edges,
        }
        return plan
